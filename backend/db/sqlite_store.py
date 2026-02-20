"""Lightweight SQLite wrapper that mimics the Supabase Python client API.

This allows the entire backend to run locally without Supabase for
development and demo purposes. All router code works unchanged.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "local.db"

_local = threading.local()


def _get_conn() -> sqlite3.Connection:
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


@dataclass
class _Result:
    data: list[dict] | None = None
    count: int | None = None


@dataclass
class _NotFilter:
    _qb: _QueryBuilder

    def is_(self, column: str, value: str) -> _QueryBuilder:
        self._qb._wheres.append(f'"{column}" IS NOT NULL')
        return self._qb


@dataclass
class _QueryBuilder:
    _table: str
    _columns: str = "*"
    _wheres: list[str] = field(default_factory=list)
    _params: list[Any] = field(default_factory=list)
    _order_col: str | None = None
    _order_desc: bool = False
    _limit_val: int | None = None
    _offset_val: int | None = None
    _range_start: int | None = None
    _range_end: int | None = None
    _is_single: bool = False
    _count_mode: str | None = None
    _insert_data: dict | list | None = None
    _update_data: dict | None = None
    _upsert_data: dict | None = None
    _delete: bool = False

    @property
    def not_(self) -> _NotFilter:
        return _NotFilter(self)

    def select(self, columns: str = "*", count: str | None = None) -> _QueryBuilder:
        self._columns = columns
        self._count_mode = count
        return self

    def eq(self, column: str, value: Any) -> _QueryBuilder:
        self._wheres.append(f'"{column}" = ?')
        self._params.append(value)
        return self

    def neq(self, column: str, value: Any) -> _QueryBuilder:
        self._wheres.append(f'"{column}" != ?')
        self._params.append(value)
        return self

    def gte(self, column: str, value: Any) -> _QueryBuilder:
        self._wheres.append(f'"{column}" >= ?')
        self._params.append(value)
        return self

    def lte(self, column: str, value: Any) -> _QueryBuilder:
        self._wheres.append(f'"{column}" <= ?')
        self._params.append(value)
        return self

    def lt(self, column: str, value: Any) -> _QueryBuilder:
        self._wheres.append(f'"{column}" < ?')
        self._params.append(value)
        return self

    def in_(self, column: str, values: list) -> _QueryBuilder:
        placeholders = ",".join("?" for _ in values)
        self._wheres.append(f'"{column}" IN ({placeholders})')
        self._params.extend(values)
        return self

    def is_(self, column: str, value: str) -> _QueryBuilder:
        if value == "null":
            self._wheres.append(f'"{column}" IS NULL')
        else:
            self._wheres.append(f'"{column}" IS NOT NULL')
        return self

    def order(self, column: str, desc: bool = False) -> _QueryBuilder:
        self._order_col = column
        self._order_desc = desc
        return self

    def limit(self, n: int) -> _QueryBuilder:
        self._limit_val = n
        return self

    def offset(self, n: int) -> _QueryBuilder:
        self._offset_val = n
        return self

    def range(self, start: int, end: int) -> _QueryBuilder:
        self._range_start = start
        self._range_end = end
        return self

    def single(self) -> _QueryBuilder:
        self._is_single = True
        self._limit_val = 1
        return self

    def insert(self, data: dict | list) -> _QueryBuilder:
        self._insert_data = data
        return self

    def update(self, data: dict) -> _QueryBuilder:
        self._update_data = data
        return self

    def upsert(self, data: dict) -> _QueryBuilder:
        self._upsert_data = data
        return self

    def delete(self) -> _QueryBuilder:
        self._delete = True
        return self

    def execute(self) -> _Result:
        conn = _get_conn()

        if self._insert_data is not None:
            return self._do_insert(conn)
        if self._update_data is not None:
            return self._do_update(conn)
        if self._upsert_data is not None:
            return self._do_upsert(conn)
        if self._delete:
            return self._do_delete(conn)
        return self._do_select(conn)

    def _do_select(self, conn: sqlite3.Connection) -> _Result:
        sql = f'SELECT * FROM "{self._table}"'
        where_clause = " AND ".join(self._wheres) if self._wheres else ""
        if where_clause:
            sql += f" WHERE {where_clause}"
        if self._order_col:
            direction = "DESC" if self._order_desc else "ASC"
            sql += f' ORDER BY "{self._order_col}" {direction}'
        if self._range_start is not None and self._range_end is not None:
            sql += f" LIMIT {self._range_end - self._range_start + 1} OFFSET {self._range_start}"
        elif self._limit_val is not None:
            sql += f" LIMIT {self._limit_val}"
            if self._offset_val is not None:
                sql += f" OFFSET {self._offset_val}"

        cursor = conn.execute(sql, self._params)
        rows = [_row_to_dict(r) for r in cursor.fetchall()]

        count = None
        if self._count_mode == "exact":
            count_sql = f'SELECT COUNT(*) FROM "{self._table}"'
            if where_clause:
                count_sql += f" WHERE {where_clause}"
            count = conn.execute(count_sql, self._params).fetchone()[0]

        if self._is_single:
            return _Result(data=rows[0] if rows else None, count=count)
        return _Result(data=rows, count=count)

    def _do_insert(self, conn: sqlite3.Connection) -> _Result:
        items = self._insert_data if isinstance(self._insert_data, list) else [self._insert_data]
        results = []
        for item in items:
            item = _serialize_json_fields(item)
            cols = list(item.keys())
            vals = list(item.values())
            placeholders = ",".join("?" for _ in cols)
            col_names = ",".join(f'"{c}"' for c in cols)
            sql = f'INSERT INTO "{self._table}" ({col_names}) VALUES ({placeholders})'
            cursor = conn.execute(sql, vals)
            conn.commit()
            item["id"] = cursor.lastrowid
            results.append(item)
        return _Result(data=results)

    def _do_update(self, conn: sqlite3.Connection) -> _Result:
        data = _serialize_json_fields(self._update_data)
        set_parts = [f'"{k}" = ?' for k in data.keys()]
        vals = list(data.values())
        sql = f'UPDATE "{self._table}" SET {",".join(set_parts)}'
        if self._wheres:
            sql += f' WHERE {" AND ".join(self._wheres)}'
            vals.extend(self._params)
        conn.execute(sql, vals)
        conn.commit()
        return _Result(data=[data])

    def _do_upsert(self, conn: sqlite3.Connection) -> _Result:
        data = _serialize_json_fields(self._upsert_data)
        cols = list(data.keys())
        vals = list(data.values())
        placeholders = ",".join("?" for _ in cols)
        col_names = ",".join(f'"{c}"' for c in cols)
        update_parts = ",".join(f'"{c}" = excluded."{c}"' for c in cols if c != "id")
        # Determine conflict column — use 'key' for system_config, 'id' for others
        conflict_col = "key" if self._table == "system_config" else "id"
        sql = (
            f'INSERT INTO "{self._table}" ({col_names}) VALUES ({placeholders})'
            f' ON CONFLICT("{conflict_col}") DO UPDATE SET {update_parts}'
        )
        conn.execute(sql, vals)
        conn.commit()
        return _Result(data=[data])

    def _do_delete(self, conn: sqlite3.Connection) -> _Result:
        sql = f'DELETE FROM "{self._table}"'
        if self._wheres:
            sql += f' WHERE {" AND ".join(self._wheres)}'
        conn.execute(sql, self._params)
        conn.commit()
        return _Result(data=[])


class SQLiteClient:
    """Drop-in replacement for supabase.Client using local SQLite."""

    def table(self, name: str) -> _QueryBuilder:
        return _QueryBuilder(_table=name)


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, str) and v.startswith(("{", "[")):
            try:
                d[k] = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                pass
    return d


def _serialize_json_fields(data: dict) -> dict:
    out = {}
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v)
        else:
            out[k] = v
    return out


def init_sqlite_db() -> None:
    """Create all tables and seed demo data if the DB doesn't exist."""
    conn = _get_conn()

    # Create tables
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS platforms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            auth_method TEXT DEFAULT 'oauth',
            status TEXT DEFAULT 'disconnected',
            credentials_encrypted TEXT,
            session_health TEXT DEFAULT 'unknown',
            workers_status TEXT DEFAULT '{}',
            connected_at TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS discovered_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            video_url TEXT,
            creator TEXT,
            description TEXT,
            transcript TEXT,
            hashtags TEXT DEFAULT '[]',
            likes INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            classification TEXT,
            discovered_at TEXT DEFAULT (datetime('now')),
            status TEXT DEFAULT 'new',
            engaged INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS generated_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER REFERENCES discovered_videos(id),
            text TEXT NOT NULL,
            approach TEXT DEFAULT 'witty',
            char_count INTEGER DEFAULT 0,
            generated_at TEXT DEFAULT (datetime('now')),
            selected INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS risk_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id INTEGER REFERENCES generated_comments(id),
            total_score REAL DEFAULT 0,
            blocklist_score REAL DEFAULT 0,
            context_score REAL DEFAULT 0,
            ai_judge_score REAL DEFAULT 0,
            reasoning TEXT,
            routing_decision TEXT DEFAULT 'review',
            scored_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS engagements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            video_id INTEGER REFERENCES discovered_videos(id),
            comment_id INTEGER REFERENCES generated_comments(id),
            comment_text TEXT,
            risk_score REAL DEFAULT 0,
            approval_path TEXT DEFAULT 'auto',
            approved_by TEXT,
            posted_at TEXT DEFAULT (datetime('now')),
            screenshot_url TEXT,
            status TEXT DEFAULT 'posted'
        );
        CREATE TABLE IF NOT EXISTS engagement_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            engagement_id INTEGER REFERENCES engagements(id),
            checked_at TEXT DEFAULT (datetime('now')),
            likes INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            reply_texts TEXT DEFAULT '[]',
            reply_sentiment REAL,
            impressions INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS saved_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            engagement_id INTEGER REFERENCES engagements(id),
            saved_by TEXT,
            tags TEXT DEFAULT '[]',
            notes TEXT,
            saved_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS review_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id INTEGER,
            video_id INTEGER,
            proposed_text TEXT,
            risk_score REAL DEFAULT 0,
            risk_reasoning TEXT,
            classification TEXT,
            queued_at TEXT DEFAULT (datetime('now')),
            reviewed_by TEXT,
            decision TEXT,
            decision_reason TEXT,
            decided_at TEXT
        );
        CREATE TABLE IF NOT EXISTS voice_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voice_guide_md TEXT,
            positive_examples TEXT DEFAULT '[]',
            negative_examples TEXT DEFAULT '[]',
            platform_adapters TEXT DEFAULT '{}',
            updated_at TEXT DEFAULT (datetime('now')),
            updated_by TEXT
        );
        CREATE TABLE IF NOT EXISTS risk_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auto_approve_max INTEGER DEFAULT 30,
            review_max INTEGER DEFAULT 65,
            blocklist TEXT DEFAULT '{}',
            override_rules TEXT DEFAULT '[]',
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT DEFAULT '{}',
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT,
            entity_type TEXT,
            entity_id TEXT,
            details TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS neoclaw_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            platform TEXT,
            payload TEXT DEFAULT '{}',
            priority INTEGER DEFAULT 5,
            status TEXT DEFAULT 'pending',
            assigned_agent TEXT,
            result TEXT,
            error TEXT,
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            created_at TEXT DEFAULT (datetime('now')),
            started_at TEXT,
            completed_at TEXT,
            expires_at TEXT,
            created_by TEXT DEFAULT 'system',
            metadata TEXT DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS neoclaw_heartbeats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            active_sessions TEXT DEFAULT '[]',
            current_task_id INTEGER REFERENCES neoclaw_tasks(id),
            system_stats TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)

    # Seed demo data if tables are empty
    count = conn.execute("SELECT COUNT(*) FROM platforms").fetchone()[0]
    if count == 0:
        _seed_demo_data(conn)


