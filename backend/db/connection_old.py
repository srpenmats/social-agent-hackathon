from __future__ import annotations

import logging

from config import get_settings

logger = logging.getLogger(__name__)

_client = None
_admin = None
_initialized = False
_using_sqlite = True


def init_clients() -> None:
    global _client, _admin, _initialized, _using_sqlite
    _initialized = True
    
    # Use SQLite for now (simple and reliable)
    # PostgreSQL integration can be added later if needed
    from db.sqlite_store import SQLiteClient, init_sqlite_db
    init_sqlite_db()
    _client = SQLiteClient()
    _admin = SQLiteClient()
    _using_sqlite = True
    logger.info("Using SQLite database")


def get_supabase_client():
    if not _initialized:
        init_clients()
    return _client


def get_supabase_admin():
    if not _initialized:
        init_clients()
    return _admin


def is_sqlite_mode() -> bool:
    return _using_sqlite
