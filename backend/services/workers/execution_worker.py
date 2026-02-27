"""Execution worker — posts approved comments to social platforms.

Reads from the review_queue (decision=approve) and engagements (status=ready),
applies human-like delays, and posts via the appropriate platform service.
"""

import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Default posting window: 8 AM – 11 PM EST (UTC-5 → 13:00–04:00 UTC)
DEFAULT_POSTING_HOURS = (8, 23)  # Evaluated in EST
POLL_INTERVAL = 30  # seconds


class ExecutionWorker:
    """Background worker that posts approved comments for a single platform."""

    MAX_RETRIES = 3

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

    async def _check_posting_schedule(self) -> bool:
        """Return True if posting is allowed at the current hour (EST)."""
        try:
            row = (
                self._supabase.table("system_config")
                .select("value")
                .eq("key", "execution_config")
                .single()
                .execute()
            )
            if row.data and row.data.get("value"):
                schedule = row.data["value"].get("schedule", {})
                start_hour = schedule.get("start_hour", DEFAULT_POSTING_HOURS[0])
                end_hour = schedule.get("end_hour", DEFAULT_POSTING_HOURS[1])
            else:
                start_hour, end_hour = DEFAULT_POSTING_HOURS
        except Exception:
            start_hour, end_hour = DEFAULT_POSTING_HOURS

        # Approximate EST as UTC-5
        utc_hour = datetime.now(timezone.utc).hour
        est_hour = (utc_hour - 5) % 24
        return start_hour <= est_hour < end_hour

    async def _apply_human_delay(self) -> None:
        """Sleep with configurable human-like jitter."""
        try:
            row = (
                self._supabase.table("system_config")
                .select("value")
                .eq("key", "execution_config")
                .single()
                .execute()
            )
            if row.data and row.data.get("value"):
                behavior = row.data["value"].get("behavior", {})
                base_delay = behavior.get("base_delay", 4)
                jitter = behavior.get("jitter", 30)
            else:
                base_delay, jitter = 4, 30
        except Exception:
            base_delay, jitter = 4, 30

        delay = base_delay + random.uniform(-jitter, jitter)
        delay = max(1.0, delay)  # Floor at 1 second
        await asyncio.sleep(delay)

    async def _get_platform_service(self) -> Any:
        """Instantiate the correct platform service."""
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
            fromservices.social.tiktok import TikTokService
            return TikTokService(platform_id, self._supabase)
        elif self._platform == "instagram":
            fromservices.social.instagram import InstagramService
            return InstagramService(platform_id, self._supabase)
        elif self._platform == "twitter":
            fromservices.social.twitter import TwitterService
            return TwitterService(platform_id, self._supabase)
        return None

    async def _fetch_approved_items(self) -> list[dict]:
        """Fetch items ready for posting on this platform."""
        items: list[dict] = []

        # Approved review queue items not yet posted
        try:
            result = (
                self._supabase.table("review_queue")
                .select("*, discovered_videos!inner(platform, video_url)")
                .eq("decision", "approve")
                .is_("decided_at", "not.null")
                .execute()
            )
            for row in result.data or []:
                video = row.get("discovered_videos", {})
                if video.get("platform") == self._platform:
                    items.append(row)
        except Exception:
            pass

        # Also check engagements table for status=ready
        try:
            result = (
                self._supabase.table("engagements")
                .select("*")
                .eq("platform", self._platform)
                .eq("status", "ready")
                .limit(10)
                .execute()
            )
            items.extend(result.data or [])
        except Exception:
            pass

        return items

    async def _post_comment(self, service: Any, item: dict) -> dict:
        """Post a single comment using the platform service."""
        video_url = (
            item.get("video_url")
            or (item.get("discovered_videos") or {}).get("video_url")
        )
        text = item.get("proposed_text") or item.get("comment_text", "")

        if self._platform == "tiktok":
            return await service.post_comment(video_url, text)
        elif self._platform == "instagram":
            media_id = item.get("media_id") or item.get("video_id")
            if media_id:
                return await service.post_comment(str(media_id), text)
            return {"success": False, "error": "No media_id available"}
        elif self._platform == "twitter":
            tweet_id = item.get("tweet_id") or item.get("video_id")
            if tweet_id:
                return await service.post_reply(str(tweet_id), text)
            return {"success": False, "error": "No tweet_id available"}
        return {"success": False, "error": f"Unknown platform: {self._platform}"}

    async def run(self) -> None:
        """Main execution loop."""
        logger.info("Execution worker started for %s", self._platform)

        while self._running:
            try:
                if await self._check_kill_switch():
                    logger.info("Kill switch active — %s execution paused", self._platform)
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                if not await self._check_posting_schedule():
                    logger.debug("Outside posting window — %s execution sleeping", self._platform)
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                items = await self._fetch_approved_items()
                if not items:
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                service = await self._get_platform_service()
                if not service:
                    logger.warning("Platform %s not connected — execution sleeping", self._platform)
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                try:
                    for item in items:
                        await self._apply_human_delay()

                        # Retry loop
                        success = False
                        last_error = None
                        for attempt in range(1, self.MAX_RETRIES + 1):
                            try:
                                result = await self._post_comment(service, item)
                                if result.get("success"):
                                    success = True
                                    # Update engagement status
                                    engagement_id = item.get("id")
                                    if engagement_id:
                                        self._supabase.table("engagements").update({
                                            "status": "posted",
                                            "posted_at": datetime.now(timezone.utc).isoformat(),
                                        }).eq("id", engagement_id).execute()
                                    break
                                last_error = result.get("error", "Unknown error")
                            except Exception as exc:
                                last_error = str(exc)
                                if attempt < self.MAX_RETRIES:
                                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

                        if not success:
                            logger.warning(
                                "Failed to post on %s after %d retries: %s",
                                self._platform, self.MAX_RETRIES, last_error,
                            )
                            engagement_id = item.get("id")
                            if engagement_id:
                                self._supabase.table("engagements").update({
                                    "status": "failed",
                                }).eq("id", engagement_id).execute()

                        # Log attempt
                        self._supabase.table("audit_log").insert({
                            "action": "execution_attempt",
                            "entity_type": self._platform,
                            "details": {
                                "item_id": item.get("id"),
                                "success": success,
                                "error": last_error if not success else None,
                            },
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }).execute()
                finally:
                    if hasattr(service, "close"):
                        await service.close()

            except asyncio.CancelledError:
                logger.info("Execution worker for %s cancelled", self._platform)
                return
            except Exception as exc:
                logger.exception("Execution worker error for %s: %s", self._platform, exc)

            await asyncio.sleep(POLL_INTERVAL)

    async def stop(self) -> None:
        self._running = False
