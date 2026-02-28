"""
NeoClaw-powered Smart Discovery with async queue.
User submits query → Backend queues → NeoClaw processes → Frontend polls for results.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db.connection import get_supabase_admin

logger = logging.getLogger(__name__)
router = APIRouter(tags=["discovery", "neoclaw"])


# ==================== REQUEST/RESPONSE MODELS ====================

class SmartQueryRequest(BaseModel):
    """User query for smart discovery."""
    query: str = Field(..., description="Natural language description of what to find", min_length=3, max_length=500)
    max_results: Optional[int] = Field(10, description="Max posts to analyze", ge=5, le=25)


class QueryStatusResponse(BaseModel):
    """Status of a queued discovery request."""
    query_id: str
    status: str  # queued | processing | complete | error
    message: Optional[str] = None
    estimated_seconds: Optional[int] = None
    results: Optional[dict] = None
    error: Optional[str] = None


class PostAnalysis(BaseModel):
    """Single post analysis result."""
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


class DiscoveryResults(BaseModel):
    """Complete discovery results from NeoClaw."""
    query_id: str
    original_query: str
    search_strategy: str
    found_posts: int
    analyzed_posts: int
    recommendations: list[PostAnalysis]
    context_summary: str
    processed_by: str = "NeoClaw"
    processing_time_seconds: Optional[float] = None


# ==================== ENDPOINTS ====================

@router.post("/api/v1/discovery/smart-query")
async def submit_smart_query(request: SmartQueryRequest) -> QueryStatusResponse:
    """
    Submit a smart discovery query for NeoClaw processing.
    Returns immediately with query_id for polling.
    
    Flow:
    1. Store query in discovery_queue table
    2. Send message to NeoClaw via OpenClaw
    3. Return query_id for status polling
    """
    
    db = get_supabase_admin()
    query_id = str(uuid.uuid4())
    
    try:
        # Store in queue
        db.table("discovery_queue").insert({
            "query_id": query_id,
            "query_text": request.query,
            "max_results": request.max_results,
            "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        
        logger.info(f"✅ Queued discovery request {query_id}: {request.query}")
        
        # TODO: Send to NeoClaw via OpenClaw session messaging
        # For now, we'll rely on NeoClaw polling or webhook
        # await send_to_neoclaw(query_id, request.query, request.max_results)
        
        return QueryStatusResponse(
            query_id=query_id,
            status="queued",
            message="NeoClaw is preparing to analyze your query...",
            estimated_seconds=30
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to queue discovery: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to queue request: {str(e)}")


@router.get("/api/v1/discovery/status/{query_id}")
async def get_query_status(query_id: str) -> QueryStatusResponse:
    """
    Check status of a discovery query.
    Returns results when complete, status message while processing.
    """
    
    db = get_supabase_admin()
    
    try:
        # Check for completed results first
        result = db.table("discovery_results").select("*").eq("query_id", query_id).execute()
        
        if result.data:
            # Results ready!
            result_data = result.data[0]
            return QueryStatusResponse(
                query_id=query_id,
                status="complete",
                message="Analysis complete",
                results=result_data.get("results")
            )
        
        # Check queue status
        queue_item = db.table("discovery_queue").select("*").eq("query_id", query_id).execute()
        
        if not queue_item.data:
            raise HTTPException(status_code=404, detail="Query ID not found")
        
        queue_status = queue_item.data[0]
        status = queue_status.get("status", "queued")
        
        if status == "error":
            return QueryStatusResponse(
                query_id=query_id,
                status="error",
                error=queue_status.get("error_message", "Unknown error occurred")
            )
        
        # Still processing
        messages = {
            "queued": "Waiting for NeoClaw to pick up query...",
            "processing": "NeoClaw is analyzing posts with Jen context...",
        }
        
        return QueryStatusResponse(
            query_id=query_id,
            status=status,
            message=messages.get(status, "Processing..."),
            estimated_seconds=20 if status == "processing" else 30
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to check status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check status: {str(e)}")


@router.post("/api/v1/discovery/complete")
async def receive_neoclaw_results(results: DiscoveryResults):
    """
    NeoClaw posts results back to this endpoint when processing is complete.
    This is called BY NeoClaw, not by the frontend.
    """
    
    db = get_supabase_admin()
    
    try:
        # Store results
        db.table("discovery_results").insert({
            "query_id": results.query_id,
            "results": results.dict(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        
        # Update queue status
        db.table("discovery_queue").update({
            "status": "complete",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("query_id", results.query_id).execute()
        
        # Store individual posts in discovered_posts table
        for post in results.recommendations[:10]:  # Top 10
            try:
                db.table("discovered_posts").insert({
                    "platform": "x",
                    "post_id": post.post_id,
                    "post_url": post.url,
                    "post_text": post.text,
                    "author_username": post.author,
                    "likes": post.likes,
                    "retweets": post.retweets,
                    "replies": post.replies,
                    "quotes": post.quotes,
                    "bookmarks": post.bookmarks,
                    "impressions": post.impressions,
                    "status": "discovered",
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                }).execute()
            except Exception as e:
                # Duplicate post_id is OK (already discovered)
                logger.warning(f"Post {post.post_id} already exists: {e}")
        
        logger.info(f"✅ Stored results for query {results.query_id}: {results.analyzed_posts} posts")
        
        return {"success": True, "query_id": results.query_id}
        
    except Exception as e:
        logger.error(f"❌ Failed to store results: {e}")
        
        # Mark as error in queue
        try:
            db.table("discovery_queue").update({
                "status": "error",
                "error_message": str(e),
            }).eq("query_id", results.query_id).execute()
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Failed to store results: {str(e)}")


@router.get("/api/v1/discovery/queue")
async def get_pending_queries():
    """
    Get pending queries from the queue.
    Used by NeoClaw to poll for work.
    """
    
    db = get_supabase_admin()
    
    try:
        # Get queued items (oldest first)
        pending = db.table("discovery_queue")\
            .select("*")\
            .in_("status", ["queued", "processing"])\
            .order("created_at")\
            .limit(5)\
            .execute()
        
        return {
            "pending_count": len(pending.data),
            "queries": pending.data
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch queue: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch queue: {str(e)}")


@router.post("/api/v1/discovery/claim/{query_id}")
async def claim_query(query_id: str):
    """
    NeoClaw claims a query to prevent duplicate processing.
    Marks status as 'processing'.
    """
    
    db = get_supabase_admin()
    
    try:
        db.table("discovery_queue").update({
            "status": "processing",
            "processing_started_at": datetime.now(timezone.utc).isoformat(),
        }).eq("query_id", query_id).execute()
        
        logger.info(f"✅ Query {query_id} claimed for processing")
        
        return {"success": True, "query_id": query_id}
        
    except Exception as e:
        logger.error(f"❌ Failed to claim query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to claim query: {str(e)}")
