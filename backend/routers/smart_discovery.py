"""
Smart Discovery endpoint for X/Twitter Hub.
User provides context/keywords → GenClaw discovers + analyzes posts → Returns recommendations.
"""

import logging
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from db.connection import get_supabase_admin
from services.twitter_discovery import TwitterDiscoveryService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["hubs"])


class SmartDiscoveryRequest(BaseModel):
    """User input for smart discovery."""
    query: str = Field(..., description="Keywords or context to search for", min_length=3, max_length=200)
    min_engagement: Optional[int] = Field(100, description="Minimum likes for quality posts", ge=10)
    max_results: Optional[int] = Field(10, description="Maximum posts to analyze", ge=1, le=25)


class PostAnalysis(BaseModel):
    """AI analysis of a discovered post."""
    post_id: str
    author: str
    text: str
    url: str
    likes: int
    retweets: int
    replies: int
    
    # Analysis fields
    relevance_score: float = Field(..., ge=0, le=10, description="How relevant to Agent Trust Hub (0-10)")
    engagement_potential: float = Field(..., ge=0, le=10, description="Potential for high engagement (0-10)")
    persona_recommendation: str = Field(..., description="Observer/Advisor/Connector")
    risk_level: str = Field(..., description="Green/Yellow/Red")
    angle_summary: str = Field(..., description="What angle would we take?")
    recommendation_score: float = Field(..., ge=0, le=10, description="Overall recommendation (0-10)")
    reasoning: str = Field(..., description="Why this score?")


class SmartDiscoveryResponse(BaseModel):
    """Results from smart discovery."""
    query: str
    found_posts: int
    analyzed_posts: int
    recommendations: list[PostAnalysis]
    top_post: Optional[PostAnalysis] = None


