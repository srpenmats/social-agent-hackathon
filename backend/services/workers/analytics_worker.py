"""Analytics worker — tracks engagement metrics after posting.

Checks posted comments at 1h, 4h, and 24h intervals, fetches metrics
from platform APIs, and stores snapshots in the engagement_metrics table.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

CHECK_INTERVALS_HOURS = [1, 4, 24]
POLL_INTERVAL = 300  # 5 minutes


class AnalyticsWorker:
    """Background worker that tracks post-engagement metrics."""

    def __init__(self, platform: str, supabase_client: Any) -> None:
        self._platform = platform
        self._supabase = supabase_client
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

    def _is_check_due(self, engagement: dict) -> str | None:
        """Determine if a metrics check is due for this engagement.

        Returns the check interval label ("1h", "4h", "24h") if due,
        or None if no check is needed yet.
        """
        posted_at_raw = engagement.get("posted_at")
        if not posted_at_raw:
            return None

        if isinstance(posted_at_raw, str):
            try:
                posted_at = datetime.fromisoformat(posted_at_raw.replace("Z", "+00:00"))
            except ValueError:
                return None
        else:
            posted_at = posted_at_raw

        now = datetime.now(timezone.utc)
        age_hours = (now - posted_at).total_seconds() / 3600

        # Determine which snapshots already exist for this engagement
        existing_checks: set[str] = set()
        try:
            result = (
                self._supabase.table("engagement_metrics")
                .select("checked_at")
                .eq("engagement_id", engagement["id"])
                .execute()
            )
            for row in result.data or []:
                checked_raw = row.get("checked_at")
                if not checked_raw:
                    continue
                if isinstance(checked_raw, str):
                    try:
                        checked = datetime.fromisoformat(checked_raw.replace("Z", "+00:00"))
                    except ValueError:
                        continue
                else:
                    checked = checked_raw
                check_age = (checked - posted_at).total_seconds() / 3600
                if check_age < 2:
                    existing_checks.add("1h")
                elif check_age < 6:
                    existing_checks.add("4h")
                else:
                    existing_checks.add("24h")
        except Exception:
            pass

        # Find the first due check that hasn't been done
        for interval_h in CHECK_INTERVALS_HOURS:
            label = f"{interval_h}h"
            if label not in existing_checks and age_hours >= interval_h:
                return label
        return None

    async def _get_platform_service(self) -> Any:
        row = (
            self._supabase.table("platforms")
            .select("id")
            .eq("name", self._platform)
            .eq("status", "connected")
            .single()
            .execute()
        )
        if not row.data:
            return None

        platform_id = str(row.data["id"])
        if self._platform == "tiktok":
            from backend.services.social.tiktok import TikTokService
            return TikTokService(platform_id, self._supabase)
        elif self._platform == "instagram":
            from backend.services.social.instagram import InstagramService
            return InstagramService(platform_id, self._supabase)
        elif self._platform == "twitter":
            from backend.services.social.twitter import TwitterService
            return TwitterService(platform_id, self._supabase)
        return None

    async def _fetch_metrics(self, service: Any, engagement: dict) -> dict | None:
        """Fetch engagement metrics from the platform API."""
        try:
            if self._platform == "tiktok":
                comment_url = engagement.get("screenshot_url") or engagement.get("comment_text")
                if comment_url:
                    return await service.get_engagement_metrics(comment_url)
            elif self._platform == "instagram":
                media_id = engagement.get("video_id")
                if media_id:
                    return await service.get_media_insights(str(media_id))
            elif self._platform == "twitter":
                # Use the engagement's comment_id as the tweet_id of our reply
                tweet_id = engagement.get("comment_id")
                if tweet_id:
                    return await service.get_tweet_metrics(str(tweet_id))
        except Exception as exc:
            logger.debug("Failed to fetch metrics for engagement %s: %s", engagement.get("id"), exc)
        return None

    async def run(self) -> None:
        """Main analytics loop."""
        logger.info("Analytics worker started for %s", self._platform)

        while self._running:
            try:
                if await self._check_kill_switch():
                    logger.info("Kill switch active — %s analytics paused", self._platform)
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                # Fetch posted engagements for this platform
                result = (
                    self._supabase.table("engagements")
                    .select("*")
                    .eq("platform", self._platform)
                    .eq("status", "posted")
                    .execute()
                )
                engagements = result.data or []

                # Find which ones need a metrics check
                due: list[tuple[dict, str]] = []
                for eng in engagements:
                    label = self._is_check_due(eng)
                    if label:
                        due.append((eng, label))

                if not due:
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                service = await self._get_platform_service()
                if not service:
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                try:
                    for eng, label in due:
                        metrics = await self._fetch_metrics(service, eng)
                        if not metrics:
                            continue

                        # Normalize metrics across platforms
                        likes = metrics.get("likes", 0) or metrics.get("like_count", 0)
                        replies = metrics.get("replies", 0) or metrics.get("reply_count", 0)
                        impressions = metrics.get("impressions", 0) or metrics.get("impression_count")

                        try:
                            self._supabase.table("engagement_metrics").insert({
                                "engagement_id": eng["id"],
                                "checked_at": datetime.now(timezone.utc).isoformat(),
                                "likes": likes,
                                "replies": replies,
                                "impressions": impressions,
                                "reply_texts": metrics.get("reply_texts", []),
                                "reply_sentiment": metrics.get("reply_sentiment"),
                            }).execute()
                        except Exception as exc:
                            logger.debug("Failed to store metrics for engagement %s: %s", eng["id"], exc)

                    logger.info(
                        "Analytics cycle for %s: checked=%d engagements",
                        self._platform, len(due),
                    )
                finally:
                    if hasattr(service, "close"):
                        await service.close()

            except asyncio.CancelledError:
                logger.info("Analytics worker for %s cancelled", self._platform)
                return
            except Exception as exc:
                logger.exception("Analytics worker error for %s: %s", self._platform, exc)

            await asyncio.sleep(POLL_INTERVAL)

    async def stop(self) -> None:
        self._running = False
