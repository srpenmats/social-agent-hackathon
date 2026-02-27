"""
Intelligent Query Processing Layer - GenClaw as the Smart Discovery Brain

GenClaw acts as the intelligent layer between user input and Twitter API:
1. Understands user intent from natural language
2. Extracts optimal Twitter search keywords
3. Analyzes results using Agent Trust Hub context
4. Generates contextual response explaining recommendations
"""

import os
import json
from typing import Dict, List, Optional


def create_condensed_context(full_context: str) -> str:
    """
    Create a condensed version of Jen context for Claude prompts.
    
    Extracts the most critical information:
    - Agent Trust Hub products (Scanner, Sage, Marketplace)
    - Key statistics (18K instances, 15% malicious rate)
    - Jen's personas (Observer, Advisor, Connector)
    - Core voice guidelines
    
    Target: ~8KB of dense, actionable context instead of 260KB full docs.
    """
    
    # For now, use the first ~8000 chars which prioritizes the soul document
    # (loaded first, contains densest info: identity, products, stats)
    # TODO: Could build smarter extraction if needed
    condensed = full_context[:8000]
    
    # Add explicit Agent Trust Hub summary if not prominent enough
    if "Agent Trust Hub" not in condensed[:2000]:
        ath_summary = """
AGENT TRUST HUB (Gen Digital):
- Products: Skills Scanner (free pre-install verification), Marketplace (curated audited skills), 
  Sage (runtime monitoring with 200+ rules), Vercel partnership (skills.sh for 6M developers)
- Key Stats: 18,000+ OpenClaw instances exposed, 15% malicious rate detected
- Mission: Build trust infrastructure for AI agents, prevent supply chain attacks
"""
        condensed = ath_summary + "\n\n" + condensed
    
    return condensed


async def process_user_query_with_neoclaw(user_input: str, context_docs: str) -> Dict:
    """
    Use GenClaw (via Claude) to intelligently process user query.
    
    Args:
        user_input: Natural language query from user
        context_docs: Agent Trust Hub context documentation (full 260KB)
        
    Returns:
        {
            "extracted_keywords": str,
            "search_strategy": str,
            "context_summary": str,
            "expected_results": str
        }
    """
    
    # Create condensed context for efficient prompting
    condensed_context = create_condensed_context(context_docs)
    
    prompt = f"""You are GenClaw, an AI agent expert helping Gen Digital find relevant social media conversations.

USER INPUT:
"{user_input}"

YOUR TASK:
Analyze this query and provide intelligent guidance for Twitter search.

CONTEXT ABOUT AGENT TRUST HUB & JEN:
{condensed_context}

RESPOND WITH JSON:
{{
    "extracted_keywords": "optimal Twitter search keywords (2-5 words max)",
    "search_strategy": "brief explanation of search approach",
    "relevance_criteria": "what makes a post relevant to this query",
    "engagement_context": "why engagement level matters for this query"
}}

EXAMPLES:

User: "Give me 10 top posts for AI Agent security"
Response: {{
    "extracted_keywords": "AI agent security",
    "search_strategy": "Focus on security vulnerabilities, supply chain risks, and trust issues in AI agents. Look for discussions about malicious skills or trust infrastructure.",
    "relevance_criteria": "Posts discussing security nightmares, malicious skills (15% malicious rate!), trust infrastructure, or OWASP LLM risks. Especially relevant when mentioning agent frameworks or skill marketplaces.",
    "engagement_context": "High engagement posts reach decision-makers and create conversation opportunities for Agent Trust Hub products (Scanner, Sage, Marketplace)"
}}

User: "Show me discussions about OpenClaw"
Response: {{
    "extracted_keywords": "OpenClaw",
    "search_strategy": "Find posts mentioning OpenClaw specifically - security concerns, usage, or integrations",
    "relevance_criteria": "Direct mentions of OpenClaw, especially related to skills, security, or agent frameworks. Relevant to our 18K+ exposed instances statistic.",
    "engagement_context": "Any engagement level valuable - even low-engagement posts from developers matter"
}}

NOW ANALYZE THE USER INPUT AND RESPOND WITH JSON ONLY:"""
    
    # Call Claude API (Bedrock)
    try:
        import anthropic
        
        client = anthropic.AnthropicBedrock(
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
        )
        
        message = client.messages.create(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON response
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        analysis = json.loads(response_text)
        
        return analysis
        
    except Exception as e:
        # Fallback to simple keyword extraction if Claude fails
        print(f"GenClaw analysis failed: {e}, using fallback")
        return {
            "extracted_keywords": extract_keywords_simple(user_input),
            "search_strategy": "Basic keyword search",
            "relevance_criteria": "Posts matching keywords",
            "engagement_context": "Standard engagement filtering"
        }


def extract_keywords_simple(query: str) -> str:
    """Fallback: Simple keyword extraction without AI."""
    conversational_patterns = [
        "give me", "show me", "find me", "search for", "looking for",
        "i want", "can you find", "get me", "top posts", "best posts",
    ]
    
    query_lower = query.lower()
    for pattern in conversational_patterns:
        if pattern in query_lower:
            query = query_lower.replace(pattern, "").strip()
            filler_words = ["the", "a", "an", "for", "about", "on", "posts", "post"]
            query_words = [w for w in query.split() if w not in filler_words and not w.isdigit()]
            return " ".join(query_words)
    
    return query


async def generate_response_summary(
    user_query: str,
    found_posts: List[Dict],
    analysis: Dict,
    context_docs: str
) -> str:
    """
    Use GenClaw to generate a contextual response explaining the results.
    
    Args:
        user_query: Original user query
        found_posts: Posts discovered from Twitter
        analysis: Query analysis from process_user_query_with_neoclaw
        context_docs: Agent Trust Hub context (full 260KB)
        
    Returns:
        Natural language summary explaining results and relevance
    """
    
    # Use condensed context for response generation too
    condensed_context = create_condensed_context(context_docs)
    
    # Prepare post summaries
    post_summaries = []
    for i, post in enumerate(found_posts[:5], 1):
        post_summaries.append(
            f"{i}. @{post.get('author')} ({post.get('likes', 0)} likes): "
            f"{post.get('text', '')[:100]}..."
        )
    
    posts_text = "\n".join(post_summaries)
    
    prompt = f"""You are GenClaw, providing intelligent social media guidance for Gen Digital.

USER ASKED:
"{user_query}"

WE SEARCHED FOR:
Keywords: "{analysis.get('extracted_keywords')}"
Strategy: {analysis.get('search_strategy')}

FOUND {len(found_posts)} POSTS:
{posts_text}

AGENT TRUST HUB CONTEXT:
{condensed_context[:4000]}

YOUR TASK:
Write a brief (2-3 sentences) contextual response explaining:
1. Why these posts are relevant to Gen Digital / Agent Trust Hub
2. What engagement opportunities they present
3. Which posts stand out most and why

Reference specific Agent Trust Hub products (Scanner, Sage, Marketplace) or statistics (18K instances, 15% malicious) when relevant.

TONE: Professional but conversational. Like a colleague giving strategic advice.

RESPONSE:"""
    
    try:
        import anthropic
        
        client = anthropic.AnthropicBedrock(
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
        )
        
        message = client.messages.create(
            model="us.anthropic.claude-sonnet-4-20250514-v1:0",
            max_tokens=512,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text.strip()
        
    except Exception as e:
        print(f"GenClaw response generation failed: {e}")
        return f"Found {len(found_posts)} posts matching '{analysis.get('extracted_keywords')}'. Top posts show strong engagement around {analysis.get('relevance_criteria')}."
