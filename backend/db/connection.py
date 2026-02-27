from __future__ import annotations

import logging

from config import get_settings

logger = logging.getLogger(__name__)

try:
    from supabase import Client, create_client
    _supabase_available = True
except ImportError:
    _supabase_available = False

_client = None
_admin = None
_initialized = False
_using_sqlite = False


def init_clients() -> None:
    global _client, _admin, _initialized, _using_sqlite
    _initialized = True
    settings = get_settings()

    # Try Supabase first
    if _supabase_available and settings.supabase_service_role_key:
        try:
            _client = create_client(settings.supabase_url, settings.supabase_anon_key)
            _admin = create_client(settings.supabase_url, settings.supabase_service_role_key)
            logger.info("Connected to Supabase")
            return
        except Exception as e:
            logger.warning(f"Supabase connection failed: {e}")

    # Fallback to local SQLite
    from backend.db.sqlite_store import SQLiteClient, init_sqlite_db
    init_sqlite_db()
    _client = SQLiteClient()
    _admin = SQLiteClient()
    _using_sqlite = True
    logger.info("Using local SQLite database (demo mode)")


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
