"""NeoClaw agent entry point API.

Bidirectional bridge between the NeoClaw browser-automation agent and the
dashboard backend. Auth uses a dedicated API key (not JWT).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from backend.config import get_settings
from backend.db.connection import get_supabase_admin
from backend.schemas.neoclaw import (
    AgentConfigResponse,
    BulkIngestRequest,
    BulkIngestResponse,
    CommentResultRequest,
    HeartbeatRequest,
    MetricsIngestRequest,
    PlatformHealthRequest,
    TaskCompleteRequest,
    TaskFailRequest,
    TaskResponse,
    TrendingIngestRequest,
    VideoIngestRequest,
    VideoIngestResponse,
)
from backend.services.neoclaw_queue import TaskQueue

logger = logging.getLogger(__name__)

router = APIRouter(tags=["neoclaw"])


# ---------------------------------------------------------------------------
# Auth dependency — API-key based
# ---------------------------------------------------------------------------

async def verify_neoclaw_key(x_api_key: str = Header(...)) -> str:
    settings = get_settings()
    if not settings.neoclaw_api_key or x_api_key != settings.neoclaw_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing NeoClaw API key",
        )
    return x_api_key


NeoClawAuth = Depends(verify_neoclaw_key)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_queue() -> TaskQueue:
    return TaskQueue(get_supabase_admin())


async def _process_video_ingest(
    body: VideoIngestRequest, db: Any
) -> VideoIngestResponse:
    """Store a discovered video and run the comment generation pipeline."""

    # 1. Store in discovered_videos
    row = {
        "platform": body.platform,
        "video_url": body.video_url,
        "creator": body.creator,
        "description": body.description,
        "transcript": body.transcript,
        "hashtags": body.hashtags,
        "likes": body.likes,
        "comments_count": body.comments_count,
        "shares": body.shares,
        "classification": body.classification,
        "status": "new",
    }
    insert_result = db.table("discovered_videos").insert(row).execute()
    video_id: int = insert_result.data[0]["id"]

    # 2. Attempt comment generation + risk scoring pipeline
    candidates: list[dict[str, Any]] = []
    try:
        from backend.services.ai.comment_generator import CommentGenerator
        from backend.services.ai.risk_scorer import RiskScorer

        video_context = {
            "video_id": video_id,
            "title": body.description or "",
            "description": body.description or "",
            "hashtags": body.hashtags,
            "creator": body.creator or "",
            "likes": body.likes,
            "comments_count": body.comments_count,
            "shares": body.shares,
            "classification": body.classification or "cultural",
            "transcript": body.transcript,
        }

        generator = CommentGenerator()
        candidates = await generator.generate_candidates(
            video_context, body.platform, num_candidates=3
        )

        scorer = RiskScorer()
        queue = _get_queue()

        for candidate in candidates:
            score_result = await scorer.score_comment(
                candidate["text"], video_context, body.platform
            )
            candidate["risk_score"] = score_result["total_score"]
            candidate["routing_decision"] = score_result["routing_decision"]

            # Store risk score
            comment_db_id = candidate.get("db_id")
            if comment_db_id:
                db.table("risk_scores").insert({
                    "comment_id": comment_db_id,
                    "total_score": score_result["total_score"],
                    "blocklist_score": score_result.get("blocklist_score", 0),
                    "context_score": score_result.get("context_score", 0),
                    "ai_judge_score": score_result.get("ai_judge_score", 0),
                    "reasoning": score_result.get("reasoning", ""),
                    "routing_decision": score_result["routing_decision"],
                }).execute()

            # Route the candidate
            routing = score_result["routing_decision"]
            if routing == "auto_approve":
                queue.create_task(
                    task_type="post",
                    platform=body.platform,
                    payload={
                        "video_url": body.video_url,
                        "comment_text": candidate["text"],
                    },
                    priority=3,
                    created_by="system",
                    metadata={"video_id": video_id, "comment_id": comment_db_id},
                )
            elif routing == "human_review":
                db.table("review_queue").insert({
                    "comment_id": comment_db_id,
                    "video_id": video_id,
                    "proposed_text": candidate["text"],
                    "risk_score": score_result["total_score"],
                    "risk_reasoning": score_result.get("reasoning", ""),
                    "classification": body.classification,
                }).execute()
            # auto_discard: do nothing

    except Exception as e:
        logger.warning("Comment pipeline failed for video %d: %s", video_id, e)

    return VideoIngestResponse(
        video_id=video_id,
        classification=body.classification,
        comment_candidates=candidates,
    )


# ---------------------------------------------------------------------------
# Ingest endpoints (NeoClaw -> Dashboard)
# ---------------------------------------------------------------------------

@router.post(
    "/api/v1/neoclaw/ingest/videos",
    response_model=VideoIngestResponse,
    dependencies=[NeoClawAuth],
)
async def ingest_video(body: VideoIngestRequest):
    db = get_supabase_admin()
    return await _process_video_ingest(body, db)


@router.post(
    "/api/v1/neoclaw/ingest/videos/bulk",
    response_model=BulkIngestResponse,
    dependencies=[NeoClawAuth],
)
async def ingest_videos_bulk(body: BulkIngestRequest):
    db = get_supabase_admin()
    results: list[VideoIngestResponse] = []
    errors: list[str] = []

    for video in body.videos:
        try:
            resp = await _process_video_ingest(video, db)
            results.append(resp)
        except Exception as e:
            errors.append(f"{video.video_url}: {e}")

    return BulkIngestResponse(results=results, errors=errors)


@router.post(
    "/api/v1/neoclaw/ingest/metrics",
    dependencies=[NeoClawAuth],
)
async def ingest_metrics(body: MetricsIngestRequest):
    db = get_supabase_admin()
    checked_at = (body.checked_at or datetime.now(timezone.utc)).isoformat()

    db.table("engagement_metrics").insert({
        "engagement_id": body.engagement_id,
        "likes": body.likes,
        "replies": body.replies,
        "reply_texts": body.reply_texts,
        "impressions": body.impressions,
        "checked_at": checked_at,
    }).execute()

    return {"status": "ok"}


@router.post(
    "/api/v1/neoclaw/ingest/comment-result",
    dependencies=[NeoClawAuth],
)
async def ingest_comment_result(body: CommentResultRequest):
    db = get_supabase_admin()
    queue = _get_queue()

    if body.success:
        # Update engagement record
        db.table("engagements").update({
            "status": "posted",
            "screenshot_url": body.screenshot_url,
            "posted_at": datetime.now(timezone.utc).isoformat(),
        }).eq("comment_text", body.comment_text).eq(
            "platform", body.platform
        ).execute()

        queue.complete_task(body.task_id, {
            "video_url": body.video_url,
            "screenshot_url": body.screenshot_url,
        })
    else:
        queue.fail_task(body.task_id, body.error_message or "Unknown posting error")

    return {"status": "ok"}


@router.post(
    "/api/v1/neoclaw/ingest/platform-health",
    dependencies=[NeoClawAuth],
)
async def ingest_platform_health(body: PlatformHealthRequest):
    db = get_supabase_admin()

    db.table("platforms").update({
        "session_health": body.session_health,
        "workers_status": body.workers_status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("name", body.platform).execute()

    return {"status": "ok"}


@router.post(
    "/api/v1/neoclaw/ingest/trending",
    dependencies=[NeoClawAuth],
)
async def ingest_trending(body: TrendingIngestRequest):
    db = get_supabase_admin()
    scraped_at = (body.scraped_at or datetime.now(timezone.utc)).isoformat()

    # Store as a system_config entry keyed by platform
    key = f"trending_{body.platform}"
    value = {
        "topics": body.topics,
        "hashtags": body.hashtags,
        "scraped_at": scraped_at,
    }

    db.table("system_config").upsert({
        "key": key,
        "value": value,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }, on_conflict="key").execute()

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Task endpoints (Dashboard -> NeoClaw)
# ---------------------------------------------------------------------------

@router.get(
    "/api/v1/neoclaw/tasks/next",
    response_model=TaskResponse | None,
    dependencies=[NeoClawAuth],
)
async def get_next_task(
    agent_id: str = Query(...),
    platform: str | None = Query(None),
    types: str | None = Query(None, description="Comma-separated task types"),
):
    queue = _get_queue()
    task_types = [t.strip() for t in types.split(",")] if types else None
    task = queue.get_next_task(agent_id, platform=platform, task_types=task_types)

    if not task:
        return None

    return TaskResponse(
        task_id=task["id"],
        type=task["type"],
        platform=task.get("platform"),
        payload=task["payload"],
        priority=task["priority"],
        expires_at=task.get("expires_at"),
    )


@router.post(
    "/api/v1/neoclaw/tasks/{task_id}/complete",
    dependencies=[NeoClawAuth],
)
async def complete_task(task_id: int, body: TaskCompleteRequest):
    queue = _get_queue()
    queue.complete_task(task_id, body.result)
    return {"status": "ok"}


@router.post(
    "/api/v1/neoclaw/tasks/{task_id}/fail",
    dependencies=[NeoClawAuth],
)
async def fail_task(task_id: int, body: TaskFailRequest):
    queue = _get_queue()
    queue.fail_task(task_id, body.error, should_retry=body.should_retry)
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Status endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/api/v1/neoclaw/heartbeat",
    dependencies=[NeoClawAuth],
)
async def heartbeat(body: HeartbeatRequest):
    db = get_supabase_admin()

    db.table("neoclaw_heartbeats").insert({
        "agent_id": body.agent_id,
        "active_sessions": body.active_sessions,
        "current_task_id": body.current_task_id,
        "system_stats": body.system_stats,
    }).execute()

    return {"status": "ok"}


@router.get(
    "/api/v1/neoclaw/config",
    response_model=AgentConfigResponse,
    dependencies=[NeoClawAuth],
)
async def get_agent_config():
    db = get_supabase_admin()

    # Fetch system config values
    config_result = db.table("system_config").select("key, value").in_(
        "key", ["kill_switch", "rate_limits", "posting_schedule"]
    ).execute()

    config_map: dict[str, Any] = {}
    for row in config_result.data or []:
        config_map[row["key"]] = row.get("value", {})

    kill_switch = config_map.get("kill_switch", {})
    rate_limits = config_map.get("rate_limits", {})
    posting_windows = config_map.get("posting_schedule", {})

    # Fetch voice config summary
    voice_result = db.table("voice_config").select("voice_guide_md").limit(1).execute()
    voice_summary = None
    if voice_result.data:
        guide = voice_result.data[0].get("voice_guide_md", "")
        voice_summary = guide[:500] if guide else None

    return AgentConfigResponse(
        kill_switch_active=bool(kill_switch.get("active", False)),
        rate_limits=rate_limits,
        posting_windows=posting_windows,
        keywords=[],
        voice_config_summary=voice_summary,
    )
