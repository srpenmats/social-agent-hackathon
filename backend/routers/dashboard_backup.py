"""
Enhanced dashboard with real Twitter engagement metrics.
Shows actual post engagement (likes, retweets) from discovered tweets.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Query
from db.connection import get_supabase_admin
from schemas.dashboard import Timeframe
import json

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
    timeframe: Timeframe = Query(Timeframe.day),
):
    """Dashboard overview with real Twitter engagement metrics."""
    db = get_supabase_admin()
    since = _timeframe_start(timeframe)

    # Get discovered posts (real Twitter data)
    try:
        discovered = (
            db.table("discovered_videos")
            .select("id, platform, likes, hashtags, created_at")
            .eq("platform", "x")
            .gte("created_at", since)
            .execute()
        )
        posts = discovered.data or []
    except Exception as e:
        print(f"Error fetching discovered posts: {e}")
        posts = []
    
    # Get engagements (our responses)
    try:
        engagements = (
            db.table("engagements")
            .select("id, platform, risk_score, approval_path, posted_at")
            .gte("posted_at", since)
            .execute()
        )
        rows = engagements.data or []
    except Exception as e:
        print(f"Error fetching engagements: {e}")
        rows = []
    
    # Calculate real Twitter metrics
    total_posts = len(posts)
    total_likes = sum(p.get("likes", 0) for p in posts)
    avg_likes = round(total_likes / total_posts) if total_posts > 0 else 0
    
    # Extract hashtags
    all_hashtags = []
    for p in posts:
        hashtags_str = p.get("hashtags", "[]")
        try:
            if isinstance(hashtags_str, str):
                hashtags = json.loads(hashtags_str)
            else:
                hashtags = hashtags_str
            all_hashtags.extend(hashtags)
        except:
            pass
    
    unique_hashtags = len(set(all_hashtags))
    
    # Engagement stats
    total_engagements = len(rows)
    auto_count = sum(1 for r in rows if r.get("approval_path") == "auto")
    approval_rate = (auto_count / total_engagements * 100) if total_engagements > 0 else 0.0

    # Check platforms - handle if table doesn't exist
    try:
        platforms_resp = db.table("platforms").select("name, status").execute()
        active = sum(1 for p in (platforms_resp.data or []) if p.get("status") == "connected")
    except Exception:
        # Default to X active if we have discovered posts
        active = 1 if total_posts > 0 else 0
        
    # Build per-platform counts
    platform_map: dict[str, list] = {}
    for r in rows:
        platform_map.setdefault(r.get("platform", "unknown"), []).append(r)

    # Review queue count
    try:
        review_resp = db.table("review_queue").select("id").is_("decision", "null").execute()
        pending_reviews = len(review_resp.data or [])
    except Exception:
        pending_reviews = 0

    # Stats cards with REAL Twitter metrics
    stats = [
        {
            "title": "Total Discovered Posts",
            "value": str(total_posts),
            "trend": f"{total_likes:,} total likes",
            "trendUp": True,
            "icon": "analytics",
            "color": "bg-[#1DA1F2]",
            "progress": min(total_posts * 5, 100),
        },
        {
            "title": "Avg Post Engagement",
            "value": f"{avg_likes:,}",
            "trend": f"{unique_hashtags} hashtags tracked",
            "trendUp": True,
            "icon": "favorite",
            "color": "bg-[#10B981]",
            "progress": min(avg_likes // 10, 100),
        },
        {
            "title": "Comments Posted",
            "value": str(total_engagements),
            "trend": f"{round(approval_rate, 1)}% auto-approved",
            "trendUp": True,
            "icon": "forum",
            "color": "bg-[#3B82F6]",
            "progress": min(total_engagements * 20, 100),
        },
        {
            "title": "Pending Reviews",
            "value": str(pending_reviews),
            "trend": "Needs attention",
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
        
        # X is connected if we have discovered posts
        connected = key == "x" and total_posts > 0
        
        # Real metrics for X
        if key == "x" and total_posts > 0:
            platform_health.append(
                {
                    **meta,
                    "statusColor": "bg-[#10B981]",
                    "stat1Lbl": "Discovered Posts",
                    "stat1Val": str(total_posts),
                    "stat2Lbl": "Avg Likes",
                    "stat2Val": f"{avg_likes:,}",
                }
            )
        else:
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

    # Chart data - show discovered posts over time
    chart = []
    if posts:
        # Group by 3-hour buckets
        buckets = [0] * 8
        for post in posts:
            created_at = post.get("created_at")
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    hours_ago = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
                    bucket_idx = min(int(hours_ago / 3), 7)
                    buckets[bucket_idx] += 1
                except:
                    pass
        
        for i in range(8):
            chart.append({
                "time": f"{(7-i) * 3}h ago",
                "tiktok": 0,
                "instagram": 0,
                "x": buckets[7-i],
            })
    else:
        for i in range(8):
            chart.append({"time": f"{(7-i) * 3}h ago", "tiktok": 0, "instagram": 0, "x": 0})

    return {
        "stats": stats,
        "platformHealth": platform_health,
        "chart": chart,
        "total_engagements": total_engagements,
        "total_discovered": total_posts,
        "total_likes": total_likes,
        "avg_likes": avg_likes,
        "unique_hashtags": unique_hashtags,
        "active_platforms": active,
        "approval_rate": round(approval_rate, 1),
    }
