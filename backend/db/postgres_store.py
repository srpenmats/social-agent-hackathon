"""
PostgreSQL adapter that mimics the Supabase/SQLite interface.
Provides persistent storage for Railway deployment.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
import json
from datetime import datetime


class PostgresClient:
    """PostgreSQL client with Supabase-like API."""
    
    def __init__(self, database_url: str):
        # Parse DATABASE_URL
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
        """Test database connection."""
        try:
            conn = psycopg2.connect(**self.conn_params)
            conn.close()
        except Exception as e:
            raise Exception(f"PostgreSQL connection failed: {e}")
    
    def _get_conn(self):
        """Get database connection."""
        return psycopg2.connect(**self.conn_params)
    
    def table(self, table_name: str):
        """Return query builder for table."""
        return QueryBuilder(self, table_name)


class QueryBuilder:
    """Query builder with Supabase-like API."""
    
    def __init__(self, client: PostgresClient, table: str):
        self.client = client
        self.table = table
        self._select_cols = "*"
        self._wheres = []
        self._params = []
        self._order_col = None
        self._order_desc = False
        self._limit_val = None
        self._insert_data = None
        self._update_data = None
    
    def select(self, columns: str = "*"):
        self._select_cols = columns
        return self
    
    def eq(self, column: str, value):
        self._wheres.append(f"{column} = %s")
        self._params.append(value)
        return self
    
    def neq(self, column: str, value):
        self._wheres.append(f"{column} != %s")
        self._params.append(value)
        return self
    
    def is_(self, column: str, value: str):
        if value == "null":
            self._wheres.append(f"{column} IS NULL")
        else:
            self._wheres.append(f"{column} IS NOT NULL")
        return self
    
    def order(self, column: str, desc: bool = False):
        self._order_col = column
        self._order_desc = desc
        return self
    
    def limit(self, n: int):
        self._limit_val = n
        return self
    
    def insert(self, data: dict):
        self._insert_data = data
        return self
    
    def update(self, data: dict):
        self._update_data = data
        return self
    
    def execute(self):
        """Execute the query."""
        conn = self.client._get_conn()
        cursor = conn.cursor()
        
        try:
            if self._insert_data:
                return self._do_insert(cursor, conn)
            elif self._update_data:
                return self._do_update(cursor, conn)
            else:
                return self._do_select(cursor)
        finally:
            cursor.close()
            conn.close()
    
    def _do_select(self, cursor):
        """Execute SELECT query."""
        sql = f"SELECT {self._select_cols} FROM {self.table}"
        if self._wheres:
            sql += " WHERE " + " AND ".join(self._wheres)
        if self._order_col:
            direction = "DESC" if self._order_desc else "ASC"
            sql += f" ORDER BY {self._order_col} {direction}"
        if self._limit_val:
            sql += f" LIMIT {self._limit_val}"
        
        cursor.execute(sql, self._params)
        rows = cursor.fetchall()
        
        return Result(data=[dict(row) for row in rows])
    
    def _do_insert(self, cursor, conn):
        """Execute INSERT query."""
        data = self._insert_data
        cols = list(data.keys())
        vals = list(data.values())
        
        placeholders = ", ".join(["%s"] * len(cols))
        col_names = ", ".join(cols)
        
        sql = f"INSERT INTO {self.table} ({col_names}) VALUES ({placeholders}) RETURNING *"
        cursor.execute(sql, vals)
        conn.commit()
        
        row = cursor.fetchone()
        return Result(data=[dict(row)] if row else [])
    
    def _do_update(self, cursor, conn):
        """Execute UPDATE query."""
        data = self._update_data
        set_parts = [f"{k} = %s" for k in data.keys()]
        vals = list(data.values())
        
        sql = f"UPDATE {self.table} SET {', '.join(set_parts)}"
        if self._wheres:
            sql += " WHERE " + " AND ".join(self._wheres)
            vals.extend(self._params)
        
        cursor.execute(sql, vals)
        conn.commit()
        
        return Result(data=[data])


class Result:
    """Query result."""
    def __init__(self, data=None, count=None):
        self.data = data
        self.count = count


def init_postgres_db(database_url: str):
    """Initialize PostgreSQL database with required tables."""
    client = PostgresClient(database_url)
    conn = client._get_conn()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discovered_videos (
            id SERIAL PRIMARY KEY,
            platform TEXT NOT NULL,
            video_url TEXT UNIQUE NOT NULL,
            creator TEXT,
            description TEXT,
            hashtags JSONB,
            likes INTEGER DEFAULT 0,
            status TEXT DEFAULT 'discovered',
            engaged INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS engagements (
            id SERIAL PRIMARY KEY,
            platform TEXT NOT NULL,
            video_id INTEGER REFERENCES discovered_videos(id),
            comment_text TEXT,
            risk_score INTEGER,
            approval_path TEXT,
            posted_at TIMESTAMP,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS engagement_metrics (
            id SERIAL PRIMARY KEY,
            engagement_id INTEGER REFERENCES engagements(id),
            likes INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS review_queue (
            id SERIAL PRIMARY KEY,
            video_id INTEGER REFERENCES discovered_videos(id),
            proposed_text TEXT,
            risk_score REAL,
            risk_reasoning TEXT,
            classification TEXT,
            decision TEXT,
            queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
