"""AI comment generation using Claude API with RAG-powered prompts.

Generates comment candidates for social media engagement, selecting the
best candidate based on compliance, platform fit, and engagement potential.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

import anthropic

fromconfig import get_settings
fromdb.connection import get_supabase_admin
fromservices.ai.rag import PLATFORM_CHAR_LIMITS, RAGService

logger = logging.getLogger(__name__)

CLAUDE_MODEL = "claude-sonnet-4-5-20250514"
MAX_RETRIES = 3

GENERATION_USER_PROMPT = """Generate {num_candidates} comment candidates for this social media engagement.

## Video/Post Context
- Platform: {platform}
- Title: {title}
- Description: {description}
- Hashtags: {hashtags}
- Creator: {creator} ({followers} followers)
- Engagement: {likes} likes, {comments} comments, {shares} shares
- Classification: {classification}
{transcript_section}

## Requirements
- Generate exactly {num_candidates} different comment candidates
- Each candidate should use a different approach: one witty, one helpful, one supportive
- Each comment MUST be under {char_limit} characters
- Sound like a real person commenting, NOT a brand
- Match the energy of {platform} comment sections

Respond with a JSON array of objects, each with:
- "text": the comment text
- "approach": "witty" | "helpful" | "supportive"
- "voice_pillar": which MoneyLion voice pillar it draws from
- "confidence_score": 1-10 how confident you are this will engage

