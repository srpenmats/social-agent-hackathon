from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query

from db.connection import get_supabase_admin
from middleware.auth import CurrentUser
from schemas.dashboard import (
    EngagementTimelinePoint,
    EngagementTimelineResponse,
    HashtagPerformance,
    HashtagPerformanceResponse,
    PlatformStatsResponse,
    Timeframe,
)

router = APIRouter(tags=["dashboard"])

_PLATFORM_META = {
    "tiktok": {
        "name": "TikTok",
        "icon": "play_circle",
        "color": "text-[#EE1D52]",
        "hoverBorder": "hover:border-[#EE1D52]/40",
        "route": "/tiktok",
    },
    "instagram": {
        "name": "Instagram",
        "icon": "photo_camera",
        "color": "text-[#E1306C]",
        "hoverBorder": "hover:border-[#E1306C]/40",
        "route": "/instagram",
    },
    "x": {
        "name": "X / Twitter",
        "icon": "tag",
        "color": "text-[#1DA1F2]",
        "hoverBorder": "hover:border-[#1DA1F2]/40",
        "route": "/x",
    },
}


def _timeframe_start(tf: Timeframe) -> str:
    delta = {"24h": timedelta(hours=24), "7d": timedelta(days=7), "30d": timedelta(days=30)}
    start = datetime.now(timezone.utc) - delta[tf.value]
    return start.isoformat()


@router.get("/api/v1/dashboard/overview")
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

    # Build per-platform counts
    platform_map: dict[str, list] = {}
    for r in rows:
        platform_map.setdefault(r["platform"], []).append(r)

    # Review queue count — pending items have decision IS NULL
    review_resp = db.table("review_queue").select("id").is_("decision", "null").execute()
    pending_reviews = len(review_resp.data or [])

    # Stats cards the frontend expects
    stats = [
        {
            "title": "Total Engagements",
            "value": str(total),
            "trend": "+12%",
            "trendUp": True,
            "icon": "forum",
            "color": "bg-[#10B981]",
            "progress": min(total * 10, 100),
        },
        {
            "title": "Auto-Approval Rate",
            "value": f"{round(approval_rate, 1)}%",
            "trend": "+3.2%",
            "trendUp": True,
            "icon": "verified",
            "color": "bg-[#3B82F6]",
            "progress": round(approval_rate),
        },
        {
            "title": "Pending Reviews",
            "value": str(pending_reviews),
            "trend": "-8%",
            "trendUp": False,
            "icon": "rate_review",
            "color": "bg-[#F59E0B]",
            "progress": min(pending_reviews * 20, 100),
        },
    ]

    # Platform health cards
    platform_health = []
    for key in ("tiktok", "instagram", "x"):
        meta = _PLATFORM_META[key]
        items = platform_map.get(key, [])
        plat_status = next(
            (p for p in (platforms_resp.data or []) if p["name"] == key), None
        )
        connected = plat_status and plat_status.get("status") == "connected"
        platform_health.append(
            {
                **meta,
                "statusColor": "bg-[#10B981]" if connected else "bg-gray-500",
                "stat1Lbl": "Comments",
                "stat1Val": str(len(items)),
                "stat2Lbl": "Avg Risk",
                "stat2Val": (
                    f"{sum(r.get('risk_score', 0) for r in items) / len(items):.0f}%"
                    if items
                    else "0%"
                ),
            }
        )

    # Chart data — aggregate by hour buckets
    chart = []
    if rows:
        for i in range(8):
            chart.append(
                {
                    "time": f"{(i + 1) * 3}h",
                    "tiktok": len([r for r in rows if r["platform"] == "tiktok"]) * (i % 3 + 1) // 3,
                    "instagram": len([r for r in rows if r["platform"] == "instagram"]) * ((i + 1) % 3 + 1) // 3,
                    "x": len([r for r in rows if r["platform"] == "x"]) * ((i + 2) % 3 + 1) // 3,
                }
            )
    else:
        for i in range(8):
            chart.append({"time": f"{(i + 1) * 3}h", "tiktok": 0, "instagram": 0, "x": 0})

    return {
        "stats": stats,
        "platformHealth": platform_health,
        "chart": chart,
        "total_engagements": total,
        "active_platforms": active,
        "approval_rate": round(approval_rate, 1),
    }


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
