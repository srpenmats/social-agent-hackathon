from fastapi import APIRouter

from db.connection import get_supabase_admin
from middleware.auth import require_role
from schemas.settings import (
    DiscoveryConfigResponse,
    DiscoveryConfigUpdateRequest,
    ExecutionConfigResponse,
    ExecutionConfigUpdateRequest,
    RiskConfigResponse,
    RiskConfigUpdateRequest,
    VoiceConfigResponse,
    VoiceConfigUpdateRequest,
    VoiceTestRequest,
    VoiceTestResponse,
)

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


# --- API Keys ---

_KNOWN_PROVIDERS = [
    {"provider": "anthropic", "name": "Anthropic (Claude)", "icon": "psychology"},
    {"provider": "openai", "name": "OpenAI", "icon": "auto_awesome"},
    {"provider": "gemini", "name": "Google Gemini", "icon": "stars"},
    {"provider": "serper", "name": "Serper (Search)", "icon": "search"},
]


@router.get("/api-keys")
async def get_api_keys(user: dict = require_role("admin")):
    db = get_supabase_admin()
    result = db.table("system_config").select("key, value").eq("key", "api_keys").execute()
    stored = result.data[0].get("value", {}) if result.data else {}

    items = []
    for p in _KNOWN_PROVIDERS:
        raw = stored.get(p["provider"], "")
        connected = bool(raw)
        masked = f"****{raw[-4:]}" if isinstance(raw, str) and len(raw) > 4 else None
        items.append({**p, "connected": connected, "masked_key": masked})
    return items


@router.put("/api-keys")
async def update_api_keys(body: dict, user: dict = require_role("admin")):
    db = get_supabase_admin()
    db.table("system_config").upsert({
        "key": "api_keys",
        "value": body,
    }).execute()
    return {"status": "updated"}


# --- Voice ---

@router.get("/voice", response_model=VoiceConfigResponse)
async def get_voice_config(user: dict = require_role("admin")):
    db = get_supabase_admin()
    result = db.table("voice_config").select("*").limit(1).execute()
    if not result.data:
        return VoiceConfigResponse()
    r = result.data[0]
    return VoiceConfigResponse(
        voice_guide_md=r.get("voice_guide_md"),
        positive_examples=r.get("positive_examples", []),
        negative_examples=r.get("negative_examples", []),
        platform_adapters=r.get("platform_adapters", {}),
    )


@router.put("/voice", response_model=VoiceConfigResponse)
async def update_voice_config(body: VoiceConfigUpdateRequest, user: dict = require_role("admin")):
    db = get_supabase_admin()
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    update_data["updated_by"] = user["id"]

    existing = db.table("voice_config").select("id").limit(1).execute()
    if existing.data:
        db.table("voice_config").update(update_data).eq("id", existing.data[0]["id"]).execute()
    else:
        db.table("voice_config").insert(update_data).execute()

    return await get_voice_config(user)


@router.post("/voice/test", response_model=VoiceTestResponse)
async def test_voice(body: VoiceTestRequest, user: dict = require_role("admin")):
    try:
        from services.ai.comment_generator import CommentGenerator
        generator = CommentGenerator()
        candidates = await generator.generate(body.video_context)
        return VoiceTestResponse(candidates=candidates)
    except (ImportError, Exception):
        return VoiceTestResponse(candidates=[
            {"text": f"[stub] Comment for: {body.video_context[:50]}", "approach": "witty", "char_count": 50},
            {"text": f"[stub] Helpful take on: {body.video_context[:50]}", "approach": "helpful", "char_count": 50},
            {"text": f"[stub] Supportive note: {body.video_context[:50]}", "approach": "supportive", "char_count": 50},
        ])


# --- Risk ---

@router.get("/risk", response_model=RiskConfigResponse)
async def get_risk_config(user: dict = require_role("admin")):
    db = get_supabase_admin()
    result = db.table("risk_config").select("*").limit(1).execute()
    if not result.data:
        return RiskConfigResponse()
    r = result.data[0]
    return RiskConfigResponse(
        auto_approve_max=r.get("auto_approve_max", 30),
        review_max=r.get("review_max", 65),
        blocklist=r.get("blocklist", {}),
        override_rules=r.get("override_rules", []),
    )


@router.put("/risk", response_model=RiskConfigResponse)
async def update_risk_config(body: RiskConfigUpdateRequest, user: dict = require_role("admin")):
    db = get_supabase_admin()
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    existing = db.table("risk_config").select("id").limit(1).execute()
    if existing.data:
        db.table("risk_config").update(update_data).eq("id", existing.data[0]["id"]).execute()
    else:
        db.table("risk_config").insert(update_data).execute()
    return await get_risk_config(user)


# --- Discovery ---

@router.get("/discovery", response_model=DiscoveryConfigResponse)
async def get_discovery_config(user: dict = require_role("admin")):
    db = get_supabase_admin()
    result = db.table("system_config").select("key, value").in_("key", ["discovery_keywords", "discovery_schedule", "discovery_thresholds"]).execute()
    config = {r["key"]: r["value"] for r in (result.data or [])}
    return DiscoveryConfigResponse(
        keywords=config.get("discovery_keywords", {}),
        schedule=config.get("discovery_schedule", {}),
        thresholds=config.get("discovery_thresholds", {}),
    )


@router.put("/discovery", response_model=DiscoveryConfigResponse)
async def update_discovery_config(body: DiscoveryConfigUpdateRequest, user: dict = require_role("admin")):
    db = get_supabase_admin()
    if body.keywords is not None:
        db.table("system_config").upsert({"key": "discovery_keywords", "value": body.keywords}).execute()
    if body.schedule is not None:
        db.table("system_config").upsert({"key": "discovery_schedule", "value": body.schedule}).execute()
    if body.thresholds is not None:
        db.table("system_config").upsert({"key": "discovery_thresholds", "value": body.thresholds}).execute()
    return await get_discovery_config(user)


# --- Execution ---

@router.get("/execution", response_model=ExecutionConfigResponse)
async def get_execution_config(user: dict = require_role("admin")):
    db = get_supabase_admin()
    result = db.table("system_config").select("key, value").in_("key", ["rate_limits", "execution_behavior", "posting_schedule", "supervised_mode"]).execute()
    config = {r["key"]: r["value"] for r in (result.data or [])}
    return ExecutionConfigResponse(
        rate_limits=config.get("rate_limits", {}),
        behavior=config.get("execution_behavior", {}),
        schedule=config.get("posting_schedule", {}),
        supervised_mode=config.get("supervised_mode", {}).get("enabled", False),
    )


@router.put("/execution", response_model=ExecutionConfigResponse)
async def update_execution_config(body: ExecutionConfigUpdateRequest, user: dict = require_role("admin")):
    db = get_supabase_admin()
    if body.rate_limits is not None:
        db.table("system_config").upsert({"key": "rate_limits", "value": body.rate_limits}).execute()
    if body.behavior is not None:
        db.table("system_config").upsert({"key": "execution_behavior", "value": body.behavior}).execute()
    if body.schedule is not None:
        db.table("system_config").upsert({"key": "posting_schedule", "value": body.schedule}).execute()
    if body.supervised_mode is not None:
        db.table("system_config").upsert({"key": "supervised_mode", "value": {"enabled": body.supervised_mode}}).execute()
    return await get_execution_config(user)
