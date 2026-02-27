"""
Auto-refresh scheduler for CashKitty dashboard.
Runs every hour to keep Twitter data fresh.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import asyncio
import os

from routers.agent_smart import discover_smart, SmartDiscoveryRequest

router = APIRouter(prefix="/api/v1/scheduler", tags=["scheduler"])

# In-memory flag to prevent duplicate runs
_is_refreshing = False


@router.post("/hourly-refresh")
async def hourly_refresh():
    """
    Hourly auto-refresh endpoint.
    Call this from a cron job or scheduler to keep data fresh.
    """
    global _is_refreshing
    
    if _is_refreshing:
        return {
            "success": False,
            "message": "Refresh already in progress",
            "skipped": True
        }
    
    _is_refreshing = True
    try:
        # Run discovery with good engagement threshold
        result = await discover_smart(SmartDiscoveryRequest(
            query="personal finance OR money tips OR budgeting OR investing OR debt OR savings",
            min_engagement=100,
            max_results=25
        ))
        
        return {
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "auto_refresh": True,
            **result
        }
    finally:
        _is_refreshing = False


@router.get("/health")
async def scheduler_health():
    """Check scheduler health."""
    return {
        "status": "ok",
        "refreshing": _is_refreshing,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Background task runner (optional - for testing)
async def run_hourly_refresh_loop():
    """
    Background loop that runs refresh every hour.
    This is for local testing - in production use a proper cron job.
    """
    while True:
        await asyncio.sleep(3600)  # 1 hour
        try:
            await hourly_refresh()
        except Exception as e:
            print(f"Auto-refresh failed: {e}")
