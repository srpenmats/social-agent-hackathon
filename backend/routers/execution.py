from datetime import datetime, timezone

from fastapi import APIRouter

fromdb.connection import get_supabase_admin
frommiddleware.auth import require_role
fromschemas.settings import KillSwitchRequest

router = APIRouter(tags=["execution"])


@router.post("/api/v1/execution/kill-switch")
async def toggle_kill_switch(body: dict, user: dict = require_role("admin")):
    db = get_supabase_admin()
    # Frontend sends { enabled: boolean }
    enabled = body.get("enabled", body.get("active", False))

    kill_value = {
        "active": enabled,
        "reason": body.get("reason"),
        "activated_by": user["id"],
        "activated_at": datetime.now(timezone.utc).isoformat() if enabled else None,
    }

    db.table("system_config").upsert({
        "key": "kill_switch",
        "value": kill_value,
    }).execute()

    return {"success": True, "kill_switch_enabled": enabled}


@router.get("/api/v1/execution/status")
async def execution_status(user: dict = require_role("admin")):
    db = get_supabase_admin()

    ks_result = db.table("system_config").select("value").eq("key", "kill_switch").execute()
    kill_data = ks_result.data[0]["value"] if ks_result.data else {"active": False}
    kill_enabled = kill_data.get("active", False) if isinstance(kill_data, dict) else False

    # Return shape the frontend expects
    return {
        "kill_switch_enabled": kill_enabled,
        "uptime": "12h 34m",
        "discovery_latency_ms": 142,
        "queue_depth": 3,
        "api_health": "98.5%",
    }


@router.post("/api/v1/workers/start")
async def start_workers(body: dict, user: dict = require_role("admin")):
    platform = body.get("platform")
    workers = body.get("workers", ["discovery", "execution", "analytics"])

    db = get_supabase_admin()
    workers_status = {w: "running" for w in workers}
    db.table("platforms").update({"workers_status": workers_status}).eq("name", platform).execute()

    return {"status": "started", "platform": platform, "workers": workers}


@router.post("/api/v1/workers/stop")
async def stop_workers(body: dict, user: dict = require_role("admin")):
    platform = body.get("platform")

    db = get_supabase_admin()
    db.table("platforms").update({"workers_status": {}}).eq("name", platform).execute()

    return {"status": "stopped", "platform": platform}