def _seed_demo_data(conn: sqlite3.Connection) -> None:
    """Insert realistic demo data for the hackathon dashboard."""
    now = datetime.now(timezone.utc).isoformat()

    # Platforms
    conn.executemany(
        'INSERT INTO platforms (name, status, auth_method, session_health, workers_status, connected_at) VALUES (?, ?, ?, ?, ?, ?)',
        [
            ("tiktok", "connected", "browser_session", "healthy", json.dumps({"discovery": True, "execution": True, "analytics": True}), now),
            ("instagram", "connected", "oauth", "healthy", json.dumps({"discovery": True, "execution": True, "analytics": True}), now),
            ("x", "connected", "oauth_pkce", "healthy", json.dumps({"discovery": True, "execution": True, "analytics": True}), now),
        ],
    )

    # System config
    conn.executemany(
        'INSERT INTO system_config (key, value) VALUES (?, ?)',
        [
            ("kill_switch", json.dumps({"active": False})),
            ("rate_limits", json.dumps({"tiktok": 12, "instagram": 10, "x": 15})),
            ("supervised_mode", json.dumps({"enabled": False})),
            ("posting_schedule", json.dumps({"start_hour": 8, "end_hour": 23, "timezone": "America/New_York"})),
        ],
    )

    # Risk config
    conn.execute(
        'INSERT INTO risk_config (auto_approve_max, review_max, blocklist, override_rules) VALUES (?, ?, ?, ?)',
        (30, 65, json.dumps({"financial_claims": ["guaranteed", "free money"], "political": ["vote", "election"]}), json.dumps([])),
    )

    # Discovered videos with demo data
    import random
    platforms = ["tiktok", "tiktok", "tiktok", "instagram", "instagram", "x", "x", "x"]
    creators = ["@savvysaver", "@budgettips", "@financefun", "@moneytalks", "@creditwise", "@taxhacks", "@sidehustle", "@investbro"]
    descriptions = [
        "How I saved $10k in 6 months with this budgeting hack 💰",
        "Stop making these 3 credit card mistakes right now",
        "POV: you finally check your credit score after avoiding it",
        "The 50/30/20 rule actually works if you do it right",
        "Why nobody talks about high-yield savings accounts",
        "Tax season tips that saved me $2000 last year",
        "Side hustles that actually make real money in 2026",
        "My investment portfolio at 25 vs 30 - the difference is wild",
    ]
    hashtags_list = [
        ["#money", "#budgeting", "#savingmoney"],
        ["#creditcard", "#finance", "#personalfinance"],
        ["#creditscore", "#financetok", "#moneytok"],
        ["#budgeting", "#5030/20rule", "#moneytips"],
        ["#savings", "#hysa", "#financetips"],
        ["#taxes", "#taxtips", "#money"],
        ["#sidehustle", "#makemoney", "#entrepreneur"],
        ["#investing", "#portfolio", "#stocks"],
    ]
    classifications = ["finance-educational", "finance-educational", "cultural-trending", "finance-educational", "finance-educational", "finance-educational", "cultural-trending", "finance-educational"]

    for i in range(8):
        hours_ago = random.randint(1, 48)
        discovered = datetime(2026, 2, 19, 12, 0, 0, tzinfo=timezone.utc)
        conn.execute(
            'INSERT INTO discovered_videos (platform, video_url, creator, description, hashtags, likes, comments_count, shares, classification, discovered_at, status, engaged) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                platforms[i],
                f"https://{platforms[i]}.com/video/{1000+i}",
                creators[i],
                descriptions[i],
                json.dumps(hashtags_list[i]),
                random.randint(500, 50000),
                random.randint(50, 5000),
                random.randint(10, 2000),
                classifications[i],
                discovered.isoformat(),
                "engaged",
                1,
            ),
        )

    # Generated comments
    comments_data = [
        (1, "budgeting hack? tell me more, my wallet is listening 👀", "witty", 52),
        (2, "this is genuinely great advice. the minimum payment trap is real", "helpful", 63),
        (3, "me @ my credit score: it's been 84 years 😭 but fr it's worth checking", "witty", 68),
        (4, "the 50/30/20 rule changed my whole approach to money tbh", "supportive", 55),
        (5, "HYSA gang 🙌 seriously underrated move", "witty", 34),
        (6, "saving this for later. tax season stress is real", "supportive", 45),
        (7, "the consistency is the part nobody talks about 💯", "supportive", 47),
        (8, "compound interest really is the 8th wonder of the world ngl", "helpful", 55),
    ]
    for vid_id, text, approach, char_count in comments_data:
        conn.execute(
            'INSERT INTO generated_comments (video_id, text, approach, char_count, selected) VALUES (?, ?, ?, ?, 1)',
            (vid_id, text, approach, char_count),
        )

    # Engagements (posted comments)
    for i in range(8):
        hours_ago = random.randint(1, 36)
        posted = datetime(2026, 2, 19, 10 + (i % 12), 30, 0, tzinfo=timezone.utc)
        risk = random.randint(5, 28)
        conn.execute(
            'INSERT INTO engagements (platform, video_id, comment_id, comment_text, risk_score, approval_path, posted_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (
                platforms[i],
                i + 1,
                i + 1,
                comments_data[i][1],
                risk,
                "auto" if risk < 20 else "human",
                posted.isoformat(),
                "posted",
            ),
        )

    # Engagement metrics
    for i in range(8):
        conn.execute(
            'INSERT INTO engagement_metrics (engagement_id, likes, replies, impressions) VALUES (?, ?, ?, ?)',
            (i + 1, random.randint(10, 500), random.randint(0, 30), random.randint(100, 10000)),
        )

    # Review queue items (2 pending)
    conn.execute(
        'INSERT INTO review_queue (comment_id, video_id, proposed_text, risk_score, risk_reasoning, classification, queued_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (None, 3, "honestly same. but checking it is the first step to fixing it 🙏", 42, "Moderate risk: indirect financial advice", "cultural-trending", now),
    )
    conn.execute(
        'INSERT INTO review_queue (comment_id, video_id, proposed_text, risk_score, risk_reasoning, classification, queued_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (None, 7, "this! most people quit before the compound effect kicks in", 35, "Low-moderate risk: motivational tone acceptable", "finance-educational", now),
    )

    conn.commit()
