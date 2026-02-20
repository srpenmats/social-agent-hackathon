from __future__ import annotations

import logging

from backend.config import get_settings

logger = logging.getLogger(__name__)

try:
    from supabase import Client, create_client

    _supabase_available = True
except ImportError:
    _supabase_available = False
    Client = None  # type: ignore

_anon_client = None
_admin_client = None
_initialized = False


def init_clients() -> None:
    global _anon_client, _admin_client, _initialized
    _initialized = True
    if not _supabase_available:
        logger.warning("supabase package not installed — running without database")
        return
    settings = get_settings()
    try:
        _anon_client = create_client(settings.supabase_url, settings.supabase_anon_key)
        if settings.supabase_service_role_key:
            _admin_client = create_client(
                settings.supabase_url, settings.supabase_service_role_key
            )
        logger.info("Supabase clients initialized")
    except Exception as e:
        logger.warning(f"Could not connect to Supabase: {e} — running without database")


def get_supabase_client():
    if not _initialized:
        init_clients()
    return _anon_client


def get_supabase_admin():
    if not _initialized:
        init_clients()
    return _admin_client
