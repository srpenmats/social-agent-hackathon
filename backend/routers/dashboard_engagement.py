"""
Overview dashboard showing Twitter post engagement metrics.
Shows: Total Views, Comments, Likes, Shares from discovered Twitter posts.
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
    Dashboard overview showing Twitter post engagement metrics.
    
    Shows real engagement from discovered Twitter posts:
    - Total Views (if available from API)
    - Total Comments/Replies
    - Total Likes
    - Total Shares/Retweets
    """
    db = get_supabase_admin()
    since = _timeframe_start(timeframe)

    # Get discovered posts (real Twitter data)
    try:
        discovered = (
            db.table("discovered_videos")
            .select("id, platform, likes, comments, shares, views, hashtags, created_at")
            .eq("platform", "x")
            .gte("created_at", since)
            .execute()
        )
        posts = discovered.data or []
    except Exception as e:
        print(f"Error fetching discovered posts: {e}")
        posts = []
    
    # Calculate Twitter engagement metrics
    total_posts = len(posts)
    total_likes = sum(p.get("likes", 0) for p in posts)
    total_comments = sum(p.get("comments", 0) for p in posts)  # Twitter replies
    total_shares = sum(p.get("shares", 0) for p in posts)      # Twitter retweets
    total_views = sum(p.get("views", 0) for p in posts)        # Views (if available)
    
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
    
    # Count active platforms (platforms with discovered posts)
    try:
        # Check all platforms for discovered content
        all_platforms = db.table("discovered_videos").select("platform").execute()
        active_platforms_set = set(p.get("platform") for p in (all_platforms.data or []) if p.get("platform"))
        active = len(active_platforms_set)
    except:
        active = 1 if total_posts > 0 else 0
        
    # Review queue count
    try:
        review_resp = db.table("review_queue").select("id").is_("decision", "null").execute()
        pending_reviews = len(review_resp.data or [])
    except Exception:
        pending_reviews = 0

    # Stats cards with Twitter engagement metrics
    stats = [
        {
            "title": "Total Likes",
            "value": f"{total_likes:,}",
            "trend": f"Across {total_posts} posts",
            "trendUp": True,
            "icon": "favorite",
            "color": "bg-[#E91E63]",
            "progress": min(total_likes // 100, 100),
        },
        {
            "title": "Total Comments/Replies",
            "value": f"{total_comments:,}",
            "trend": f"Avg {total_comments // total_posts if total_posts > 0 else 0} per post",
            "trendUp": True,
            "icon": "chat_bubble",
            "color": "bg-[#1DA1F2]",
            "progress": min(total_comments // 10, 100),
        },
        {
            "title": "Total Shares/Retweets",
            "value": f"{total_shares:,}",
            "trend": f"{unique_hashtags} unique hashtags",
            "trendUp": True,
            "icon": "share",
            "color": "bg-[#10B981]",
            "progress": min(total_shares // 20, 100),
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
    for key in ("tiktok", "instagram", "x"):
        meta = _PLATFORM_META[key]
        
        # X is connected if we have discovered posts
        connected = key == "x" and total_posts > 0
        
        # Real metrics for X
        if key == "x" and total_posts > 0:
            platform_health.append(
                {
                    **meta,
                    "statusColor": "bg-[#10B981]",
                    "stat1Lbl": "Posts Tracked",
                    "stat1Val": str(total_posts),
                    "stat2Lbl": "Total Engagement",
                    "stat2Val": f"{total_likes + total_comments + total_shares:,}",
                }
            )
        else:
            platform_health.append(
                {
                    **meta,
                    "statusColor": "bg-gray-500",
                    "stat1Lbl": "Posts",
                    "stat1Val": "0",
                    "stat2Lbl": "Engagement",
                    "stat2Val": "0",
                }
            )

    # Chart data - show engagement over time
    chart = []
    if posts:
        # Group by 3-hour buckets
        buckets = [{"likes": 0, "comments": 0, "shares": 0} for _ in range(8)]
        for post in posts:
            created_at = post.get("created_at")
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    hours_ago = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
                    bucket_idx = min(int(hours_ago / 3), 7)
                    buckets[bucket_idx]["likes"] += post.get("likes", 0)
                    buckets[bucket_idx]["comments"] += post.get("comments", 0)
                    buckets[bucket_idx]["shares"] += post.get("shares", 0)
                except:
                    pass
        
        for i in range(8):
            chart.append({
                "time": f"{(7-i) * 3}h ago",
                "likes": buckets[7-i]["likes"],
                "comments": buckets[7-i]["comments"],
                "shares": buckets[7-i]["shares"],
            })
    else:
        for i in range(8):
            chart.append({"time": f"{(7-i) * 3}h ago", "likes": 0, "comments": 0, "shares": 0})

    return {
        "stats": stats,
        "platformHealth": platform_health,
        "chart": chart,
        "total_posts": total_posts,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "total_views": total_views,
        "unique_hashtags": unique_hashtags,
        "active_platforms": active,
    }
