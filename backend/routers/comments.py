from fastapi import APIRouter, HTTPException, Query

from db.connection import get_supabase_admin
from middleware.auth import CurrentUser
from schemas.comments import (
    CommentDetail,
    CommentListResponse,
    CommentSaveRequest,
)

router = APIRouter(tags=["comments"])


@router.get("/api/v1/comments", response_model=CommentListResponse)
async def list_comments(
    user: CurrentUser,
    platform: str | None = Query(None),
    status: str | None = Query(None),
    category: str | None = Query(None),
    risk_min: int | None = Query(None, ge=0, le=100),
    risk_max: int | None = Query(None, ge=0, le=100),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_supabase_admin()
    query = db.table("engagements").select("*", count="exact")

    if platform:
        query = query.eq("platform", platform)
    if status:
        query = query.eq("status", status)
    if risk_min is not None:
        query = query.gte("risk_score", risk_min)
    if risk_max is not None:
        query = query.lte("risk_score", risk_max)

    offset = (page - 1) * limit
    result = query.order("posted_at", desc=True).range(offset, offset + limit - 1).execute()

    items = [
        CommentDetail(
            id=r["id"],
            platform=r["platform"],
            video_url=None,
            comment_text=r["comment_text"],
            risk_score=r.get("risk_score", 0),
            status=r.get("status", "pending"),
            likes=0,
            replies=0,
            posted_at=r.get("posted_at"),
            approval_path=r.get("approval_path"),
        )
        for r in (result.data or [])
    ]

    return CommentListResponse(
        items=items,
        total=result.count or 0,
        page=page,
        limit=limit,
    )


@router.get("/api/v1/comments/{comment_id}", response_model=CommentDetail)
async def get_comment(comment_id: int, user: CurrentUser):
    db = get_supabase_admin()

    result = db.table("engagements").select("*").eq("id", comment_id).single().execute()
    r = result.data
    if not r:
        raise HTTPException(status_code=404, detail="Comment not found")

    risk_breakdown = None
    if r.get("comment_id"):
        risk_result = (
            db.table("risk_scores")
            .select("*")
            .eq("comment_id", r["comment_id"])
            .limit(1)
            .execute()
        )
        if risk_result.data:
            rs = risk_result.data[0]
            from schemas.comments import RiskBreakdown
            risk_breakdown = RiskBreakdown(
                total_score=rs.get("total_score", 0),
                blocklist_score=rs.get("blocklist_score", 0),
                context_score=rs.get("context_score", 0),
                ai_judge_score=rs.get("ai_judge_score", 0),
                reasoning=rs.get("reasoning"),
            )

    metrics_result = (
        db.table("engagement_metrics")
        .select("likes, replies")
        .eq("engagement_id", comment_id)
        .order("checked_at", desc=True)
        .limit(1)
        .execute()
    )
    likes = 0
    replies = 0
    if metrics_result.data:
        likes = metrics_result.data[0].get("likes", 0)
        replies = metrics_result.data[0].get("replies", 0)

    return CommentDetail(
        id=r["id"],
        platform=r["platform"],
        video_url=None,
        comment_text=r["comment_text"],
        risk_score=r.get("risk_score", 0),
        risk_breakdown=risk_breakdown,
        status=r.get("status", "pending"),
        likes=likes,
        replies=replies,
        posted_at=r.get("posted_at"),
        approval_path=r.get("approval_path"),
        screenshots=[r["screenshot_url"]] if r.get("screenshot_url") else [],
    )


@router.post("/api/v1/comments/{comment_id}/save")
async def save_comment(comment_id: int, body: CommentSaveRequest, user: CurrentUser):
    db = get_supabase_admin()

    engagement = db.table("engagements").select("id").eq("id", comment_id).single().execute()
    if not engagement.data:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.table("saved_comments").insert({
        "engagement_id": comment_id,
        "saved_by": user["id"],
        "tags": body.tags,
        "notes": body.notes,
    }).execute()

    return {"status": "saved"}


@router.get("/api/v1/library/snippets")
async def list_saved_comments(
    user: CurrentUser,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    db = get_supabase_admin()
    offset = (page - 1) * limit

    result = (
        db.table("saved_comments")
        .select("*, engagements(id, platform, comment_text, posted_at)", count="exact")
        .order("saved_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    return {
        "items": result.data or [],
        "total": result.count or 0,
        "page": page,
        "limit": limit,
    }