@router.post("/api/v1/hubs/x/smart-discovery")
async def smart_discovery(request: SmartDiscoveryRequest) -> SmartDiscoveryResponse:
    """
    Smart Discovery: User provides keywords/context, GenClaw discovers + analyzes posts.
    
    Flow:
    1. Search Twitter API with user's query
    2. Filter by min_engagement
    3. For each post, run Jen-style analysis:
       - Relevance to Agent Trust Hub
       - Engagement potential
       - Recommended persona
       - Risk level
       - Angle we'd take
       - Overall recommendation score (0-10)
    4. Return ranked recommendations
    """
    
    # Step 1: Discover posts via Twitter API
    twitter_service = TwitterDiscoveryService()
    
    try:
        discovered_posts = await twitter_service.discover_by_query(
            query=request.query,
            max_results=request.max_results,
            min_engagement=request.min_engagement
        )
    except Exception as e:
        logger.error(f"Twitter discovery failed: {e}")
        raise HTTPException(status_code=500, detail=f"Twitter API error: {str(e)}")
    
    if not discovered_posts:
        return SmartDiscoveryResponse(
            query=request.query,
            found_posts=0,
            analyzed_posts=0,
            recommendations=[],
            top_post=None
        )
    
    # Step 2: Analyze each post with GenClaw
    analyzed_posts = []
    
    for post in discovered_posts:
        try:
            analysis = await analyze_post_for_recommendation(post)
            analyzed_posts.append(analysis)
        except Exception as e:
            logger.warning(f"Analysis failed for post {post.get('id')}: {e}")
            continue
    
    # Step 3: Sort by recommendation_score (highest first)
    analyzed_posts.sort(key=lambda x: x.recommendation_score, reverse=True)
    
    # Step 4: Store top posts in discovered_videos for tracking
    db = get_supabase_admin()
    for analysis in analyzed_posts[:5]:  # Store top 5
        try:
            db.table("discovered_videos").insert({
                "platform": "x",
                "video_id": analysis.post_id,
                "video_url": analysis.url,
                "creator": analysis.author,
                "description": analysis.text[:500],
                "likes": analysis.likes,
                "comments": analysis.replies,
                "shares": analysis.retweets,
                "engagement_score": int(analysis.recommendation_score * 10),
                "hashtags": [request.query],  # Track search query
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to store post {analysis.post_id}: {e}")
    
    return SmartDiscoveryResponse(
        query=request.query,
        found_posts=len(discovered_posts),
        analyzed_posts=len(analyzed_posts),
        recommendations=analyzed_posts,
        top_post=analyzed_posts[0] if analyzed_posts else None
    )


async def analyze_post_for_recommendation(post: dict) -> PostAnalysis:
    """
    Analyze a post using Jen Context Engine logic (simplified).
    
    Returns recommendation score 0-10 based on:
    - Relevance to Agent Trust Hub (does post mention AI agents, security, OpenClaw, skills?)
    - Engagement potential (likes, retweets, author followers)
    - Risk level (controversial topics, high-profile authors)
    """
    
    text = post.get("text", "").lower()
    author = post.get("author_username", "")
    likes = post.get("likes", 0)
    retweets = post.get("retweets", 0)
    replies = post.get("replies", 0)
    
    # Relevance scoring (0-10)
    relevance_keywords = {
        "openclaw": 3.0,
        "ai agent": 2.5,
        "autonomous": 2.0,
        "security": 2.0,
        "malicious": 2.5,
        "skill": 1.5,
        "plugin": 1.5,
        "vulnerability": 2.0,
        "threat": 1.5,
        "trust": 1.0,
        "agentic": 2.0,
    }
    
    relevance_score = 0.0
    for keyword, weight in relevance_keywords.items():
        if keyword in text:
            relevance_score += weight
    
    relevance_score = min(relevance_score, 10.0)
    
    # Engagement potential (0-10)
    # Based on current engagement + conversation activity
    engagement_score = min(
        (likes / 200) * 3 +  # Up to 3 points for likes
        (retweets / 50) * 2 +  # Up to 2 points for retweets
        (replies / 20) * 5,  # Up to 5 points for active discussion
        10.0
    )
    
    # Persona recommendation
    if relevance_score >= 7:
        persona = "Advisor"  # High relevance = security expertise needed
    elif relevance_score >= 4:
        persona = "Connector"  # Medium relevance = solution mention
    else:
        persona = "Observer"  # Low relevance = data sharing
    
    # Risk level
    high_risk_keywords = ["karpathy", "musk", "altman", "controversy", "lawsuit", "breach"]
    has_high_risk = any(keyword in text for keyword in high_risk_keywords)
    
    if has_high_risk or likes > 5000:
        risk_level = "Yellow"  # High-profile needs review
    elif relevance_score < 3:
        risk_level = "Red"  # Not relevant enough
    else:
        risk_level = "Green"  # Safe to engage
    
    # Angle summary
    if "openclaw" in text and "security" in text:
        angle = "Validate security concerns with Gen research (15% malicious skills)"
    elif "ai agent" in text and any(word in text for word in ["skill", "plugin", "tool"]):
        angle = "Mention Agent Trust Hub Scanner (free pre-install verification)"
    elif "autonomous" in text or "agentic" in text:
        angle = "Discuss OWASP LLM risks (supply chain, agency)"
    else:
        angle = "General security perspective with industry context"
    
    # Overall recommendation score (0-10)
    # Formula: (relevance * 0.5) + (engagement * 0.3) + (risk_factor * 0.2)
    risk_factor = {"Green": 10, "Yellow": 6, "Red": 2}[risk_level]
    recommendation_score = (
        relevance_score * 0.5 +
        engagement_score * 0.3 +
        risk_factor * 0.2
    )
    
    # Reasoning
    reasoning_parts = []
    reasoning_parts.append(f"Relevance: {relevance_score:.1f}/10")
    reasoning_parts.append(f"Engagement: {engagement_score:.1f}/10")
    reasoning_parts.append(f"Risk: {risk_level}")
    
    if relevance_score >= 7:
        reasoning_parts.append("High relevance to Agent Trust Hub")
    if engagement_score >= 7:
        reasoning_parts.append("Strong engagement potential")
    if risk_level == "Yellow":
        reasoning_parts.append("Needs human review (high-profile)")
    
    reasoning = " | ".join(reasoning_parts)
    
    return PostAnalysis(
        post_id=post.get("id", ""),
        author=author,
        text=post.get("text", ""),
        url=post.get("url", ""),
        likes=likes,
        retweets=retweets,
        replies=replies,
        relevance_score=relevance_score,
        engagement_potential=engagement_score,
        persona_recommendation=persona,
        risk_level=risk_level,
        angle_summary=angle,
        recommendation_score=recommendation_score,
        reasoning=reasoning,
    )
