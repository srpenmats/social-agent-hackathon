"""Background worker manager.

Manages lifecycle of discovery, execution, and analytics workers
for each social platform.  Workers are asyncio tasks that can be
started, stopped, and monitored.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class WorkerManager:
    """Singleton that manages background workers per platform."""

    _instance: "WorkerManager | None" = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "WorkerManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, supabase_client: Any | None = None) -> None:
        if self._initialized:
            return
        self._supabase = supabase_client
        self._tasks: dict[str, asyncio.Task] = {}
        self._initialized = True

    def set_supabase(self, client: Any) -> None:
        self._supabase = client

    # -- kill switch --------------------------------------------------------

    async def check_kill_switch(self) -> bool:
        """Return True if kill switch is active (all posting should stop)."""
        if not self._supabase:
            return False
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

    # -- worker lifecycle ---------------------------------------------------

    async def start_platform_workers(self, platform: str) -> dict[str, str]:
        """Start discovery, execution, and analytics workers for a platform.

        Returns a dict of worker_key -> status.
        """
        fromservices.workers.analytics_worker import AnalyticsWorker
        fromservices.workers.discovery_worker import DiscoveryWorker
        fromservices.workers.execution_worker import ExecutionWorker

        result: dict[str, str] = {}

        workers = {
            f"{platform}_discovery": DiscoveryWorker(platform, self._supabase),
            f"{platform}_execution": ExecutionWorker(platform, self._supabase),
            f"{platform}_analytics": AnalyticsWorker(platform, self._supabase),
        }

        for key, worker in workers.items():
            if key in self._tasks and not self._tasks[key].done():
                result[key] = "already_running"
                continue
            task = asyncio.create_task(worker.run(), name=key)
            self._tasks[key] = task
            result[key] = "started"
            logger.info("Worker %s started", key)

        # Update platform workers_status
        if self._supabase:
            try:
                self._supabase.table("platforms").update({
                    "workers_status": result,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }).eq("name", platform).execute()
            except Exception:
                pass

        return result

    async def stop_platform_workers(self, platform: str) -> dict[str, str]:
        """Stop all workers for a platform."""
        result: dict[str, str] = {}
        keys_to_stop = [k for k in self._tasks if k.startswith(f"{platform}_")]

        for key in keys_to_stop:
            task = self._tasks.pop(key, None)
            if task and not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=5.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                result[key] = "stopped"
            else:
                result[key] = "not_running"
            logger.info("Worker %s stopped", key)

        if self._supabase:
            try:
                self._supabase.table("platforms").update({
                    "workers_status": result,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }).eq("name", platform).execute()
            except Exception:
                pass

        return result

    def get_worker_status(self) -> dict[str, str]:
        """Return current status of all tracked workers."""
        status: dict[str, str] = {}
        for key, task in self._tasks.items():
            if task.done():
                exc = task.exception() if not task.cancelled() else None
                status[key] = f"failed: {exc}" if exc else "completed"
            else:
                status[key] = "running"
        return status

    async def stop_all(self) -> None:
        """Stop every running worker (used during shutdown)."""
        for key in list(self._tasks.keys()):
            task = self._tasks.pop(key, None)
            if task and not task.done():
                task.cancel()
        # Wait briefly for cancellation
        tasks = [t for t in self._tasks.values() if not t.done()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("All workers stopped")
