"""
Intelligent Twitter discovery using AI agent + Twitter API.
Fetches real data on-demand and stores persistently.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import httpx
import json
import re
from datetime import datetime, timezone

from db.connection import get_supabase_admin, is_postgres_mode, get_db_info

router = APIRouter(prefix="/api/v1/agent", tags=["intelligent-agent"])


class SmartDiscoveryRequest(BaseModel):
    query: str = "personal finance OR money tips OR budgeting"
    min_engagement: int = 50
    max_results: int = 20
    auto_populate_hub: bool = True


@router.get("/db-status")
async def get_database_status():
    """Check database type and status."""
    return get_db_info()


@router.post("/discover-smart")
async def discover_smart(request: SmartDiscoveryRequest):
    """
    Intelligent discovery: AI agent fetches high-engagement posts from Twitter.
    
    This is the main endpoint for the intelligent layer.
    The agent:
    1. Connects to Twitter API
    2. Finds high-engagement posts matching your query
    3. Stores in persistent database (PostgreSQL)
    4. Returns data for frontend display
    
    No manual steps needed - just call this endpoint!
    """
    
    # Check database
    db_info = get_db_info()
    if not is_postgres_mode():
        return {
            "success": False,
            "error": "PostgreSQL not configured",
            "message": "Add Railway PostgreSQL plugin first",
            "instructions": "Railway Dashboard → Add → PostgreSQL → Restart service",
            "current_db": db_info
        }
    
    # Get Twitter credentials
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise HTTPException(status_code=500, detail="TWITTER_BEARER_TOKEN not set")
    
    try:
        # Fetch from Twitter API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                params={
                    "query": f"{request.query} -is:retweet lang:en",
                    "max_results": min(request.max_results, 100),
                    "tweet.fields": "created_at,public_metrics,author_id,text",
                    "user.fields": "name,username,verified,public_metrics",
                    "expansions": "author_id",
                    "sort_order": "relevancy"
                },
                headers={"Authorization": f"Bearer {bearer_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, 
                                  detail=f"Twitter API error: {response.text}")
            
            data = response.json()
            tweets = data.get("data", [])
            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
        
        # Filter for high engagement
        high_engagement = []
        for tweet in tweets:
            metrics = tweet.get("public_metrics", {})
            likes = metrics.get("like_count", 0)
            retweets = metrics.get("retweet_count", 0)
            
            if likes >= request.min_engagement or retweets >= 20:
                author_id = tweet.get("author_id")
                author = users.get(author_id, {})
                
                high_engagement.append({
                    "id": tweet["id"],
                    "text": tweet.get("text", ""),
                    "author_username": author.get("username", "unknown"),
                    "author_name": author.get("name", "Unknown"),
                    "likes": likes,
                    "retweets": retweets,
                    "replies": metrics.get("reply_count", 0),
                    "url": f"https://twitter.com/{author.get('username', 'i')}/status/{tweet['id']}"
                })
        
        if not high_engagement:
            return {
                "success": False,
                "message": f"No tweets found with {request.min_engagement}+ likes",
                "suggestion": "Try lower min_engagement or different query",
                "found": len(tweets),
                "filtered": 0
            }
        
        # Store in database (PostgreSQL - persistent!)
        db = get_supabase_admin()
        stored_count = 0
        
        for tweet in high_engagement:
            # Extract hashtags
            hashtags = re.findall(r'#\w+', tweet["text"])
            if not hashtags:
                hashtags = ["#finance", "#money"]
            
            record = {
                "platform": "x",
                "video_url": tweet["url"],
                "creator": f"@{tweet['author_username']}",
                "description": tweet["text"][:500],
                "hashtags": json.dumps(hashtags),
                "likes": tweet["likes"],
                "status": "discovered",
                "engaged": 0
            }
            
            try:
                # Check if exists
                existing = db.table("discovered_videos").select("id").eq("video_url", tweet["url"]).execute()
                if existing.data:
                    db.table("discovered_videos").update(record).eq("video_url", tweet["url"]).execute()
                else:
                    db.table("discovered_videos").insert(record).execute()
                stored_count += 1
            except Exception as e:
                print(f"Error storing tweet: {e}")
        
        return {
            "success": True,
            "message": f"Agent discovered {stored_count} high-engagement posts from Twitter",
            "query": request.query,
            "min_engagement": request.min_engagement,
            "found": len(tweets),
            "filtered": len(high_engagement),
            "stored": stored_count,
            "database": "PostgreSQL (persistent)",
            "top_posts": high_engagement[:5]  # Preview
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")


@router.post("/auto-refresh")
async def auto_refresh_dashboard():
    """
    Auto-refresh: Agent automatically fetches latest high-engagement posts.
    Call this from a cron job or frontend refresh button.
    """
    # Use default search for financial content
    result = await discover_smart(SmartDiscoveryRequest(
        query="personal finance OR money tips OR budgeting OR investing",
        min_engagement=100,
        max_results=15
    ))
    
    return {
        **result,
        "auto_refresh": True,
        "message": "Dashboard auto-refreshed with latest Twitter data"
    }
