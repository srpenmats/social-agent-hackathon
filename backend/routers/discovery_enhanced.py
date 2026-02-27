"""
Enhanced discovery router with real Twitter integration and comment generation.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os

from services.twitter_discovery import get_twitter_service
from db.connection import get_supabase_admin

router = APIRouter(prefix="/api/v1/discovery", tags=["discovery"])


# ============================================================================
# Request/Response Models
# ============================================================================

class TwitterSearchRequest(BaseModel):
    query: str = "AI agent security"
    max_results: int = 20
    context: Optional[str] = None  # e.g., "cybersecurity", "finance"


class CommentGenerationRequest(BaseModel):
    post_id: str
    tweet_text: str
    author_username: str
    num_candidates: int = 3
    tone: str = "professional"  # professional, casual, technical, humorous


# ============================================================================
# Twitter Discovery Endpoints
# ============================================================================

@router.post("/twitter/search")
async def search_twitter(request: TwitterSearchRequest):
    """
    Search Twitter for relevant posts based on query and context.
    Stores results in discovered_posts table.
    
    Example:
        POST /api/v1/discovery/twitter/search
        {
            "query": "AI agent security",
            "max_results": 20,
            "context": "cybersecurity"
        }
    """
    try:
        twitter_service = get_twitter_service()
        result = await twitter_service.discover_and_store(
            query=request.query,
            max_results=request.max_results,
            context=request.context
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")


@router.get("/twitter/posts")
async def get_discovered_posts(
    status: str = "discovered",
    limit: int = 50,
    min_score: Optional[int] = None
):
    """
    Get discovered Twitter posts.
    
    Query params:
        status: Filter by status (discovered, scored, reviewed, posted)
        limit: Max number of posts to return
        min_score: Filter by minimum engagement score
    """
    db = get_supabase_admin()
    
    query = db.table("discovered_posts").select("*").eq("platform", "x")
    
    if status:
        query = query.eq("status", status)
    
    result = query.order("discovered_at", desc=True).limit(limit).execute()
    posts = result.data or []
    
    # Calculate engagement scores if requested
    if min_score is not None:
        twitter_service = get_twitter_service()
        scored_posts = []
        for post in posts:
            score = twitter_service.score_engagement_potential(post)
            if score >= min_score:
                post["engagement_score"] = score
                scored_posts.append(post)
        return scored_posts
    
    return posts


@router.get("/twitter/thread/{tweet_id}")
async def get_thread_context(tweet_id: str):
    """
    Get full conversation thread for a tweet.
    Useful for understanding context before generating a reply.
    """
    try:
        twitter_service = get_twitter_service()
        thread = await twitter_service.get_thread_context(tweet_id)
        return {
            "tweet_id": tweet_id,
            "thread_length": len(thread),
            "thread": thread
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Comment Generation (AI-powered)
# ============================================================================

@router.post("/generate-comment")
async def generate_comment(request: CommentGenerationRequest):
    """
    Generate AI comment candidates for a discovered post.
    
    This uses Claude/GPT to generate contextually appropriate responses
    based on the tweet content, author, and your brand voice.
    
    Example:
        POST /api/v1/discovery/generate-comment
        {
            "post_id": "1234567890",
            "tweet_text": "Just discovered this amazing AI security framework!",
            "author_username": "tech_enthusiast",
            "num_candidates": 3,
            "tone": "professional"
        }
    """
    try:
        # Get thread context for better understanding
        twitter_service = get_twitter_service()
        thread = await twitter_service.get_thread_context(request.post_id)
        
        # Extract key topics
        topics = twitter_service.extract_key_topics(request.tweet_text)
        
        # Build context for AI generation
        context = {
            "original_tweet": request.tweet_text,
            "author": request.author_username,
            "thread_length": len(thread),
            "key_topics": topics,
            "tone": request.tone
        }
        
        # Generate comment candidates using AI
        # (This would call Claude/GPT API - simplified here)
        candidates = await _generate_ai_comments(context, request.num_candidates)
        
        # Store candidates in review_queue
        db = get_supabase_admin()
        
        # Get the discovered post record
        post_result = db.table("discovered_posts").select("id").eq("post_id", request.post_id).execute()
        if not post_result.data:
            raise HTTPException(status_code=404, detail="Post not found")
        
        video_id = post_result.data[0]["id"]
        
        # Store each candidate
        stored_candidates = []
        for candidate in candidates:
            record = {
                "video_id": video_id,
                "proposed_text": candidate["text"],
                "risk_score": candidate["risk_score"],
                "risk_reasoning": candidate["reasoning"],
                "classification": candidate["classification"],
                "confidence": candidate["confidence"],
                "queued_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = db.table("review_queue").insert(record).execute()
            stored_candidates.append(result.data[0])
        
        return {
            "success": True,
            "post_id": request.post_id,
            "candidates_generated": len(candidates),
            "candidates": stored_candidates
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


async def _generate_ai_comments(context: dict, num_candidates: int) -> List[dict]:
    """
    Generate AI-powered comment candidates.
    
    This is a simplified version - in production, this would call Claude/GPT API
    with proper prompts based on your brand voice and guidelines.
    """
    # For now, return template-based candidates
    # In production, replace with actual AI API calls
    
    tweet_text = context["original_tweet"]
    author = context["author"]
    topics = context["key_topics"]
    tone = context.get("tone", "professional")
    
    # Template candidates based on tone
    if tone == "professional":
        templates = [
            f"Great insights on {topics[0] if topics else 'this topic'}! We've been exploring similar approaches in our security research. Would love to hear more about your implementation.",
            f"This aligns perfectly with what we're seeing in the AI security space. Have you considered {topics[1] if len(topics) > 1 else 'additional safeguards'}?",
            f"Excellent thread @{author}. This is exactly the kind of conversation the industry needs around AI agent security."
        ]
    elif tone == "technical":
        templates = [
            f"Interesting approach. How are you handling authentication and authorization at the agent layer? We've found that traditional methods don't scale well.",
            f"Have you evaluated this against OWASP Top 10 for LLMs? Would be curious to see how it addresses prompt injection attacks.",
            f"The architecture looks solid. Are you using any specific frameworks for agent orchestration? We're seeing good results with LangChain Security."
        ]
    elif tone == "casual":
        templates = [
            f"This is fire 🔥 Been thinking about this exact problem. Your solution is clean!",
            f"ngl this is exactly what the AI security space needs rn. Nice work @{author}!",
            f"yo this actually slaps. Been wrestling with similar issues and this approach makes so much sense"
        ]
    else:  # humorous
        templates = [
            f"Finally! Someone who gets it. My AI agents have been running wild without proper security. They're basically cyberpunk cowboys at this point.",
            f"This tweet just fixed my entire threat model. My agents thank you (they told me to say that, I swear I'm still in control)",
            f"*frantically takes notes* My AI agents are currently held together with duct tape and prayers, so this is exactly what I needed"
        ]
    
    candidates = []
    for i, template in enumerate(templates[:num_candidates]):
        # Calculate risk score based on content
        risk_score = 15 if tone == "professional" else 25 if tone == "technical" else 35
        
        candidates.append({
            "text": template,
            "risk_score": risk_score + (i * 5),  # Vary scores slightly
            "reasoning": f"Low risk: {tone} tone, on-topic engagement, no controversial claims",
            "classification": "technical-discussion" if tone in ["professional", "technical"] else "casual-engagement",
            "confidence": 0.85 - (i * 0.05)  # First candidate highest confidence
        })
    
    return candidates


# ============================================================================
# Sync to Hub (Bridge discovered_posts → discovered_videos)
# ============================================================================

@router.post("/sync-to-hub")
async def sync_to_hub():
    """
    Sync discovered_posts to discovered_videos for Hub display.
    This bridges the discovery system with the dashboard UI.
    """
    try:
        db = get_supabase_admin()
        
        # Get unsynced posts
        posts = db.table("discovered_posts").select("*").eq("status", "discovered").execute()
        
        synced_count = 0
        for post in posts.data or []:
            # Extract hashtags
            import re
            text = post.get("post_text", "")
            hashtags = re.findall(r'#\w+', text)
            if not hashtags:
                hashtags = ["#AI", "#tech"]
            
            # Insert into discovered_videos
            import json
            video_record = {
                "platform": "x",
                "video_url": post["post_url"],
                "creator": f"@{post['author_username']}",
                "description": post["post_text"],
                "hashtags": json.dumps(hashtags),
                "likes": post.get("likes", 0),
                "comments": post.get("replies", 0),
                "shares": post.get("retweets", 0),
                "status": "discovered",
                "engaged": 0,
                "discovered_at": post.get("discovered_at"),
            }
            
            # Check if video already exists
            existing = db.table("discovered_videos").select("id").eq("video_url", video_record["video_url"]).execute()
            if existing.data:
                db.table("discovered_videos").update(video_record).eq("video_url", video_record["video_url"]).execute()
            else:
                db.table("discovered_videos").insert(video_record).execute()
            
            # Mark as synced
            db.table("discovered_posts").update({
                "status": "synced",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", post["id"]).execute()
            
            synced_count += 1
        
        return {
            "success": True,
            "synced_count": synced_count,
            "message": f"Synced {synced_count} posts to Hub"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


# ============================================================================
# Automated Discovery Workflow
# ============================================================================

@router.post("/auto-discover")
async def auto_discover(background_tasks: BackgroundTasks):
    """
    Automated discovery workflow:
    1. Search Twitter for relevant posts
    2. Score engagement potential
    3. Generate comment candidates for high-scoring posts
    4. Queue for human review
    
    This runs in the background and returns immediately.
    """
    background_tasks.add_task(_run_auto_discovery)
    
    return {
        "success": True,
        "message": "Auto-discovery started in background",
        "status": "running"
    }


async def _run_auto_discovery():
    """Background task for automated discovery."""
    try:
        twitter_service = get_twitter_service()
        
        # Define search queries
        queries = [
            {"query": "AI agent security", "context": "cybersecurity"},
            {"query": "autonomous agents", "context": "AI research"},
            {"query": "LLM security", "context": "AI safety"},
        ]
        
        all_posts = []
        for q in queries:
            result = await twitter_service.discover_and_store(
                query=q["query"],
                max_results=10,
                context=q.get("context")
            )
            all_posts.extend(result["tweets"])
        
        # Score and filter high-potential posts
        high_value_posts = []
        for post in all_posts:
            score = twitter_service.score_engagement_potential(post)
            if score >= 60:  # Only high-scoring posts
                post["engagement_score"] = score
                high_value_posts.append(post)
        
        # Generate comments for top posts
        for post in high_value_posts[:5]:  # Top 5 only
            await generate_comment(CommentGenerationRequest(
                post_id=post["id"],
                tweet_text=post["text"],
                author_username=post["author_username"],
                num_candidates=2,
                tone="professional"
            ))
        
        # Sync to hub
        await sync_to_hub()
        
        print(f"Auto-discovery complete: {len(all_posts)} posts found, {len(high_value_posts)} high-value")
        
    except Exception as e:
        print(f"Auto-discovery failed: {e}")
