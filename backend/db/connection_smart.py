"""
PostgreSQL-aware database connection with automatic fallback.
Priority: PostgreSQL (persistent) > SQLite (dev only)
"""

from __future__ import annotations
import os
import logging

logger = logging.getLogger(__name__)

_client = None
_admin = None
_initialized = False
_using_postgres = False


def init_clients() -> None:
    global _client, _admin, _initialized, _using_postgres
    _initialized = True
    
    # Check for PostgreSQL first (Railway, Supabase, etc.)
    database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("SUPABASE_URL")
    
    if database_url:
        # Use PostgreSQL (persistent!)
        logger.info(f"🐘 Using PostgreSQL database (persistent)")
        try:
            from db.postgres_store import PostgresClient, init_postgres_db
            init_postgres_db(database_url)
            _client = PostgresClient(database_url)
            _admin = PostgresClient(database_url)
            _using_postgres = True
            logger.info("✅ PostgreSQL connected successfully")
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            logger.info("⚠️  Falling back to SQLite")
            _init_sqlite()
    else:
        # Fall back to SQLite (dev/local only)
        logger.warning("⚠️  No DATABASE_URL found - using SQLite (ephemeral!)")
        logger.warning("💡 Add Railway PostgreSQL for persistent data")
        _init_sqlite()


def _init_sqlite():
    """Initialize SQLite (dev/fallback only)."""
    global _client, _admin, _using_postgres
    from db.sqlite_store import SQLiteClient, init_sqlite_db
    init_sqlite_db()
    _client = SQLiteClient()
    _admin = SQLiteClient()
    _using_postgres = False
    logger.info("📁 Using SQLite (development mode)")


def get_supabase_client():
    if not _initialized:
        init_clients()
    return _client


def get_supabase_admin():
    if not _initialized:
        init_clients()
    return _admin


def is_postgres_mode() -> bool:
    return _using_postgres


def get_db_info() -> dict:
    """Return database info for debugging."""
    return {
        "initialized": _initialized,
        "using_postgres": _using_postgres,
        "database_type": "PostgreSQL" if _using_postgres else "SQLite",
        "persistent": _using_postgres,
        "warning": None if _using_postgres else "SQLite is ephemeral - add PostgreSQL for persistence"
    }
