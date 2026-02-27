"""Live Twitter discovery endpoint."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx
import os
from datetime import datetime, timezone
from backend.db.connection import get_supabase_admin

router = APIRouter(prefix="/api/v1/discovery", tags=["discovery"])


class DiscoveryRequest(BaseModel):
    query: str = "AI agent security"
    max_results: int = 20


class DiscoveryResponse(BaseModel):
    job_id: str
    status: str
    message: str


async def discover_tweets_background(query: str, max_results: int, job_id: str):
    """Background task to discover tweets."""
    db = get_supabase_admin()
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    
    try:
        # Update job status
        db.table("discovery_jobs").update({
            "status": "running",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", job_id).execute()
        
        # Call Twitter API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                params={
                    "query": f"{query} -is:retweet lang:en",
                    "max_results": max_results,
                    "tweet.fields": "created_at,public_metrics,author_id,text",
                    "user.fields": "name,username",
                    "expansions": "author_id",
                },
                headers={"Authorization": f"Bearer {bearer_token}"},
                timeout=30.0,
            )
            
            if response.status_code != 200:
                raise Exception(f"Twitter API error: {response.status_code}")
            
            data = response.json()
            tweets = data.get("data", [])
            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
            
            # Store discovered tweets in database
            discovered_count = 0
            for tweet in tweets:
                author_id = tweet.get("author_id")
                author = users.get(author_id, {})
                metrics = tweet.get("public_metrics", {})
                
                record = {
                    "platform": "x",
                    "post_id": tweet["id"],
                    "post_url": f"https://twitter.com/{author.get('username', 'i')}/status/{tweet['id']}",
                    "post_text": tweet.get("text", ""),
                    "author_username": author.get("username", "unknown"),
                    "author_name": author.get("name", "Unknown"),
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "status": "discovered",
                    "discovered_at": tweet.get("created_at", datetime.now(timezone.utc).isoformat()),
                    "job_id": job_id
                }
                
                db.table("discovered_posts").upsert(record, on_conflict="post_id").execute()
                discovered_count += 1
            
            # Update job status
            db.table("discovery_jobs").update({
                "status": "completed",
                "posts_found": discovered_count,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", job_id).execute()
            
    except Exception as e:
        # Update job with error
        db.table("discovery_jobs").update({
            "status": "failed",
            "error_message": str(e),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", job_id).execute()


@router.post("/start", response_model=DiscoveryResponse)
async def start_discovery(
    request: DiscoveryRequest,
    background_tasks: BackgroundTasks
):
    """Start Twitter discovery job."""
    db = get_supabase_admin()
    
    # Create job record
    job_data = {
        "query": request.query,
        "max_results": request.max_results,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = db.table("discovery_jobs").insert(job_data).execute()
    job_id = result.data[0]["id"]
    
    # Start background task
    background_tasks.add_task(
        discover_tweets_background,
        request.query,
        request.max_results,
        job_id
    )
    
    return DiscoveryResponse(
        job_id=str(job_id),
        status="pending",
        message=f"Discovery started for query: {request.query}"
    )


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get discovery job status."""
    db = get_supabase_admin()
    
    result = db.table("discovery_jobs").select("*").eq("id", job_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return result.data


@router.get("/posts")
async def get_discovered_posts(
    status: str = "discovered",
    limit: int = 50
):
    """Get discovered posts."""
    db = get_supabase_admin()
    
    query = db.table("discovered_posts").select("*")
    
    if status:
        query = query.eq("status", status)
    
    result = query.order("discovered_at", desc=True).limit(limit).execute()
    
    return result.data or []
