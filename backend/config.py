from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str | None = None

    # Auth
    jwt_secret: str
    encryption_key: str | None = None

    # LLM providers
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    openai_api_key: str | None = None

    # Social platform credentials
    tiktok_client_key: str | None = None
    tiktok_client_secret: str | None = None
    instagram_app_id: str | None = None
    instagram_app_secret: str | None = None
    twitter_client_id: str | None = None
    twitter_client_secret: str | None = None

    # External services
    serper_api_key: str | None = None
    slack_webhook_url: str | None = None
    openclaw_base_url: str | None = None

    # NeoClaw agent
    neoclaw_api_key: str | None = None

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
