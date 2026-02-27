from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from db.connection import get_supabase_admin
from middleware.auth import CurrentUser
from schemas.review import (
    ReviewDecision,
    ReviewDecisionRequest,
    ReviewHistoryItem,
    ReviewHistoryResponse,
    ReviewHistoryStats,
    ReviewItem,
    ReviewQueueResponse,
    VideoContext,
)

router = APIRouter(tags=["review"])


@router.get("/api/v1/review/queue", response_model=ReviewQueueResponse)
async def review_queue(user: CurrentUser):
    db = get_supabase_admin()

    result = (
        db.table("review_queue")
        .select("*")
        .is_("decision", "null")
        .order("queued_at")
        .execute()
    )
    rows = result.data or []

    items = []
    for r in rows:
        video_context = None
        if r.get("video_id"):
            vid = (
                db.table("discovered_videos")
                .select("video_url, creator, description, classification")
                .eq("id", r["video_id"])
                .limit(1)
                .execute()
            )
            if vid.data:
                v = vid.data[0]
                video_context = VideoContext(
                    video_url=v.get("video_url"),
                    creator=v.get("creator"),
                    description=v.get("description"),
                    classification=v.get("classification"),
                )

        items.append(
            ReviewItem(
                id=r["id"],
                comment_id=r.get("comment_id"),
                video_id=r.get("video_id"),
                proposed_text=r["proposed_text"],
                risk_score=r.get("risk_score", 0),
                risk_reasoning=r.get("risk_reasoning"),
                classification=r.get("classification"),
                queued_at=r.get("queued_at"),
                video_context=video_context,
            )
        )

    now = datetime.now(timezone.utc)
    wait_times = []
    for r in rows:
        if r.get("queued_at"):
            queued = datetime.fromisoformat(r["queued_at"].replace("Z", "+00:00"))
            wait_times.append((now - queued).total_seconds() / 60)

    avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0.0
    sla_breaches = sum(1 for w in wait_times if w > 15)

    return ReviewQueueResponse(
        items=items,
        pending_count=len(rows),
        avg_wait_min=round(avg_wait, 1),
        sla_breaches=sla_breaches,
    )


@router.post("/api/v1/review/{review_id}/decide")
async def review_decide(
    review_id: int,
    body: ReviewDecisionRequest,
    user: CurrentUser,
):
    db = get_supabase_admin()

    existing = db.table("review_queue").select("id, decision").eq("id", review_id).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Review item not found")
    if existing.data.get("decision") is not None:
        raise HTTPException(status_code=400, detail="Already reviewed")

    db.table("review_queue").update({
        "decision": body.decision.value,
        "decision_reason": body.reason,
        "reviewed_by": user["id"],
        "decided_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", review_id).execute()

    # When approved, create a NeoClaw "post" task so the agent posts the comment
    if body.decision == ReviewDecision.approve:
        try:
            from services.neoclaw_queue import TaskQueue

            review_row = (
                db.table("review_queue")
                .select("proposed_text, video_id")
                .eq("id", review_id)
                .single()
                .execute()
            )
            if review_row.data:
                row = review_row.data
                video_url = ""
                platform = ""
                if row.get("video_id"):
                    vid = (
                        db.table("discovered_videos")
                        .select("video_url, platform")
                        .eq("id", row["video_id"])
                        .single()
                        .execute()
                    )
                    if vid.data:
                        video_url = vid.data.get("video_url", "")
                        platform = vid.data.get("platform", "")
                queue = TaskQueue(db)
                queue.on_comment_approved(
                    review_id=review_id,
                    video_url=video_url,
                    comment_text=row["proposed_text"],
                    platform=platform,
                )
        except Exception:
            pass  # Non-critical — don't block the review decision

    return {"status": "decided", "decision": body.decision.value}


@router.get("/api/v1/review/history", response_model=ReviewHistoryResponse)
async def review_history(
    user: CurrentUser,
    date: str | None = Query(None, description="ISO date YYYY-MM-DD"),
):
    db = get_supabase_admin()

    query = (
        db.table("review_queue")
        .select("*")
        .not_.is_("decision", "null")
    )
    if date:
        query = query.gte("decided_at", f"{date}T00:00:00").lt("decided_at", f"{date}T23:59:59")

    result = query.order("decided_at", desc=True).limit(100).execute()
    rows = result.data or []

    items = [
        ReviewHistoryItem(
            id=r["id"],
            proposed_text=r["proposed_text"],
            decision=r.get("decision"),
            decision_reason=r.get("decision_reason"),
            reviewed_by=r.get("reviewed_by"),
            queued_at=r.get("queued_at"),
            decided_at=r.get("decided_at"),
        )
        for r in rows
    ]

    approved = sum(1 for r in rows if r.get("decision") == "approve")
    rejected = sum(1 for r in rows if r.get("decision") == "reject")

    times = []
    for r in rows:
        if r.get("queued_at") and r.get("decided_at"):
            q = datetime.fromisoformat(r["queued_at"].replace("Z", "+00:00"))
            d = datetime.fromisoformat(r["decided_at"].replace("Z", "+00:00"))
            times.append((d - q).total_seconds())

    avg_time = sum(times) / len(times) if times else 0.0

    return ReviewHistoryResponse(
        items=items,
        stats=ReviewHistoryStats(
            approved=approved,
            rejected=rejected,
            avg_time_seconds=round(avg_time, 1),
        ),
    )
