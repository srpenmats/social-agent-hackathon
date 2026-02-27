"""
Jen endpoints for comment posting and management.
"""

import logging
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from services.twitter_discovery import TwitterDiscoveryService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["jen"])


class PostCommentRequest(BaseModel):
    """Request to post a comment."""
    tweet_id: str
    comment_text: str


class PostCommentResponse(BaseModel):
    """Response after posting a comment."""
    success: bool
    comment_id: str
    comment_url: str
    posted_at: str


@router.post("/api/v1/jen/post-comment", response_model=PostCommentResponse)
async def post_comment(request: PostCommentRequest):
    """
    Post Jen's comment to a tweet.
    
    This endpoint:
    1. Takes approved comment text
    2. Posts it as a reply via Twitter API
    3. Returns the posted comment URL
    """
    
    try:
        twitter = TwitterDiscoveryService()
        
        # Post the reply
        result = await twitter.post_reply(
            tweet_id=request.tweet_id,
            text=request.comment_text
        )
        
        return PostCommentResponse(
            success=True,
            comment_id=result["id"],
            comment_url=result["url"],
            posted_at=result.get("created_at", "")
        )
    
    except Exception as e:
        logger.error(f"Failed to post comment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to post comment: {str(e)}"
        )


@router.get("/api/v1/jen/verify-auth")
async def verify_auth():
    """
    Verify Twitter API authentication.
    
    Returns authentication status and user info.
    """
    
    try:
        twitter = TwitterDiscoveryService()
        result = await twitter.verify_credentials()
        return result
    
    except Exception as e:
        logger.error(f"Auth verification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Auth verification failed: {str(e)}"
        )


@router.get("/api/v1/jen/tweet-details/{tweet_id}")
async def get_tweet_details(tweet_id: str):
    """
    Get full details for a tweet including all metrics.
    
    Returns:
    - All engagement metrics (likes, RT, replies, quotes, bookmarks, impressions)
    - Author info
    - Direct URL
    """
    
    try:
        twitter = TwitterDiscoveryService()
        result = await twitter.get_tweet_details(tweet_id)
        return result
    
    except Exception as e:
        logger.error(f"Failed to get tweet details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tweet details: {str(e)}"
        )
