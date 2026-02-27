"""
Overview dashboard showing CashKitty's performance metrics.
Shows our comments and their engagement across all platforms.
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
    """
    Dashboard overview showing CashKitty's performance.
    
    Shows metrics for OUR comments across all platforms:
    - Total comments posted by CashKitty
    - Total likes our comments received
    - Total replies to our comments
    - Posts we're tracking (discovered content)
    """
    db = get_supabase_admin()
    since = _timeframe_start(timeframe)

    # Get OUR engagements (CashKitty's comments)
    try:
        engagements = (
            db.table("engagements")
            .select("id, platform, posted_at, comment_text")
            .gte("posted_at", since)
            .eq("status", "posted")
            .execute()
        )
        our_comments = engagements.data or []
    except Exception as e:
        print(f"Error fetching engagements: {e}")
        our_comments = []
    
    # Get engagement metrics for OUR comments
    total_likes_on_our_comments = 0
    total_replies_to_our_comments = 0
    
    try:
        if our_comments:
            engagement_ids = [e["id"] for e in our_comments]
            metrics = (
                db.table("engagement_metrics")
                .select("likes, replies")
                .execute()
            )
            for m in (metrics.data or []):
                total_likes_on_our_comments += m.get("likes", 0)
                total_replies_to_our_comments += m.get("replies", 0)
    except Exception as e:
        print(f"Error fetching engagement metrics: {e}")
    
    # Get discovered posts (content we're tracking)
    try:
        discovered = (
            db.table("discovered_videos")
            .select("id, platform, created_at")
            .execute()
        )
        tracked_posts = discovered.data or []
    except Exception as e:
        print(f"Error fetching discovered posts: {e}")
        tracked_posts = []
    
    # Count active/connected platforms
    try:
        platforms_resp = db.table("platforms").select("name, status").execute()
        active = sum(1 for p in (platforms_resp.data or []) if p.get("status") == "connected")
    except Exception:
        active = 0
        
    # Review queue count
    try:
        review_resp = db.table("review_queue").select("id").is_("decision", "null").execute()
        pending_reviews = len(review_resp.data or [])
    except Exception:
        pending_reviews = 0

    # Stats cards - CashKitty's Performance
    total_comments_posted = len(our_comments)
    
    stats = [
        {
            "title": "Comments Posted",
            "value": str(total_comments_posted),
            "trend": f"By CashKitty",
            "trendUp": True,
            "icon": "chat",
            "color": "bg-[#1DA1F2]",
            "progress": min(total_comments_posted * 10, 100),
        },
        {
            "title": "Likes Received",
            "value": f"{total_likes_on_our_comments:,}",
            "trend": f"On our comments",
            "trendUp": True,
            "icon": "favorite",
            "color": "bg-[#E91E63]",
            "progress": min(total_likes_on_our_comments // 10, 100),
        },
        {
            "title": "Replies Received",
            "value": f"{total_replies_to_our_comments:,}",
            "trend": f"To our comments",
            "trendUp": True,
            "icon": "reply",
            "color": "bg-[#10B981]",
            "progress": min(total_replies_to_our_comments * 5, 100),
        },
        {
            "title": "Pending Reviews",
            "value": str(pending_reviews),
            "trend": "Needs attention" if pending_reviews > 0 else "All clear",
            "trendUp": False,
            "icon": "rate_review",
            "color": "bg-[#F59E0B]",
            "progress": min(pending_reviews * 20, 100),
        },
    ]

    # Platform health cards
    platform_health = []
    
    # Group comments by platform
    comments_by_platform = {}
    for comment in our_comments:
        platform = comment.get("platform", "unknown")
        comments_by_platform[platform] = comments_by_platform.get(platform, 0) + 1
    
    # Group tracked posts by platform
    tracked_by_platform = {}
    for post in tracked_posts:
        platform = post.get("platform", "unknown")
        tracked_by_platform[platform] = tracked_by_platform.get(platform, 0) + 1
    
    for key in ("tiktok", "instagram", "x"):
        meta = _PLATFORM_META[key]
        
        # Check if platform is connected
        try:
            platform_status = db.table("platforms").select("status").eq("name", key).execute()
            connected = platform_status.data and platform_status.data[0].get("status") == "connected"
        except:
            connected = False
        
        comments_count = comments_by_platform.get(key, 0)
        tracked_count = tracked_by_platform.get(key, 0)
        
        platform_health.append(
            {
                **meta,
                "statusColor": "bg-[#10B981]" if connected else "bg-gray-500",
                "stat1Lbl": "Comments Posted",
                "stat1Val": str(comments_count),
                "stat2Lbl": "Posts Tracked",
                "stat2Val": str(tracked_count),
            }
        )

    # Chart data - comments posted over time
    chart = []
    if our_comments:
        # Group by 3-hour buckets
        buckets = [0] * 8
        for comment in our_comments:
            posted_at = comment.get("posted_at")
            if posted_at:
                try:
                    dt = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                    hours_ago = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
                    bucket_idx = min(int(hours_ago / 3), 7)
                    buckets[bucket_idx] += 1
                except:
                    pass
        
        for i in range(8):
            chart.append({
                "time": f"{(7-i) * 3}h ago",
                "comments": buckets[7-i],
            })
    else:
        for i in range(8):
            chart.append({"time": f"{(7-i) * 3}h ago", "comments": 0})

    return {
        "stats": stats,
        "platformHealth": platform_health,
        "chart": chart,
        "total_comments_posted": total_comments_posted,
        "total_likes_received": total_likes_on_our_comments,
        "total_replies_received": total_replies_to_our_comments,
        "posts_tracked": len(tracked_posts),
        "active_platforms": active,
        "pending_reviews": pending_reviews,
    }
