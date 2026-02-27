"""
Review Posts endpoints for Jen workflow.
"""

import logging
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from db.connection import get_supabase_admin

logger = logging.getLogger(__name__)
router = APIRouter(tags=["jen"])


class ReviewPostCreate(BaseModel):
    """Post to add to review queue."""
    post_id: str
    author: str
    text: str
    url: str
    likes: int
    retweets: int
    replies: int
    quotes: int = 0
    bookmarks: int = 0
    impressions: int = 0
    relevance_score: float
    engagement_potential: float
    persona_recommendation: str
    risk_level: str
    angle_summary: str
    recommendation_score: float
    reasoning: str


class ReviewPostResponse(BaseModel):
    """Review post with status."""
    id: str
    post_id: str
    author: str
    text: str
    url: str
    likes: int
    retweets: int
    replies: int
    quotes: int
    bookmarks: int
    impressions: int
    relevance_score: float
    engagement_potential: float
    persona_recommendation: str
    risk_level: str
    angle_summary: str
    recommendation_score: float
    status: str
    draft_comment: Optional[str]
    created_at: str


@router.post("/api/v1/jen/review-posts")
async def add_to_review_queue(post: ReviewPostCreate):
    """
    Add a post to the review queue.
    
    User clicks "Add to Review Queue" in Smart Discovery.
    Post is stored with status="pending".
    """
    
    db = get_supabase_admin()
    
    try:
        # Check if post already in queue
        existing = db.table("review_posts").select("id").eq("post_id", post.post_id).execute()
        if existing.data:
            return {"success": True, "message": "Post already in review queue", "exists": True}
        
        # Insert new review post
        record = {
            **post.dict(),
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = db.table("review_posts").insert(record).execute()
        
        return {
            "success": True,
            "message": "Added to review queue",
            "id": result.data[0]["id"] if result.data else None
        }
    
    except Exception as e:
        logger.error(f"Failed to add to review queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/jen/review-posts")
async def get_review_posts(status: str = "all"):
    """
    Get posts from review queue.
    
    Filter by status: all, pending, draft, approved
    """
    
    db = get_supabase_admin()
    
    try:
        query = db.table("review_posts").select("*").order("created_at", desc=True)
        
        if status != "all":
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {"posts": result.data}
    
    except Exception as e:
        logger.error(f"Failed to get review posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/v1/jen/review-posts/{post_id}/draft")
async def save_draft_comment(post_id: str, request: dict):
    """
    Save draft comment for a review post.
    
    Updates status to "draft" and stores the comment.
    """
    
    db = get_supabase_admin()
    comment = request.get("comment", "")
    
    try:
        result = db.table("review_posts").update({
            "draft_comment": comment,
            "status": "draft",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", post_id).execute()
        
        return {"success": True, "message": "Draft saved"}
    
    except Exception as e:
        logger.error(f"Failed to save draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/jen/review-posts/{post_id}/approve")
async def approve_and_post(post_id: str, request: dict):
    """
    Approve comment and post to Twitter.
    
    Updates status to "approved", marks as posted, and tracks response.
    """
    
    db = get_supabase_admin()
    comment = request.get("comment", "")
    
    try:
        # Get the post
        post_result = db.table("review_posts").select("*").eq("id", post_id).execute()
        if not post_result.data:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post = post_result.data[0]
        tweet_id = post["post_id"]
        
        # Post comment via Twitter API (using TwitterDiscoveryService)
        from services.twitter_discovery import TwitterDiscoveryService
        twitter = TwitterDiscoveryService()
        
        try:
            reply_result = await twitter.post_reply(tweet_id, comment)
            
            # Update with successful response tracking
            db.table("review_posts").update({
                "status": "approved",
                "final_comment": comment,
                "posted": True,
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "posted_url": reply_result.get("url"),
                "responded_at": datetime.now(timezone.utc).isoformat(),
                "response_text": comment,
                "response_url": reply_result.get("url")
            }).eq("id", post_id).execute()
            
            return {
                "success": True,
                "message": "Comment posted successfully",
                "url": reply_result.get("url")
            }
        
        except Exception as twitter_error:
            # Update status but mark as failed
            db.table("review_posts").update({
                "status": "failed",
                "posted": False,
                "error": str(twitter_error)
            }).eq("id", post_id).execute()
            
            raise HTTPException(
                status_code=500,
                detail=f"Failed to post comment: {str(twitter_error)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/v1/jen/review-posts/{post_id}")
async def remove_from_queue(post_id: str):
    """
    Remove a post from review queue.
    """
    
    db = get_supabase_admin()
    
    try:
        db.table("review_posts").delete().eq("id", post_id).execute()
        return {"success": True, "message": "Removed from queue"}
    
    except Exception as e:
        logger.error(f"Failed to remove post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/jen/response-queue")
async def get_response_queue(limit: int = 50):
    """
    Get posts we've responded to (Response Queue).
    
    Shows history of approved and posted comments.
    """
    
    db = get_supabase_admin()
    
    try:
        result = db.table("review_posts")\
            .select("*")\
            .eq("posted", True)\
            .order("responded_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return {"posts": result.data, "total": len(result.data)}
    
    except Exception as e:
        logger.error(f"Failed to get response queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))
