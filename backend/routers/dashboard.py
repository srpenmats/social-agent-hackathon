from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query

from backend.db.connection import get_supabase_admin
from backend.middleware.auth import CurrentUser
from backend.schemas.dashboard import (
    EngagementTimelinePoint,
    EngagementTimelineResponse,
    HashtagPerformance,
    HashtagPerformanceResponse,
    OverviewResponse,
    PlatformStatsResponse,
    PlatformSummary,
    Timeframe,
)

router = APIRouter(tags=["dashboard"])


def _timeframe_start(tf: Timeframe) -> str:
    delta = {"24h": timedelta(hours=24), "7d": timedelta(days=7), "30d": timedelta(days=30)}
    start = datetime.now(timezone.utc) - delta[tf.value]
    return start.isoformat()


@router.get("/api/v1/dashboard/overview", response_model=OverviewResponse)
async def dashboard_overview(
    user: CurrentUser,
    timeframe: Timeframe = Query(Timeframe.day),
):
    db = get_supabase_admin()
    since = _timeframe_start(timeframe)

    engagements = (
        db.table("engagements")
        .select("id, platform, risk_score, approval_path, posted_at")
        .gte("posted_at", since)
        .execute()
    )
    rows = engagements.data or []
    total = len(rows)

    platforms_resp = db.table("platforms").select("name, status").execute()
    active = sum(1 for p in (platforms_resp.data or []) if p["status"] == "connected")

    auto_count = sum(1 for r in rows if r.get("approval_path") == "auto")
    approval_rate = (auto_count / total * 100) if total > 0 else 0.0

    platform_map: dict[str, list] = {}
    for r in rows:
        platform_map.setdefault(r["platform"], []).append(r)

    summaries = []
    for name, items in platform_map.items():
        summaries.append(
            PlatformSummary(
                platform=name,
                comments_posted=len(items),
                avg_likes=0.0,
                sentiment_score=0.0,
                trending_status="green",
            )
        )

    return OverviewResponse(
        total_engagements=total,
        avg_engagement_rate=0.0,
        approval_rate=round(approval_rate, 1),
        active_platforms=active,
        platform_summaries=summaries,
    )


@router.get("/api/v1/dashboard/{platform}", response_model=PlatformStatsResponse)
async def platform_stats(
    platform: str,
    user: CurrentUser,
    timeframe: Timeframe = Query(Timeframe.day),
):
    if platform not in ("tiktok", "instagram", "x"):
        raise HTTPException(status_code=400, detail="Invalid platform")

    db = get_supabase_admin()
    since = _timeframe_start(timeframe)

    engagements = (
        db.table("engagements")
        .select("*")
        .eq("platform", platform)
        .gte("posted_at", since)
        .execute()
    )
    rows = engagements.data or []

    return PlatformStatsResponse(
        kpis={
            "comments_posted": len(rows),
            "total_likes": 0,
            "avg_likes": 0.0,
            "sentiment_score": 0.0,
        },
        category_breakdown=[],
        timeline_data=[],
        top_comments=rows[:10],
    )


@router.get("/api/v1/analytics/engagement-timeline", response_model=EngagementTimelineResponse)
async def engagement_timeline(
    user: CurrentUser,
    timeframe: Timeframe = Query(Timeframe.day),
    platform: str | None = Query(None),
):
    db = get_supabase_admin()
    since = _timeframe_start(timeframe)

    query = db.table("engagements").select("platform, posted_at").gte("posted_at", since)
    if platform:
        query = query.eq("platform", platform)
    result = query.order("posted_at").execute()

    points = [
        EngagementTimelinePoint(
            timestamp=r["posted_at"],
            comments_posted=1,
            engagement_rate=0.0,
            platform=r.get("platform"),
        )
        for r in (result.data or [])
    ]
    return EngagementTimelineResponse(data_points=points)


@router.get("/api/v1/analytics/hashtag-performance", response_model=HashtagPerformanceResponse)
async def hashtag_performance(user: CurrentUser):
    db = get_supabase_admin()
    videos = db.table("discovered_videos").select("hashtags").not_.is_("hashtags", "null").execute()

    tag_counts: dict[str, int] = {}
    for v in videos.data or []:
        for tag in v.get("hashtags") or []:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    hashtags = [
        HashtagPerformance(tag=tag, comment_count=count)
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:50]
    ]
    return HashtagPerformanceResponse(hashtags=hashtags)
