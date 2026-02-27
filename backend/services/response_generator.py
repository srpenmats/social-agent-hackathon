"""
Jen Response Generator - Context-Aware Comment Generation

Generates comments for social media posts using:
- Jen's voice guidelines and persona rules
- Agent Trust Hub knowledge and statistics
- Post-specific context and angle
- Pre-post checklist validation
"""

import os
import json
from typing import Dict, Optional, List


async def generate_suggested_response(
    post: Dict,
    persona: str,
    context_docs: str,
    condensed_context: str = None
) -> Optional[Dict]:
    """
    Generate a suggested comment for a post using Jen's voice and context.
    
    Args:
        post: Post data including text, author, metrics
        persona: Recommended persona (Observer/Advisor/Connector)
        context_docs: Full Jen context (260KB)
        condensed_context: Pre-condensed context (8KB) - optional
        
    Returns:
        {
            "comment": str,
            "persona_used": str,
            "angle": str,
            "voice_checks": dict,
            "char_count": int,
            "confidence": float
        }
        or None if generation fails
    """
    
    # Use provided condensed context or create it
    if not condensed_context:
        from services.intelligent_query import create_condensed_context
        condensed_context = create_condensed_context(context_docs)
    
    # Extract Jen voice rules from context
    voice_rules = extract_voice_rules(condensed_context)
    persona_guidelines = extract_persona_guidelines(condensed_context, persona)
    
    prompt = f"""You are Jen, a practitioner in late 20s to mid-30s working on AI agent security at Gen Digital.

POST TO RESPOND TO:
Author: @{post.get('author')}
Text: "{post.get('text')}"
Engagement: {post.get('likes', 0)} likes, {post.get('retweets', 0)} RTs

YOUR CONTEXT & KNOWLEDGE:
{condensed_context[:6000]}

VOICE RULES:
{voice_rules}

PERSONA FOR THIS POST: {persona}
{persona_guidelines}

PRE-POST CHECKLIST (your response MUST pass):
1. Specific to THIS post (not generic template)
2. Adds value (insight, perspective, or question)
3. Human voice (casual delivery, no corporate speak)
4. Short (under 280 chars, ideally <200)
5. Natural fit (flows with conversation)
6. No unsolicited advice (unless Advisor mode)
7. No product mentions unless earned (Connector only, if truly relevant)
8. Not preachy or lecturing
9. Acknowledges uncertainty where appropriate
10. Would a real builder actually say this?

TASK:
Generate ONE comment that:
- Reacts to this specific post
- Follows Jen's voice
- Uses {persona} persona appropriately
- Passes ALL checklist items
- Is under 280 characters

EXAMPLES:

Observer mode:
"yeah we've been tracking this pattern too. the detection challenge isn't the tech, it's doing it at scale without false positives 🤔"

Advisor mode (when they're asking for help):
"depends on your threat model. if you're worried about supply chain attacks, pre-install verification catches most of it. runtime monitoring is the hard part"

Connector mode (ONLY if post specifically mentions our space):
"this aligns with what we're seeing at Gen - 15% malicious rate across 18K instances. Scanner helps with the pre-install verification piece"

RESPOND WITH JSON:
{{
    "comment": "your generated comment here",
    "angle": "brief explanation of angle taken",
    "reasoning": "why this approach fits the post"
}}

GENERATE NOW:"""
    
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
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        # Validate the comment
        comment = result.get("comment", "")
        validation = validate_comment(comment, post, persona)
        
        return {
            "comment": comment,
            "persona_used": persona,
            "angle": result.get("angle", ""),
            "voice_checks": validation["checks"],
            "char_count": len(comment),
            "confidence": validation["confidence"],
            "reasoning": result.get("reasoning", "")
        }
        
    except Exception as e:
        print(f"Response generation failed: {e}")
        return None


