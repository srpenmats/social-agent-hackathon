"""Discovery worker — periodically scans platforms for engagement opportunities.

Runs as an asyncio background task.  Schedule defaults:
  TikTok:    every 10 minutes
  Instagram: every 30 minutes
  Twitter:   every  5 minutes
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_INTERVALS: dict[str, int] = {
    "tiktok": 600,
    "instagram": 1800,
    "twitter": 300,
}


class DiscoveryWorker:
    """Background worker that discovers content on a single platform."""

    def __init__(
        self,
        platform: str,
        supabase_client: Any,
        interval_seconds: int | None = None,
    ) -> None:
        self._platform = platform
        self._supabase = supabase_client
        self._interval = interval_seconds or DEFAULT_INTERVALS.get(platform, 600)
        self._running = True

    async def _check_kill_switch(self) -> bool:
        try:
            row = (
                self._supabase.table("system_config")
                .select("value")
                .eq("key", "kill_switch")
                .single()
                .execute()
            )
            if row.data:
                return row.data.get("value", {}).get("active", False)
        except Exception:
            pass
        return False

    async def _load_keywords(self) -> list[str]:
        try:
            row = (
                self._supabase.table("system_config")
                .select("value")
                .eq("key", "keyword_taxonomy")
                .single()
                .execute()
            )
            if row.data and row.data.get("value"):
                taxonomy: dict = row.data["value"]
                keywords: list[str] = []
                for terms in taxonomy.values():
                    if isinstance(terms, list):
                        keywords.extend(terms)
                return keywords[:20]  # Cap at 20 keywords per cycle
        except Exception:
            pass
        return ["finance", "money", "investing", "budget", "moneylion"]

    async def _load_discovery_config(self) -> dict:
        try:
            row = (
                self._supabase.table("system_config")
                .select("value")
                .eq("key", "discovery_config")
                .single()
                .execute()
            )
            if row.data and row.data.get("value"):
                return row.data["value"]
        except Exception:
            pass
        return {"min_engagement": 500, "max_age_hours": 24}

    async def run(self) -> None:
        """Main discovery loop."""
        from services.social.discovery import DiscoveryService

        logger.info("Discovery worker started for %s (interval=%ds)", self._platform, self._interval)

        while self._running:
            try:
                # Check kill switch
                if await self._check_kill_switch():
                    logger.info("Kill switch active — %s discovery paused", self._platform)
                    await asyncio.sleep(self._interval)
                    continue

                keywords = await self._load_keywords()
                config = await self._load_discovery_config()

                discovery = DiscoveryService(self._supabase)
                results = await discovery.discover_content(
                    platform=self._platform,
                    keywords=keywords,
                    min_engagement=config.get("min_engagement", 500),
                    max_age_hours=config.get("max_age_hours", 24),
                )

                # Store each discovered item
                stored = 0
                for item in results:
                    url = item.get("video_url") or item.get("permalink") or item.get("url")
                    if not url:
                        continue

                    classification = discovery.classify_content(item)
                    score = discovery.score_opportunity(item)

                    try:
                        self._supabase.table("discovered_videos").insert({
                            "platform": self._platform,
                            "video_url": url,
                            "creator": item.get("creator") or item.get("username") or item.get("author_id"),
                            "description": item.get("description") or item.get("caption") or item.get("text"),
                            "hashtags": item.get("hashtags", []),
                            "likes": item.get("likes", 0) or item.get("like_count", 0),
                            "comments_count": item.get("comments", 0) or item.get("comments_count", 0),
                            "shares": item.get("shares", 0),
                            "classification": classification,
                            "status": "new",
                            "discovered_at": datetime.now(timezone.utc).isoformat(),
                        }).execute()
                        stored += 1
                    except Exception as exc:
                        logger.debug("Duplicate or insert error for %s: %s", url, exc)

                # Log cycle
                self._supabase.table("audit_log").insert({
                    "action": "discovery_cycle",
                    "entity_type": self._platform,
                    "details": {
                        "found": len(results),
                        "stored": stored,
                        "keywords_used": len(keywords),
                    },
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }).execute()

                logger.info(
                    "Discovery cycle for %s: found=%d stored=%d",
                    self._platform, len(results), stored,
                )

            except asyncio.CancelledError:
                logger.info("Discovery worker for %s cancelled", self._platform)
                return
            except Exception as exc:
                logger.exception("Discovery worker error for %s: %s", self._platform, exc)

            await asyncio.sleep(self._interval)

    async def stop(self) -> None:
        self._running = False
