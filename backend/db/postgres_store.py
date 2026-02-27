"""
PostgreSQL adapter that mimics the Supabase/SQLite interface.
Provides persistent storage for Railway deployment.
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse


class PostgresClient:
    """PostgreSQL client with Supabase-like API."""

    def __init__(self, database_url: str):
        parsed = urlparse(database_url)
        self.conn_params = {
            'dbname': parsed.path[1:],
            'user': parsed.username,
            'password': parsed.password,
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'cursor_factory': RealDictCursor
        }
        self._test_connection()

    def _test_connection(self):
        try:
            conn = psycopg2.connect(**self.conn_params)
            conn.close()
        except Exception as e:
            raise Exception(f"PostgreSQL connection failed: {e}")

    def _get_conn(self):
        return psycopg2.connect(**self.conn_params)

    def table(self, table_name: str):
        return QueryBuilder(self, table_name)


class _NotFilter:
    def __init__(self, qb):
        self._qb = qb

    def is_(self, column: str, value: str):
        self._qb._wheres.append(f'"{column}" IS NOT NULL')
        return self._qb


class QueryBuilder:
    """Query builder with Supabase-like API — matches SQLite wrapper."""

    def __init__(self, client: PostgresClient, table: str):
        self.client = client
        self._table = table
        self._select_cols = "*"
        self._wheres = []
        self._params = []
        self._order_col = None
        self._order_desc = False
        self._limit_val = None
        self._offset_val = None
        self._range_start = None
        self._range_end = None
        self._is_single = False
        self._count_mode = None
        self._insert_data = None
        self._update_data = None
        self._upsert_data = None
        self._delete_flag = False

    @property
    def not_(self):
        return _NotFilter(self)

    def select(self, columns: str = "*", count: str | None = None):
        self._select_cols = columns
        self._count_mode = count
        return self

    def eq(self, column: str, value):
        self._wheres.append(f'"{column}" = %s')
        self._params.append(value)
        return self

    def neq(self, column: str, value):
        self._wheres.append(f'"{column}" != %s')
        self._params.append(value)
        return self

    def gte(self, column: str, value):
        self._wheres.append(f'"{column}" >= %s')
        self._params.append(value)
        return self

    def lte(self, column: str, value):
        self._wheres.append(f'"{column}" <= %s')
        self._params.append(value)
        return self

    def lt(self, column: str, value):
        self._wheres.append(f'"{column}" < %s')
        self._params.append(value)
        return self

    def in_(self, column: str, values: list):
        placeholders = ",".join("%s" for _ in values)
        self._wheres.append(f'"{column}" IN ({placeholders})')
        self._params.extend(values)
        return self

    def is_(self, column: str, value: str):
        if value == "null":
            self._wheres.append(f'"{column}" IS NULL')
        else:
            self._wheres.append(f'"{column}" IS NOT NULL')
        return self

    def order(self, column: str, desc: bool = False):
        self._order_col = column
        self._order_desc = desc
        return self

    def limit(self, n: int):
        self._limit_val = n
        return self

    def offset(self, n: int):
        self._offset_val = n
        return self

    def range(self, start: int, end: int):
        self._range_start = start
        self._range_end = end
        return self

    def single(self):
        self._is_single = True
        self._limit_val = 1
        return self

    def insert(self, data):
        self._insert_data = data
        return self

    def update(self, data: dict):
        self._update_data = data
        return self

    def upsert(self, data: dict):
        self._upsert_data = data
        return self

    def delete(self):
        self._delete_flag = True
        return self

    def execute(self):
        conn = self.client._get_conn()
        cursor = conn.cursor()

        try:
            if self._insert_data is not None:
                return self._do_insert(cursor, conn)
            elif self._update_data is not None:
                return self._do_update(cursor, conn)
            elif self._upsert_data is not None:
                return self._do_upsert(cursor, conn)
            elif self._delete_flag:
                return self._do_delete(cursor, conn)
            else:
                return self._do_select(cursor)
        finally:
            cursor.close()
            conn.close()

    def _do_select(self, cursor):
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

        cursor.execute(sql, self._params)
        rows = [dict(row) for row in cursor.fetchall()]

        count = None
        if self._count_mode == "exact":
            count_sql = f'SELECT COUNT(*) FROM "{self._table}"'
            if where_clause:
                count_sql += f" WHERE {where_clause}"
            cursor.execute(count_sql, self._params)
            count = cursor.fetchone()["count"]

        if self._is_single:
            return Result(data=rows[0] if rows else None, count=count)
        return Result(data=rows, count=count)

    def _do_insert(self, cursor, conn):
        items = self._insert_data if isinstance(self._insert_data, list) else [self._insert_data]
        results = []
        for item in items:
            item = _serialize_json_fields(item)
            cols = list(item.keys())
            vals = list(item.values())
            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(f'"{c}"' for c in cols)
            sql = f'INSERT INTO "{self._table}" ({col_names}) VALUES ({placeholders}) RETURNING *'
            cursor.execute(sql, vals)
            conn.commit()
            row = cursor.fetchone()
            if row:
                results.append(dict(row))
        return Result(data=results)

    def _do_update(self, cursor, conn):
        data = _serialize_json_fields(self._update_data)
        set_parts = [f'"{k}" = %s' for k in data.keys()]
        vals = list(data.values())
        sql = f'UPDATE "{self._table}" SET {", ".join(set_parts)}'
        if self._wheres:
            sql += f' WHERE {" AND ".join(self._wheres)}'
            vals.extend(self._params)
        sql += " RETURNING *"
        cursor.execute(sql, vals)
        conn.commit()
        rows = cursor.fetchall()
        return Result(data=[dict(r) for r in rows] if rows else [data])

    def _do_upsert(self, cursor, conn):
        data = _serialize_json_fields(self._upsert_data)
        cols = list(data.keys())
        vals = list(data.values())
        placeholders = ", ".join(["%s"] * len(cols))
        col_names = ", ".join(f'"{c}"' for c in cols)
        update_parts = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in cols if c != "id")
        conflict_col = "key" if self._table == "system_config" else "id"
        sql = (
            f'INSERT INTO "{self._table}" ({col_names}) VALUES ({placeholders})'
            f' ON CONFLICT ("{conflict_col}") DO UPDATE SET {update_parts}'
            f' RETURNING *'
        )
        cursor.execute(sql, vals)
        conn.commit()
        row = cursor.fetchone()
        return Result(data=[dict(row)] if row else [data])

    def _do_delete(self, cursor, conn):
        sql = f'DELETE FROM "{self._table}"'
        if self._wheres:
            sql += f' WHERE {" AND ".join(self._wheres)}'
        cursor.execute(sql, self._params)
        conn.commit()
        return Result(data=[])


class Result:
    """Query result."""
    def __init__(self, data=None, count=None):
        self.data = data
        self.count = count


def _serialize_json_fields(data: dict) -> dict:
    out = {}
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v)
        else:
            out[k] = v
    return out


def init_postgres_db(database_url: str):
    """Initialize PostgreSQL database with all required tables."""
    client = PostgresClient(database_url)
    conn = client._get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platforms (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            auth_method TEXT DEFAULT 'oauth',
            status TEXT DEFAULT 'disconnected',
            credentials_encrypted TEXT,
            session_health TEXT DEFAULT 'unknown',
            workers_status TEXT DEFAULT '{}',
            connected_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS discovered_videos (
            id SERIAL PRIMARY KEY,
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
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'new',
            engaged INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS generated_comments (
            id SERIAL PRIMARY KEY,
            video_id INTEGER REFERENCES discovered_videos(id),
            text TEXT NOT NULL,
            approach TEXT DEFAULT 'witty',
            char_count INTEGER DEFAULT 0,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            selected INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS risk_scores (
            id SERIAL PRIMARY KEY,
            comment_id INTEGER REFERENCES generated_comments(id),
            total_score REAL DEFAULT 0,
            blocklist_score REAL DEFAULT 0,
            context_score REAL DEFAULT 0,
            ai_judge_score REAL DEFAULT 0,
            reasoning TEXT,
            routing_decision TEXT DEFAULT 'review',
            scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS engagements (
            id SERIAL PRIMARY KEY,
            platform TEXT NOT NULL,
            video_id INTEGER REFERENCES discovered_videos(id),
            comment_id INTEGER,
            comment_text TEXT,
            risk_score REAL DEFAULT 0,
            approval_path TEXT DEFAULT 'auto',
            approved_by TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            screenshot_url TEXT,
            status TEXT DEFAULT 'posted'
        );

        CREATE TABLE IF NOT EXISTS engagement_metrics (
            id SERIAL PRIMARY KEY,
            engagement_id INTEGER REFERENCES engagements(id),
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            likes INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            reply_texts TEXT DEFAULT '[]',
            reply_sentiment REAL,
            impressions INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS saved_comments (
            id SERIAL PRIMARY KEY,
            engagement_id INTEGER REFERENCES engagements(id),
            saved_by TEXT,
            tags TEXT DEFAULT '[]',
            notes TEXT,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS review_queue (
            id SERIAL PRIMARY KEY,
            comment_id INTEGER,
            video_id INTEGER,
            proposed_text TEXT,
            risk_score REAL DEFAULT 0,
            risk_reasoning TEXT,
            classification TEXT,
            queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_by TEXT,
            decision TEXT,
            decision_reason TEXT,
            decided_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS voice_config (
            id SERIAL PRIMARY KEY,
            voice_guide_md TEXT,
            positive_examples TEXT DEFAULT '[]',
            negative_examples TEXT DEFAULT '[]',
            platform_adapters TEXT DEFAULT '{}',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by TEXT
        );

        CREATE TABLE IF NOT EXISTS risk_config (
            id SERIAL PRIMARY KEY,
            auto_approve_max INTEGER DEFAULT 30,
            review_max INTEGER DEFAULT 65,
            blocklist TEXT DEFAULT '{}',
            override_rules TEXT DEFAULT '[]',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS system_config (
            id SERIAL PRIMARY KEY,
            key TEXT UNIQUE NOT NULL,
            value TEXT DEFAULT '{}',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            action TEXT,
            entity_type TEXT,
            entity_id TEXT,
            details TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS neoclaw_tasks (
            id SERIAL PRIMARY KEY,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            expires_at TIMESTAMP,
            created_by TEXT DEFAULT 'system',
            metadata TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS neoclaw_heartbeats (
            id SERIAL PRIMARY KEY,
            agent_id TEXT NOT NULL,
            active_sessions TEXT DEFAULT '[]',
            current_task_id INTEGER,
            system_stats TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS comment_feedback (
            id SERIAL PRIMARY KEY,
            comment_text TEXT NOT NULL,
            original_post_text TEXT,
            original_post_author TEXT,
            platform TEXT DEFAULT 'x',
            decision TEXT NOT NULL,
            decision_reason TEXT,
            risk_score REAL DEFAULT 0,
            approach TEXT,
            persona TEXT,
            decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            decided_by TEXT DEFAULT 'reviewer'
        );

        CREATE TABLE IF NOT EXISTS review_posts (
            id SERIAL PRIMARY KEY,
            post_id TEXT UNIQUE NOT NULL,
            author TEXT,
            text TEXT,
            url TEXT,
            likes INTEGER DEFAULT 0,
            retweets INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            quotes INTEGER DEFAULT 0,
            bookmarks INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            relevance_score REAL DEFAULT 0,
            engagement_potential REAL DEFAULT 0,
            persona_recommendation TEXT,
            risk_level TEXT DEFAULT 'green',
            angle_summary TEXT,
            recommendation_score REAL DEFAULT 0,
            reasoning TEXT,
            status TEXT DEFAULT 'pending',
            draft_comment TEXT,
            final_comment TEXT,
            posted INTEGER DEFAULT 0,
            posted_at TIMESTAMP,
            posted_url TEXT,
            responded_at TIMESTAMP,
            response_text TEXT,
            response_url TEXT,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
