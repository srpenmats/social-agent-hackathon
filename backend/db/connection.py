from supabase import Client, create_client

from backend.config import get_settings

_anon_client: Client | None = None
_admin_client: Client | None = None


def init_clients() -> None:
    global _anon_client, _admin_client
    settings = get_settings()
    _anon_client = create_client(settings.supabase_url, settings.supabase_anon_key)
    if settings.supabase_service_role_key:
        _admin_client = create_client(
            settings.supabase_url, settings.supabase_service_role_key
        )


def get_supabase_client() -> Client:
    if _anon_client is None:
        init_clients()
    assert _anon_client is not None, "Supabase anon client not initialized"
    return _anon_client


def get_supabase_admin() -> Client:
    if _admin_client is None:
        init_clients()
    assert _admin_client is not None, "Supabase admin client not initialized (missing SUPABASE_SERVICE_ROLE_KEY)"
    return _admin_client
