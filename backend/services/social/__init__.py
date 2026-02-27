"""Social platform integrations — Instagram, Twitter/X, TikTok, and discovery."""

try:
    fromservices.social.instagram import InstagramService
except ImportError:
    InstagramService = None  # type: ignore[assignment,misc]

try:
    fromservices.social.twitter import TwitterService
except ImportError:
    TwitterService = None  # type: ignore[assignment,misc]

try:
    fromservices.social.tiktok import TikTokService
except ImportError:
    TikTokService = None  # type: ignore[assignment,misc]

try:
    fromservices.social.discovery import DiscoveryService
except ImportError:
    DiscoveryService = None  # type: ignore[assignment,misc]

__all__ = ["InstagramService", "TwitterService", "TikTokService", "DiscoveryService"]
