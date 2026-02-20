from datetime import datetime, timezone

from fastapi import APIRouter

from backend.db.connection import get_supabase_admin
from backend.middleware.auth import require_role
from backend.schemas.settings import KillSwitchRequest

router = APIRouter(tags=["execution"])


@router.post("/api/v1/execution/kill-switch")
async def toggle_kill_switch(body: KillSwitchRequest, user: dict = require_role("admin")):
    db = get_supabase_admin()

    kill_value = {
        "active": body.active,
        "reason": body.reason,
        "activated_by": user["id"],
        "activated_at": datetime.now(timezone.utc).isoformat() if body.active else None,
    }

    db.table("system_config").upsert({
        "key": "kill_switch",
        "value": kill_value,
    }).execute()

    db.table("audit_log").insert({
        "user_id": user["id"],
        "action": "kill_switch_activated" if body.active else "kill_switch_deactivated",
        "entity_type": "system_config",
        "entity_id": "kill_switch",
        "details": kill_value,
    }).execute()

    return {"status": "active" if body.active else "inactive", "kill_switch": kill_value}


@router.get("/api/v1/execution/status")
async def execution_status(user: dict = require_role("admin")):
    db = get_supabase_admin()

    ks_result = db.table("system_config").select("value").eq("key", "kill_switch").execute()
    kill_switch = ks_result.data[0]["value"] if ks_result.data else {"active": False}

    platforms_result = db.table("platforms").select("name, status, workers_status").execute()
    platforms = {
        p["name"]: {"status": p["status"], "workers": p.get("workers_status", {})}
        for p in (platforms_result.data or [])
    }

    return {
        "kill_switch": kill_switch,
        "platforms": platforms,
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
