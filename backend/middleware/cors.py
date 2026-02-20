from backend.config import get_settings


def get_cors_config() -> dict:
    settings = get_settings()
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    return {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"],
    }
