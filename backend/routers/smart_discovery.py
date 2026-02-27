"""
Smart Discovery endpoint for X/Twitter Hub.
User provides context/keywords → GenClaw discovers + analyzes posts → Returns recommendations.

GenClaw acts as intelligent layer:
- Understands natural language queries
- Extracts optimal keywords
- Provides contextual analysis
"""

import logging
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from db.connection import get_supabase_admin
from services.twitter_discovery import TwitterDiscoveryService
from services.intelligent_query import process_user_query_with_neoclaw, generate_response_summary
from services.context_engine_loader import AGENT_TRUST_HUB_CONTEXT

logger = logging.getLogger(__name__)
router = APIRouter(tags=["hubs"])


# Context is now loaded from Jen Context Engine files


def determine_min_engagement_from_context(query: str) -> int:
    """
    INTELLIGENT LAYER: GenClaw determines optimal min_engagement based on user context.
    
    Logic:
    - High-authority figures (Karpathy, Musk, etc.): 500+ likes (viral potential)
    - Security/breaking news: 200+ likes (timely, important)
    - Product discussions: 100+ likes (engaged community)
    - General topics: 50+ likes (active conversation)
    - Niche/specific: 20+ likes (quality over quantity)
    """
    query_lower = query.lower()
    
    # High-authority keywords (want viral posts)
    high_authority_keywords = ['karpathy', 'musk', 'altman', 'yann lecun', 'demis hassabis']
    if any(keyword in query_lower for keyword in high_authority_keywords):
        return 500
    
    # Breaking news / urgent (want high visibility)
    urgent_keywords = ['breaking', 'security nightmare', 'hacked', 'breach', 'vulnerability', 'exploit']
    if any(keyword in query_lower for keyword in urgent_keywords):
        return 200
    
    # Product/skill discussions (engaged community)
    product_keywords = ['openclaw', 'skills', 'marketplace', 'agent trust hub', 'plugins']
    if any(keyword in query_lower for keyword in product_keywords):
        return 100
    
    # Niche/specific topics (quality over quantity)
    if len(query.split()) > 10:  # Detailed context = niche
        return 20
    
    # Default: moderate engagement
    return 50


class SmartDiscoveryRequest(BaseModel):
    """User input for smart discovery."""
    query: str = Field(..., description="Context describing what posts to find", min_length=3, max_length=500)
    max_results: Optional[int] = Field(10, description="Maximum posts to analyze", ge=1, le=25)
    generate_suggestions: Optional[bool] = Field(False, description="Generate suggested responses for top posts")


class PostAnalysis(BaseModel):
    """AI analysis of a discovered post."""
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
    
    # Analysis fields
    relevance_score: float = Field(..., ge=0, le=10, description="How relevant to Agent Trust Hub (0-10)")
    engagement_potential: float = Field(..., ge=0, le=10, description="Potential for high engagement (0-10)")
    persona_recommendation: str = Field(..., description="Observer/Advisor/Connector")
    risk_level: str = Field(..., description="Green/Yellow/Red")
    angle_summary: str = Field(..., description="What angle would we take?")
    recommendation_score: float = Field(..., ge=0, le=10, description="Overall recommendation (0-10)")
    reasoning: str = Field(..., description="Why this score?")
    
    # Suggested response (optional)
    suggested_comment: Optional[dict] = Field(None, description="AI-generated suggested response")


class SmartDiscoveryResponse(BaseModel):
    """Results from smart discovery with GenClaw analysis."""
    query: str
    found_posts: int
    analyzed_posts: int
    recommendations: list[PostAnalysis]
    top_post: Optional[PostAnalysis] = None
    
    # GenClaw intelligent layer
    extracted_keywords: Optional[str] = None
    search_strategy: Optional[str] = None
    context_summary: Optional[str] = None


