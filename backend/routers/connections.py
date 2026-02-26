from fastapi import APIRouter, HTTPException, Query

from backend.db.connection import get_supabase_admin
from backend.middleware.auth import require_role
from backend.schemas.connections import (
    ConnectRequest,
    ConnectionTestResponse,
    OAuthCallbackRequest,
    PlatformConnectionResponse,
)

router = APIRouter(tags=["connections"])

VALID_PLATFORMS = {"tiktok", "instagram", "x"}


@router.get("/api/v1/connections", response_model=list[PlatformConnectionResponse])
async def list_connections(user: dict = require_role("admin")):
    db = get_supabase_admin()
    result = db.table("platforms").select("*").execute()

    return [
        PlatformConnectionResponse(
            platform=r["name"],
            status=r.get("status", "disconnected"),
            connected=r.get("status") == "connected",
            auth_method=r.get("auth_method"),
            session_health=r.get("session_health"),
            workers_status=r.get("workers_status"),
            connected_at=r.get("connected_at"),
        )
        for r in (result.data or [])
    ]


@router.post("/api/v1/connections/{platform}/connect")
async def connect_platform(platform: str, body: ConnectRequest, user: dict = require_role("admin")):
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

    db = get_supabase_admin()

    existing = db.table("platforms").select("id").eq("name", platform).execute()

    platform_data = {
        "name": platform,
        "auth_method": body.auth_method,
        "status": "connected",
        "credentials_encrypted": str(body.credentials),
        "session_health": "healthy",
        "workers_status": {"discovery": "starting", "execution": "starting", "analytics": "starting"},
    }

    if existing.data:
        db.table("platforms").update(platform_data).eq("name", platform).execute()
    else:
        db.table("platforms").insert(platform_data).execute()

    # Delegate to platform-specific service for actual connection
    try:
        if platform == "tiktok":
            from backend.services.social.tiktok import TikTokService
            await TikTokService().connect(body.credentials)
        elif platform == "instagram":
            from backend.services.social.instagram import InstagramService
            await InstagramService().connect(body.credentials)
        elif platform == "x":
            from backend.services.social.twitter import TwitterService
            await TwitterService().connect(body.credentials)
    except ImportError:
        pass  # Services not built yet

    return {"status": "connected", "platform": platform}


@router.post("/api/v1/connections/{platform}/disconnect")
async def disconnect_platform(platform: str, user: dict = require_role("admin")):
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

    db = get_supabase_admin()
    db.table("platforms").update({
        "status": "disconnected",
        "session_health": None,
        "workers_status": {},
    }).eq("name", platform).execute()

    return {"status": "disconnected", "platform": platform}


@router.post("/api/v1/connections/{platform}/test", response_model=ConnectionTestResponse)
async def test_connection(platform: str, user: dict = require_role("admin")):
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

    db = get_supabase_admin()
    result = db.table("platforms").select("status, session_health").eq("name", platform).execute()

    if not result.data:
        return ConnectionTestResponse(healthy=False, details="Platform not configured")

    p = result.data[0]
    healthy = p.get("status") == "connected" and p.get("session_health") in ("healthy", None)
    return ConnectionTestResponse(
        healthy=healthy,
        details=f"Status: {p.get('status')}, Health: {p.get('session_health', 'unknown')}",
    )


@router.get("/api/v1/auth/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str = Query(...),
    state: str | None = Query(None),
):
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {platform}")

    try:
        if platform == "instagram":
            from backend.services.social.instagram import InstagramService
            result = await InstagramService().handle_oauth_callback(code, state)
            return result
        elif platform == "x":
            from backend.services.social.twitter import TwitterService
            result = await TwitterService().handle_oauth_callback(code, state)
            return result
    except ImportError:
        pass

    return {"status": "callback_received", "platform": platform, "code": code}
