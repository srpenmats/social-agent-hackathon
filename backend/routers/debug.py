"""
Diagnostic endpoint to debug Overview data issues.
"""

from fastapi import APIRouter
from db.connection import get_supabase_admin
import json

router = APIRouter(prefix="/api/v1/debug", tags=["debug"])


@router.get("/discovered-posts")
async def get_discovered_posts():
    """Check what's in discovered_videos table."""
    db = get_supabase_admin()
    
    try:
        # Get all X platform posts
        posts = db.table("discovered_videos").select("*").eq("platform", "x").limit(5).execute()
        
        return {
            "success": True,
            "count": len(posts.data or []),
            "sample": posts.data[:5] if posts.data else [],
            "columns": list(posts.data[0].keys()) if posts.data else []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/overview-query")
async def test_overview_query():
    """Test the exact query Overview uses."""
    db = get_supabase_admin()
    
    try:
        # Same query as Overview
        discovered = (
            db.table("discovered_videos")
            .select("id, platform, likes, comments, shares, views, hashtags, created_at")
            .eq("platform", "x")
            .execute()
        )
        posts = discovered.data or []
        
        total_likes = sum(p.get("likes", 0) for p in posts)
        total_comments = sum(p.get("comments", 0) for p in posts)
        total_shares = sum(p.get("shares", 0) for p in posts)
        
        return {
            "success": True,
            "total_posts": len(posts),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "sample": posts[:3] if posts else []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