def extract_voice_rules(context: str) -> str:
    """Extract key voice rules from Jen context."""
    # Look for voice rules section or use defaults
    if "voice" in context.lower() and "casual" in context.lower():
        # Try to extract voice section
        lines = context.split('\n')
        voice_section = []
        in_voice = False
        for line in lines:
            if 'voice' in line.lower() and ('rule' in line.lower() or 'guideline' in line.lower()):
                in_voice = True
            if in_voice:
                voice_section.append(line)
                if len(voice_section) > 20:  # Limit size
                    break
        if voice_section:
            return '\n'.join(voice_section)
    
    # Default voice rules
    return """
- Casual delivery, technical substance
- Short over long (ideally <200 chars)
- Specific over generic (reference actual content)
- Experience-based framing ("we've seen..." not "best practice is...")
- Direct but not harsh
- No corporate speak ever
- No marketing language
- No condescension
- No empty enthusiasm
"""


def extract_persona_guidelines(context: str, persona: str) -> str:
    """Extract persona-specific guidelines."""
    
    guidelines = {
        "Observer": """
Observer Mode Rules:
- React as peer, not expert
- No product mentions (stay neutral)
- No unsolicited advice
- Keep it shortest of all modes
- Share experience or ask genuine question
- "yeah", "the thing here is...", "curious about..."
""",
        "Advisor": """
Advisor Mode Rules:
- Help from experience (they're asking)
- Ask for context before advising
- Offer perspectives, not prescriptions
- Can be longer than Observer
- No product mentions unless genuinely relevant
- "depends on...", "one thing to watch for...", "in our experience..."
""",
        "Connector": """
Connector Mode Rules:
- Like Advisor but can mention Gen Digital's work
- ONLY if post is directly relevant to our space
- Value must exist without product mention
- Be transparent about connection
- Reference specific products (Scanner, Sage, Marketplace) or statistics (18K instances, 15% malicious)
- "this aligns with what we're seeing at Gen...", "we've built..."
"""
    }
    
    return guidelines.get(persona, guidelines["Observer"])


def validate_comment(comment: str, post: Dict, persona: str) -> Dict:
    """
    Validate comment against Jen's pre-post checklist.
    
    Returns confidence score (0-1) and check results.
    """
    checks = {}
    
    # 1. Specific to post
    post_words = set(post.get('text', '').lower().split())
    comment_words = set(comment.lower().split())
    common_words = post_words.intersection(comment_words)
    checks["specific"] = len(common_words) > 2
    
    # 2. Adds value (not just "great post")
    filler_phrases = ["great post", "nice work", "good point", "thanks for sharing", "interesting"]
    checks["adds_value"] = not any(phrase in comment.lower() for phrase in filler_phrases)
    
    # 3. Human voice (no corporate speak)
    corporate_speak = ["excited to", "great question", "let me explain", "happy to help", "reach out", "ecosystem"]
    checks["human_voice"] = not any(phrase in comment.lower() for phrase in corporate_speak)
    
    # 4. Short enough
    checks["short"] = len(comment) <= 280
    
    # 5. No unsolicited advice (unless Advisor)
    advice_words = ["should", "must", "need to", "have to", "you need"]
    has_advice = any(word in comment.lower() for word in advice_words)
    checks["no_unsolicited_advice"] = not has_advice or persona == "Advisor"
    
    # 6. No product spam (unless Connector and relevant)
    products = ["scanner", "sage", "marketplace"]
    has_product = any(prod in comment.lower() for prod in products)
    checks["no_spam"] = not has_product or persona == "Connector"
    
    # 7. Not preachy
    preachy_words = ["actually", "simply", "just", "obviously", "clearly"]
    checks["not_preachy"] = not any(word in comment.lower() for word in preachy_words)
    
    # Calculate confidence
    passed = sum(1 for v in checks.values() if v)
    confidence = passed / len(checks)
    
    return {
        "checks": checks,
        "confidence": confidence
    }


async def generate_multiple_options(
    post: Dict,
    persona: str,
    context_docs: str,
    num_options: int = 3
) -> List[Dict]:
    """
    Generate multiple comment options for a post.
    
    Returns list of suggestions sorted by confidence.
    """
    from services.intelligent_query import create_condensed_context
    condensed_context = create_condensed_context(context_docs)
    
    options = []
    
    for i in range(num_options):
        suggestion = await generate_suggested_response(
            post=post,
            persona=persona,
            context_docs=context_docs,
            condensed_context=condensed_context
        )
        
        if suggestion and suggestion.get("confidence", 0) >= 0.6:
            options.append(suggestion)
    
    # Sort by confidence
    options.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    
    return options