@router.post("/api/v1/hubs/x/smart-discovery")
async def smart_discovery(request: SmartDiscoveryRequest) -> SmartDiscoveryResponse:
    """
    Smart Discovery with GenClaw Intelligence.
    
    Flow:
    1. GenClaw analyzes user query and extracts optimal keywords
    2. GenClaw determines search strategy based on Agent Trust Hub context
    3. Search Twitter API with extracted keywords
    4. Analyze each post for relevance
    5. GenClaw generates contextual summary of results
    6. Return ranked recommendations with GenClaw insights
    """
    
    # STEP 1: GenClaw Intelligence Layer
    logger.info(f"GenClaw analyzing query: {request.query}")
    
    try:
        query_analysis = await process_user_query_with_neoclaw(
            user_input=request.query,
            context_docs=AGENT_TRUST_HUB_CONTEXT
        )
        
        extracted_keywords = query_analysis.get("extracted_keywords", request.query)
        logger.info(f"GenClaw extracted keywords: {extracted_keywords}")
        logger.info(f"GenClaw strategy: {query_analysis.get('search_strategy')}")
        
    except Exception as e:
        logger.warning(f"GenClaw analysis failed, using fallback: {e}")
        extracted_keywords = request.query
        query_analysis = {
            "extracted_keywords": extracted_keywords,
            "search_strategy": "Basic keyword search",
            "relevance_criteria": "Posts matching keywords"
        }
    
    # STEP 2: Determine min_engagement
    min_engagement = determine_min_engagement_from_context(extracted_keywords)
    logger.info(f"GenClaw determined min_engagement={min_engagement} for keywords: {extracted_keywords}")
    
    # STEP 3: Discover posts via Twitter API
    twitter_service = TwitterDiscoveryService()
    
    try:
        discovered_posts = await twitter_service.discover_by_query(
            query=extracted_keywords,
            max_results=request.max_results,
            min_engagement=min_engagement
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
            top_post=None,
            extracted_keywords=extracted_keywords,
            search_strategy=query_analysis.get("search_strategy"),
            context_summary="No posts found matching these keywords. Try broader search terms."
        )
    
    # STEP 4: Analyze each post
    analyzed_posts = []
    
    for post in discovered_posts:
        try:
            analysis = await analyze_post_for_recommendation(post)
            analyzed_posts.append(analysis)
        except Exception as e:
            logger.warning(f"Analysis failed for post {post.get('id')}: {e}")
            continue
    
    # STEP 5: Sort by recommendation_score
    analyzed_posts.sort(key=lambda x: x.recommendation_score, reverse=True)
    
    # STEP 5.5: Generate suggested responses for top posts (if requested)
    if request.generate_suggestions:
        from services.response_generator import generate_suggested_response
        
        logger.info("Generating suggested responses for top 3 posts...")
        for i, post_analysis in enumerate(analyzed_posts[:3]):  # Only top 3
            try:
                suggestion = await generate_suggested_response(
                    post={
                        "author": post_analysis.author,
                        "text": post_analysis.text,
                        "likes": post_analysis.likes,
                        "retweets": post_analysis.retweets
                    },
                    persona=post_analysis.persona_recommendation,
                    context_docs=AGENT_TRUST_HUB_CONTEXT
                )
                
                if suggestion and suggestion.get("confidence", 0) >= 0.6:
                    post_analysis.suggested_comment = suggestion
                    logger.info(f"Generated suggestion for post {i+1}: confidence={suggestion.get('confidence')}")
                else:
                    logger.warning(f"Low confidence suggestion for post {i+1}, skipping")
                    
            except Exception as e:
                logger.warning(f"Failed to generate suggestion for post {i+1}: {e}")
    
    # STEP 6: GenClaw generates contextual summary
    try:
        context_summary = await generate_response_summary(
            user_query=request.query,
            found_posts=[{
                "author": p.author,
                "text": p.text,
                "likes": p.likes,
                "url": p.url
            } for p in analyzed_posts[:5]],
            analysis=query_analysis,
            context_docs=AGENT_TRUST_HUB_CONTEXT
        )
    except Exception as e:
        logger.warning(f"GenClaw summary generation failed: {e}")
        context_summary = f"Found {len(analyzed_posts)} relevant posts about {extracted_keywords}."
    
    # STEP 7: Store top posts
    db = get_supabase_admin()
    for analysis in analyzed_posts[:5]:
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
                "hashtags": [request.query],
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to store post {analysis.post_id}: {e}")
    
    return SmartDiscoveryResponse(
        query=request.query,
        found_posts=len(discovered_posts),
        analyzed_posts=len(analyzed_posts),
        recommendations=analyzed_posts,
        top_post=analyzed_posts[0] if analyzed_posts else None,
        extracted_keywords=extracted_keywords,
        search_strategy=query_analysis.get("search_strategy"),
        context_summary=context_summary
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
        quotes=post.get("quotes", 0),
        bookmarks=post.get("bookmarks", 0),
        impressions=post.get("impressions", 0),
        relevance_score=relevance_score,
        engagement_potential=engagement_score,
        persona_recommendation=persona,
        risk_level=risk_level,
        angle_summary=angle,
        recommendation_score=recommendation_score,
        reasoning=reasoning,
    )
