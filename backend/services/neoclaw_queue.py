"""Task queue service for NeoClaw agent integration.

Manages the lifecycle of tasks that NeoClaw executes: creating, claiming,
completing, failing, and cancelling. Integrates with the kill switch from
system_config to halt all operations when activated.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from supabase import Client
except ImportError:
    Client = None  # type: ignore

logger = logging.getLogger(__name__)


class TaskQueue:
    """Manages the neoclaw_tasks queue for agent work items."""

    def __init__(self, client: Client):
        self.client = client

    # ------------------------------------------------------------------
    # Core task lifecycle
    # ------------------------------------------------------------------

    def create_task(
        self,
        task_type: str,
        platform: str | None,
        payload: dict[str, Any],
        priority: int = 5,
        max_retries: int = 3,
        expires_in_minutes: int = 60,
        created_by: str = "system",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Create a new task in the queue. Returns the task id."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=expires_in_minutes)

        row = {
            "type": task_type,
            "platform": platform,
            "payload": payload,
            "priority": priority,
            "status": "pending",
            "max_retries": max_retries,
            "expires_at": expires_at.isoformat(),
            "created_by": created_by,
            "metadata": metadata or {},
        }

        result = self.client.table("neoclaw_tasks").insert(row).execute()
        task_id: int = result.data[0]["id"]
        logger.info("Created task %d (type=%s, platform=%s)", task_id, task_type, platform)
        return task_id

    def get_next_task(
        self,
        agent_id: str,
        platform: str | None = None,
        task_types: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """Atomically claim the highest-priority pending task.

        Returns the task row dict, or None if the queue is empty or
        the kill switch is active.
        """
        if self._is_kill_switch_active():
            logger.warning("Kill switch active — not dispatching tasks")
            return None

        query = (
            self.client.table("neoclaw_tasks")
            .select("*")
            .eq("status", "pending")
            .order("priority")
            .order("created_at")
            .limit(1)
        )

        if platform:
            query = query.eq("platform", platform)
        if task_types:
            query = query.in_("type", task_types)

        result = query.execute()
        if not result.data:
            return None

        task = result.data[0]

        # Check expiry
        if task.get("expires_at"):
            expires = datetime.fromisoformat(task["expires_at"].replace("Z", "+00:00"))
            if expires < datetime.now(timezone.utc):
                self.client.table("neoclaw_tasks").update(
                    {"status": "expired"}
                ).eq("id", task["id"]).execute()
                return None

        # Claim the task
        now = datetime.now(timezone.utc).isoformat()
        self.client.table("neoclaw_tasks").update({
            "status": "assigned",
            "assigned_agent": agent_id,
            "started_at": now,
        }).eq("id", task["id"]).eq("status", "pending").execute()

        task["status"] = "assigned"
        task["assigned_agent"] = agent_id
        task["started_at"] = now
        logger.info("Task %d assigned to agent %s", task["id"], agent_id)
        return task

    def complete_task(self, task_id: int, result: dict[str, Any]) -> None:
        """Mark a task as completed with its result data."""
        self.client.table("neoclaw_tasks").update({
            "status": "completed",
            "result": result,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", task_id).execute()
        logger.info("Task %d completed", task_id)

    def fail_task(
        self, task_id: int, error: str, should_retry: bool = True
    ) -> None:
        """Mark a task as failed. Re-queues if retries remain."""
        task_result = (
            self.client.table("neoclaw_tasks")
            .select("retry_count, max_retries")
            .eq("id", task_id)
            .single()
            .execute()
        )
        task = task_result.data
        retry_count = task.get("retry_count", 0)
        max_retries = task.get("max_retries", 3)

        if should_retry and retry_count < max_retries:
            self.client.table("neoclaw_tasks").update({
                "status": "pending",
                "assigned_agent": None,
                "started_at": None,
                "retry_count": retry_count + 1,
                "error": error,
            }).eq("id", task_id).execute()
            logger.info("Task %d re-queued (retry %d/%d)", task_id, retry_count + 1, max_retries)
        else:
            self.client.table("neoclaw_tasks").update({
                "status": "failed",
                "error": error,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", task_id).execute()
            logger.warning("Task %d failed permanently: %s", task_id, error)

    def cancel_task(self, task_id: int) -> None:
        """Cancel a single task."""
        self.client.table("neoclaw_tasks").update({
            "status": "cancelled",
        }).eq("id", task_id).execute()
        logger.info("Task %d cancelled", task_id)

    def cancel_all_tasks(self, platform: str | None = None) -> int:
        """Cancel all pending/assigned tasks. Returns count cancelled."""
        query = (
            self.client.table("neoclaw_tasks")
            .select("id")
            .in_("status", ["pending", "assigned"])
        )
        if platform:
            query = query.eq("platform", platform)

        result = query.execute()
        ids = [r["id"] for r in (result.data or [])]

        for task_id in ids:
            self.client.table("neoclaw_tasks").update({
                "status": "cancelled",
            }).eq("id", task_id).execute()

        logger.info("Cancelled %d tasks (platform=%s)", len(ids), platform)
        return len(ids)

    def expire_stale_tasks(self) -> int:
        """Expire tasks past their expires_at. Returns count expired."""
        now = datetime.now(timezone.utc).isoformat()
        result = (
            self.client.table("neoclaw_tasks")
            .select("id")
            .in_("status", ["pending", "assigned"])
            .lt("expires_at", now)
            .execute()
        )
        ids = [r["id"] for r in (result.data or [])]

        for task_id in ids:
            self.client.table("neoclaw_tasks").update({
                "status": "expired",
            }).eq("id", task_id).execute()

        if ids:
            logger.info("Expired %d stale tasks", len(ids))
        return len(ids)

    # ------------------------------------------------------------------
    # Stats / counts
    # ------------------------------------------------------------------

    def get_pending_count(self, platform: str | None = None) -> int:
        """Count of pending tasks, optionally filtered by platform."""
        query = (
            self.client.table("neoclaw_tasks")
            .select("id", count="exact")
            .eq("status", "pending")
        )
        if platform:
            query = query.eq("platform", platform)
        result = query.execute()
        return result.count or 0

    def get_task_stats(self) -> dict[str, Any]:
        """Aggregate task counts by status."""
        result = (
            self.client.table("neoclaw_tasks")
            .select("status")
            .execute()
        )
        counts: dict[str, int] = {}
        for row in result.data or []:
            s = row.get("status", "unknown")
            counts[s] = counts.get(s, 0) + 1
        return {"by_status": counts, "total": sum(counts.values())}

    # ------------------------------------------------------------------
    # Integration hooks (called by other parts of the system)
    # ------------------------------------------------------------------

    def on_comment_approved(
        self,
        review_id: int,
        video_url: str,
        comment_text: str,
        platform: str,
    ) -> int:
        """Create a 'post' task when a comment is approved in the review queue."""
        return self.create_task(
            task_type="post",
            platform=platform,
            payload={
                "video_url": video_url,
                "comment_text": comment_text,
            },
            priority=2,
            created_by="dashboard",
            metadata={"review_queue_id": review_id},
        )

    def on_discovery_needed(
        self, platform: str, keywords: list[str]
    ) -> int:
        """Create a 'discover' task for content discovery."""
        return self.create_task(
            task_type="discover",
            platform=platform,
            payload={"keywords": keywords},
            priority=5,
            created_by="system",
        )

    def on_metrics_check_needed(
        self, engagement_id: int, platform: str, comment_url: str
    ) -> int:
        """Create a 'track' task for post-engagement metrics collection."""
        return self.create_task(
            task_type="track",
            platform=platform,
            payload={
                "engagement_id": engagement_id,
                "comment_url": comment_url,
            },
            priority=7,
            created_by="system",
            metadata={"engagement_id": engagement_id},
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_kill_switch_active(self) -> bool:
        """Check if the global kill switch is active."""
        try:
            result = (
                self.client.table("system_config")
                .select("value")
                .eq("key", "kill_switch")
                .single()
                .execute()
            )
            if result.data:
                value = result.data.get("value", {})
                return bool(value.get("active", False))
        except Exception as e:
            logger.error("Failed to check kill switch: %s", e)
        return False
