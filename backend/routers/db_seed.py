"""
Database initialization endpoint for Railway.
Populates the database with sample/seed data.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import json

from db.connection import get_supabase_admin

router = APIRouter(prefix="/api/v1/db", tags=["database"])


@router.post("/init-twitter-data")
async def initialize_twitter_data():
    """
    Initialize database with sample Twitter data.
    This populates discovered_videos, review_queue, and engagements tables.
    """
    db = get_supabase_admin()
    
    # Sample discovered videos (tweets)
    sample_videos = [
        {
            "platform": "x",
            "video_url": "https://twitter.com/mabele2003/status/123",
            "creator": "@mabele2003",
            "description": "Simple financial knowledge tip: It's small decisions that determine your financial future",
            "hashtags": json.dumps(["#finance", "#personalfinance", "#money"]),
            "likes": 1250,
            "comments": 89,
            "shares": 234,
            "status": "discovered",
            "engaged": 1,
        },
        {
            "platform": "x",
            "video_url": "https://twitter.com/techexpert/status/456",
            "creator": "@techexpert",
            "description": "Cloud security alliance just published an agentic trust framework. Zero trust for AI agents.",
            "hashtags": json.dumps(["#AI", "#security", "#agents"]),
            "likes": 2100,
            "comments": 145,
            "shares": 567,
            "status": "discovered",
            "engaged": 0,
        },
        {
            "platform": "x",
            "video_url": "https://twitter.com/devworld/status/789",
            "creator": "@devworld",
            "description": "Building autonomous agents with proper authentication is critical for enterprise deployment",
            "hashtags": json.dumps(["#agents", "#automation", "#security"]),
            "likes": 890,
            "comments": 67,
            "shares": 123,
            "status": "discovered",
            "engaged": 0,
        },
    ]
    
    video_ids = []
    for video in sample_videos:
        result = db.table("discovered_videos").insert(video).execute()
        if result.data:
            video_ids.append(result.data[0]["id"])
    
    # Sample pending drafts
    sample_drafts = [
        {
            "video_id": video_ids[0] if video_ids else None,
            "proposed_text": "ngl this is the financial literacy content we need more of. the kitty approves 🐱",
            "risk_score": 18,
            "risk_reasoning": "Low risk: supportive commentary on financial education content",
            "classification": "finance-educational",
            "queued_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "video_id": video_ids[1] if len(video_ids) > 1 else None,
            "proposed_text": "This aligns perfectly with what we're seeing in the AI security space. Have you considered additional safeguards?",
            "risk_score": 22,
            "risk_reasoning": "Low risk: professional technical discussion",
            "classification": "technical-security",
            "queued_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "video_id": video_ids[2] if len(video_ids) > 2 else None,
            "proposed_text": "the way this actually works tho. tried it last month and my systems said thank you",
            "risk_score": 35,
            "risk_reasoning": "Moderate risk: implies personal experience with solution",
            "classification": "technical-experience",
            "queued_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "video_id": video_ids[0] if video_ids else None,
            "proposed_text": "ok but why is nobody talking about this?? saving this for later fr",
            "risk_score": 12,
            "risk_reasoning": "Very low risk: casual engagement, no claims",
            "classification": "casual-engagement",
            "queued_at": datetime.now(timezone.utc).isoformat(),
        },
    ]
    
    for draft in sample_drafts:
        db.table("review_queue").insert(draft).execute()
    
    # Sample posted engagements
    sample_engagements = [
        {
            "platform": "x",
            "video_id": video_ids[0] if video_ids else None,
            "comment_text": "invest consistently assumes you have something left over to invest. the real challenge is getting to that point",
            "risk_score": 15,
            "approval_path": "auto",
            "posted_at": datetime.now(timezone.utc).isoformat(),
            "status": "posted",
        },
        {
            "platform": "x",
            "comment_text": "the small decisions matter. but the big ones like rent, student loans, healthcare - those eat up everything before you get to the 'small' stuff",
            "risk_score": 20,
            "approval_path": "auto",
            "posted_at": datetime.now(timezone.utc).isoformat(),
            "status": "posted",
        },
    ]
    
    eng_ids = []
    for eng in sample_engagements:
        result = db.table("engagements").insert(eng).execute()
        if result.data:
            eng_ids.append(result.data[0]["id"])
    
    # Add engagement metrics
    for eng_id in eng_ids:
        db.table("engagement_metrics").insert({
            "engagement_id": eng_id,
            "likes": 150,
            "replies": 23,
            "impressions": 2500,
        }).execute()
    
    return {
        "success": True,
        "message": "Database initialized with sample Twitter data",
        "stats": {
            "videos": len(sample_videos),
            "drafts": len(sample_drafts),
            "engagements": len(sample_engagements),
        }
    }


@router.post("/clear-twitter-data")
async def clear_twitter_data():
    """Clear all Twitter data from database (for testing)."""
    db = get_supabase_admin()
    
    # Clear in reverse order of dependencies
    db.table("engagement_metrics").delete().neq("id", 0).execute()
    db.table("engagements").delete().eq("platform", "x").execute()
    db.table("review_queue").delete().neq("id", 0).execute()
    db.table("discovered_videos").delete().eq("platform", "x").execute()
    
    return {
        "success": True,
        "message": "All Twitter data cleared"
    }
