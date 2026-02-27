"""
Working endpoint to populate Hub with real high-engagement Twitter posts.
This endpoint:
1. Discovers tweets from Twitter API
2. Filters for high engagement (likes, retweets)
3. Populates discovered_videos table correctly
4. Shows in frontend queue
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import os
import json
import re

from db.connection import get_supabase_admin

router = APIRouter(prefix="/api/v1/twitter", tags=["twitter-live"])


async def fetch_high_engagement_tweets(query: str, min_likes: int = 100, max_results: int = 20):
    """Fetch high-engagement tweets from Twitter API."""
    import httpx
    
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise Exception("TWITTER_BEARER_TOKEN not set")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            "https://api.twitter.com/2/tweets/search/recent",
            params={
                "query": f"{query} -is:retweet lang:en",
                "max_results": max_results,
                "tweet.fields": "created_at,public_metrics,author_id,text",
                "user.fields": "name,username,verified,public_metrics",
                "expansions": "author_id",
                "sort_order": "relevancy"  # Get most relevant first
            },
            headers={"Authorization": f"Bearer {bearer_token}"},
        )
        
        if response.status_code != 200:
            raise Exception(f"Twitter API error: {response.status_code} - {response.text}")
        
        data = response.json()
        tweets = data.get("data", [])
        users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
        
        # Filter for high engagement
        high_engagement_tweets = []
        for tweet in tweets:
            metrics = tweet.get("public_metrics", {})
            likes = metrics.get("like_count", 0)
            retweets = metrics.get("retweet_count", 0)
            
            # Only include tweets with decent engagement
            if likes >= min_likes or retweets >= 20:
                author_id = tweet.get("author_id")
                author = users.get(author_id, {})
                
                high_engagement_tweets.append({
                    "id": tweet["id"],
                    "text": tweet.get("text", ""),
                    "author_username": author.get("username", "unknown"),
                    "author_name": author.get("name", "Unknown"),
                    "author_verified": author.get("verified", False),
                    "author_followers": author.get("public_metrics", {}).get("followers_count", 0),
                    "likes": likes,
                    "retweets": retweets,
                    "replies": metrics.get("reply_count", 0),
                    "created_at": tweet.get("created_at"),
                    "url": f"https://twitter.com/{author.get('username', 'i')}/status/{tweet['id']}"
                })
        
        return high_engagement_tweets


@router.post("/discover-top-posts")
async def discover_top_posts(
    query: str = "personal finance OR money tips OR budgeting",
    min_likes: int = 50,
    max_results: int = 20
):
    """
    Discover high-engagement posts from Twitter and populate Hub.
    
    This endpoint:
    1. Searches Twitter for relevant posts
    2. Filters for posts with min_likes or 20+ retweets
    3. Stores in discovered_videos (what Hub reads)
    4. Returns list of discovered posts
    """
    try:
        # Fetch high-engagement tweets
        tweets = await fetch_high_engagement_tweets(query, min_likes, max_results)
        
        if not tweets:
            return {
                "success": False,
                "message": f"No tweets found with {min_likes}+ likes. Try lowering min_likes or different query."
            }
        
        db = get_supabase_admin()
        stored_count = 0
        
        for tweet in tweets:
            # Extract hashtags
            hashtags = re.findall(r'#\w+', tweet["text"])
            if not hashtags:
                if "finance" in tweet["text"].lower() or "money" in tweet["text"].lower():
                    hashtags = ["#personalfinance", "#money"]
                else:
                    hashtags = ["#trending"]
            
            # Prepare record
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
            
            # Insert or update
            try:
                existing = db.table("discovered_videos").select("id").eq("video_url", tweet["url"]).execute()
                if existing.data:
                    db.table("discovered_videos").update(record).eq("video_url", tweet["url"]).execute()
                else:
                    db.table("discovered_videos").insert(record).execute()
                stored_count += 1
            except Exception as e:
                print(f"Error storing tweet {tweet['id']}: {e}")
        
        return {
            "success": True,
            "found": len(tweets),
            "stored": stored_count,
            "query": query,
            "min_likes": min_likes,
            "top_posts": tweets[:5]  # Return top 5 as preview
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")


@router.get("/top-posts")
async def get_top_posts(limit: int = 20):
    """Get discovered high-engagement posts."""
    db = get_supabase_admin()
    
    # Get posts sorted by likes
    result = db.table("discovered_videos").select("*").eq("platform", "x").order("likes", desc=True).limit(limit).execute()
    
    return {
        "count": len(result.data or []),
        "posts": result.data or []
    }