Output ONLY the JSON array, no other text.
"""


class CommentGenerator:
    """Generate comment candidates using Claude API with RAG context."""

    def __init__(self, rag_service: RAGService | None = None):
        self.rag = rag_service or RAGService()
        settings = get_settings()
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def generate_candidates(
        self,
        video_context: dict[str, Any],
        platform: str,
        num_candidates: int = 3,
    ) -> list[dict[str, Any]]:
        """Generate N comment candidates using RAG + Claude.

        Returns list of candidates with text, approach, voice_pillar, confidence_score.
        Stores all candidates in generated_comments table.
        """
        # Assemble system prompt with RAG context
        system_prompt = await self.rag.assemble_system_prompt(platform, video_context)

        # Format user prompt
        char_limit = PLATFORM_CHAR_LIMITS.get(platform.lower(), 300)
        user_prompt = GENERATION_USER_PROMPT.format(
            num_candidates=num_candidates,
            platform=platform,
            title=video_context.get("title", "N/A"),
            description=video_context.get("description", "N/A"),
            hashtags=", ".join(video_context.get("hashtags", [])),
            creator=video_context.get("creator", "Unknown"),
            followers=video_context.get("followers", "N/A"),
            likes=video_context.get("likes", 0),
            comments=video_context.get("comments_count", 0),
            shares=video_context.get("shares", 0),
            classification=video_context.get("classification", "cultural"),
            transcript_section=(
                f"- Transcript: {video_context['transcript']}"
                if video_context.get("transcript")
                else ""
            ),
            char_limit=char_limit,
        )

        # Call Claude API
        candidates = await self._call_claude(system_prompt, user_prompt)

        # Validate and store candidates
        validated = []
        video_id = video_context.get("video_id")
        for candidate in candidates:
            text = candidate.get("text", "").strip()
            if not text:
                continue

            # Enforce character limit
            if len(text) > char_limit:
                text = text[:char_limit].rsplit(" ", 1)[0]
                candidate["text"] = text

            candidate["char_count"] = len(text)
            validated.append(candidate)

            # Store in database
            if video_id:
                self._store_candidate(video_id, candidate)

        return validated

    async def select_best_candidate(
        self, candidates: list[dict[str, Any]], video_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Select the best candidate from a list using scoring.

        Scores by: confidence, character count appropriateness, and approach variety.
        """
        if not candidates:
            return {}

        if len(candidates) == 1:
            return candidates[0]

        # Simple scoring: confidence_score is primary, then prefer shorter comments
        scored = []
        for c in candidates:
            score = c.get("confidence_score", 5)
            # Bonus for shorter comments (more punchy)
            char_count = len(c.get("text", ""))
            if char_count < 100:
                score += 1
            scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1]
        best["selected"] = True

        # Mark as selected in DB
        if best.get("db_id"):
            try:
                db = get_supabase_admin()
                db.table("generated_comments").update({"selected": True}).eq(
                    "id", best["db_id"]
                ).execute()
            except Exception as e:
                logger.warning("Failed to mark candidate as selected: %s", e)

        return best

    async def test_voice(
        self, video_context: dict[str, Any], platform: str = "tiktok"
    ) -> list[dict[str, Any]]:
        """Generate test candidates without storing or posting.

        Used by the settings/voice/test endpoint.
        """
        system_prompt = await self.rag.assemble_system_prompt(platform, video_context)

        char_limit = PLATFORM_CHAR_LIMITS.get(platform.lower(), 300)
        user_prompt = GENERATION_USER_PROMPT.format(
            num_candidates=3,
            platform=platform,
            title=video_context.get("title", "Test video"),
            description=video_context.get("description", "Test description"),
            hashtags=", ".join(video_context.get("hashtags", [])),
            creator=video_context.get("creator", "TestCreator"),
            followers=video_context.get("followers", "10000"),
            likes=video_context.get("likes", 5000),
            comments=video_context.get("comments_count", 200),
            shares=video_context.get("shares", 100),
            classification=video_context.get("classification", "cultural"),
            transcript_section="",
            char_limit=char_limit,
        )

        candidates = await self._call_claude(system_prompt, user_prompt)
        # Don't store, just return
        return [
            {
                "text": c.get("text", "").strip(),
                "approach": c.get("approach", "witty"),
                "voice_pillar": c.get("voice_pillar", ""),
                "confidence_score": c.get("confidence_score", 5),
                "char_count": len(c.get("text", "")),
            }
            for c in candidates
            if c.get("text", "").strip()
        ]

    async def generate_with_edit(
        self, original_text: str, edit_instructions: str, platform: str = "tiktok"
    ) -> str:
        """Re-generate a comment with specific edit instructions."""
        char_limit = PLATFORM_CHAR_LIMITS.get(platform.lower(), 300)
        system_prompt = (
            "You are MoneyLion's social media voice editor. "
            "Modify the given comment according to the instructions while "
            "maintaining the brand voice (witty, confident, accessible, culturally relevant). "
            f"Keep the result under {char_limit} characters."
        )
        user_prompt = (
            f"Original comment: {original_text}\n\n"
            f"Edit instructions: {edit_instructions}\n\n"
            f"Output ONLY the revised comment text, nothing else."
        )

        message = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        result = message.content[0].text.strip()
        # Enforce char limit
        if len(result) > char_limit:
            result = result[:char_limit].rsplit(" ", 1)[0]
        return result

    async def _call_claude(
        self, system_prompt: str, user_prompt: str
    ) -> list[dict[str, Any]]:
        """Call Claude API and parse JSON response. Retries on failure."""
        for attempt in range(MAX_RETRIES):
            try:
                message = self.client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )

                response_text = message.content[0].text.strip()

                # Extract JSON array from response
                # Handle cases where model wraps in markdown code block
                if response_text.startswith("```"):
                    lines = response_text.split("\n")
                    json_lines = [
                        l
                        for l in lines
                        if not l.startswith("```")
                    ]
                    response_text = "\n".join(json_lines)

                candidates = json.loads(response_text)
                if isinstance(candidates, list):
                    return candidates

                logger.warning(
                    "Claude returned non-list response on attempt %d", attempt + 1
                )
            except json.JSONDecodeError as e:
                logger.warning(
                    "Failed to parse Claude response as JSON (attempt %d): %s",
                    attempt + 1,
                    e,
                )
            except anthropic.APIError as e:
                logger.error("Claude API error (attempt %d): %s", attempt + 1, e)
                if attempt == MAX_RETRIES - 1:
                    raise

        return []

    def _store_candidate(
        self, video_id: int, candidate: dict[str, Any]
    ) -> None:
        """Store a generated candidate in the database."""
        try:
            db = get_supabase_admin()
            row = {
                "video_id": video_id,
                "text": candidate["text"],
                "approach": candidate.get("approach", "witty"),
                "char_count": candidate.get("char_count", len(candidate["text"])),
                "selected": False,
            }
            result = db.table("generated_comments").insert(row).execute()
            if result.data:
                candidate["db_id"] = result.data[0]["id"]
        except Exception as e:
            logger.warning("Failed to store candidate: %s", e)
