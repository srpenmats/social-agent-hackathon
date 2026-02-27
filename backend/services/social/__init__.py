"""Social platform integrations — Instagram, Twitter/X, TikTok, and discovery."""

try:
    from services.social.instagram import InstagramService
except ImportError:
    InstagramService = None  # type: ignore[assignment,misc]

try:
    from services.social.twitter import TwitterService
except ImportError:
    TwitterService = None  # type: ignore[assignment,misc]

try:
    from services.social.tiktok import TikTokService
except ImportError:
    TikTokService = None  # type: ignore[assignment,misc]

try:
    from services.social.discovery import DiscoveryService
except ImportError:
    DiscoveryService = None  # type: ignore[assignment,misc]

__all__ = ["InstagramService", "TwitterService", "TikTokService", "DiscoveryService"]
