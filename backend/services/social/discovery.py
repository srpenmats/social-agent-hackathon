"""Unified content discovery service across all social platforms.

Handles cross-platform content discovery, classification, opportunity
scoring, and discovery queue management.
"""

from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Classification keywords (defaults; overridable via system_config)
# ---------------------------------------------------------------------------

DEFAULT_KEYWORD_TAXONOMY: dict[str, list[str]] = {
    "finance-educational": [
        "investing", "stock", "finance", "budget", "savings", "credit",
        "loan", "mortgage", "debt", "crypto", "401k", "retirement",
        "fintech", "banking", "money", "financial literacy",
    ],
    "cultural-trending": [
        "trending", "viral", "challenge", "meme", "trend", "fyp",
    ],
    "competitor-adjacent": [
        "cashapp", "venmo", "chime", "sofi", "robinhood", "acorns",
        "dave", "albert", "varo", "current",
    ],
    "supportive": [
        "moneylion", "money lion", "instacash", "roarmoney",
    ],
}


class DiscoveryService:
    """Cross-platform content discovery, classification, and scoring."""

    def __init__(self, supabase_client: Any) -> None:
        self._supabase = supabase_client
        self._keyword_taxonomy: dict[str, list[str]] | None = None

    # -- helpers ------------------------------------------------------------

    async def _load_keyword_taxonomy(self) -> dict[str, list[str]]:
        if self._keyword_taxonomy:
            return self._keyword_taxonomy
        try:
            row = (
                self._supabase.table("system_config")
                .select("value")
                .eq("key", "keyword_taxonomy")
                .single()
                .execute()
            )
            if row.data and row.data.get("value"):
                self._keyword_taxonomy = row.data["value"]
                return self._keyword_taxonomy
        except Exception:
            pass
        self._keyword_taxonomy = DEFAULT_KEYWORD_TAXONOMY
        return self._keyword_taxonomy

    async def _get_platform_service(self, platform: str) -> Any:
        """Lazily import and instantiate the platform service."""
        row = (
            self._supabase.table("platforms")
            .select("id")
            .eq("name", platform)
            .eq("status", "connected")
            .single()
            .execute()
        )
        if not row.data:
            return None

        platform_id = str(row.data["id"])

        if platform == "tiktok":
            from services.social.tiktok import TikTokService
            return TikTokService(platform_id, self._supabase)
        elif platform == "instagram":
            from services.social.instagram import InstagramService
            return InstagramService(platform_id, self._supabase)
        elif platform == "twitter":
            from services.social.twitter import TwitterService
            return TwitterService(platform_id, self._supabase)
        return None

    # -- public API ---------------------------------------------------------

    async def discover_content(
        self,
        platform: str,
        keywords: list[str],
        hashtags: list[str] | None = None,
        min_engagement: int = 500,
        max_age_hours: int = 24,
    ) -> list[dict]:
        """Find relevant content on a platform matching keywords/hashtags."""
        service = await self._get_platform_service(platform)
        if not service:
            return []

        raw_results: list[dict] = []
        try:
            if platform == "tiktok":
                raw_results = await service.scan_feed(keywords)
            elif platform == "instagram":
                search_terms = hashtags or keywords
                raw_results = await service.search_explore(search_terms)
            elif platform == "twitter":
                query = " OR ".join(keywords[:5])
                if hashtags:
                    query += " " + " OR ".join(f"#{h.lstrip('#')}" for h in hashtags[:3])
                raw_results = await service.search_tweets(query, max_results=50)
        except Exception:
            pass  # Platform may be temporarily unavailable
        finally:
            if hasattr(service, "close"):
                await service.close()

        # Filter by engagement threshold
        filtered = []
        for item in raw_results:
            likes = item.get("likes", 0) or item.get("like_count", 0)
            metrics = item.get("public_metrics", {})
            if metrics:
                likes = metrics.get("like_count", likes)
            if likes >= min_engagement:
                filtered.append(item)

        # Deduplicate against already-discovered
        filtered = await self.filter_already_engaged(filtered)
        return filtered

    def classify_content(self, video_data: dict) -> str:
        """Classify content into one of four categories.

        Uses keyword matching against the taxonomy.  Returns the
        best-matching category or 'cultural-trending' as default.
        """
        text = " ".join([
            video_data.get("description", ""),
            video_data.get("caption", ""),
            video_data.get("text", ""),
            " ".join(video_data.get("hashtags", [])),
        ]).lower()

        taxonomy = self._keyword_taxonomy or DEFAULT_KEYWORD_TAXONOMY
        scores: dict[str, int] = {}
        for category, terms in taxonomy.items():
            scores[category] = sum(1 for term in terms if term.lower() in text)

        if not any(scores.values()):
            return "cultural-trending"
        return max(scores, key=lambda k: scores[k])

    def score_opportunity(self, video_data: dict) -> int:
        """Score a content opportunity from 0 to 100.

        Weighted: engagement 40%, freshness 20%, relevance 30%, reach 10%.
        """
        # Engagement score (0-100 based on likes, capped at 50k)
        likes = video_data.get("likes", 0) or video_data.get("like_count", 0)
        metrics = video_data.get("public_metrics", {})
        if metrics:
            likes = metrics.get("like_count", likes)
        engagement_score = min(likes / 500, 100)  # 50k likes = 100

        # Freshness score (0-100, fully fresh = 100, >48h = 0)
        freshness_score = 50.0  # default for unknown age
        discovered_at = video_data.get("discovered_at") or video_data.get("created_at") or video_data.get("timestamp")
        if discovered_at:
            if isinstance(discovered_at, str):
                try:
                    dt = datetime.fromisoformat(discovered_at.replace("Z", "+00:00"))
                except ValueError:
                    dt = None
            elif isinstance(discovered_at, (int, float)):
                dt = datetime.fromtimestamp(discovered_at, tz=timezone.utc)
            else:
                dt = discovered_at
            if dt:
                age_hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
                freshness_score = max(0, 100 - (age_hours / 48 * 100))

        # Relevance score based on classification
        classification = self.classify_content(video_data)
        relevance_map = {
            "finance-educational": 90,
            "supportive": 80,
            "competitor-adjacent": 70,
            "cultural-trending": 50,
        }
        relevance_score = relevance_map.get(classification, 50)

        # Reach score (follower count of creator, capped at 1M)
        followers = video_data.get("followers_count", 0) or video_data.get("creator_followers", 0)
        reach_score = min(followers / 10000, 100)  # 1M followers = 100

        total = (
            engagement_score * 0.4
            + freshness_score * 0.2
            + relevance_score * 0.3
            + reach_score * 0.1
        )
        return int(min(max(total, 0), 100))

    async def get_trending_topics(self) -> list[dict]:
        """Aggregate trending topics across all connected platforms."""
        topics: list[dict] = []
        for platform in ("tiktok", "instagram", "twitter"):
            service = await self._get_platform_service(platform)
            if not service:
                continue
            try:
                if platform == "twitter":
                    tweets = await service.search_tweets("trending finance OR money", max_results=10)
                    for tweet in tweets:
                        text = tweet.get("text", "")
                        topics.append({"topic": text[:80], "platform": platform, "volume": 0})
                # TikTok and IG trending require scan_feed which returns hashtags
                elif platform == "tiktok":
                    videos = await service.scan_feed(["trending", "finance"])
                    seen = set()
                    for v in videos:
                        for tag in v.get("hashtags", []):
                            if tag not in seen:
                                seen.add(tag)
                                topics.append({"topic": tag, "platform": platform, "volume": v.get("likes", 0)})
            except Exception:
                continue
            finally:
                if hasattr(service, "close"):
                    await service.close()
        return topics

    async def filter_already_engaged(self, videos: list[dict]) -> list[dict]:
        """Remove videos/tweets that we've already engaged with."""
        if not videos:
            return []
        urls = [
            v.get("video_url") or v.get("permalink") or v.get("url")
            for v in videos
            if v.get("video_url") or v.get("permalink") or v.get("url")
        ]
        if not urls:
            return videos

        try:
            existing = (
                self._supabase.table("discovered_videos")
                .select("video_url")
                .in_("video_url", urls)
                .execute()
            )
            engaged_urls = {row["video_url"] for row in (existing.data or [])}
        except Exception:
            engaged_urls = set()

        return [
            v for v in videos
            if (v.get("video_url") or v.get("permalink") or v.get("url")) not in engaged_urls
        ]

    async def get_discovery_queue(self) -> list[dict]:
        """Return prioritized queue of discovered videos pending engagement."""
        result = (
            self._supabase.table("discovered_videos")
            .select("*")
            .eq("status", "new")
            .eq("engaged", False)
            .order("likes", desc=True)
            .limit(50)
            .execute()
        )
        return result.data or []

    async def update_keywords(self, keywords_config: dict) -> bool:
        """Update keyword taxonomy in system_config."""
        self._supabase.table("system_config").upsert({
            "key": "keyword_taxonomy",
            "value": keywords_config,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        self._keyword_taxonomy = keywords_config
        return True
