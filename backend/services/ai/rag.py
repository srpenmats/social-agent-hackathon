"""RAG retrieval service for assembling context-rich prompts.

Combines brand voice chunks, platform playbooks, compliance rules,
and personality config into a complete system prompt for comment generation.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from backend.services.ai.brand_voice import BrandVoiceService
from backend.services.ai.embeddings import EmbeddingsService

logger = logging.getLogger(__name__)

# Character limits per platform
PLATFORM_CHAR_LIMITS: dict[str, int] = {
    "tiktok": 150,
    "instagram": 300,
    "x": 280,
    "youtube": 500,
}


class RAGService:
    """Retrieve brand voice context and assemble system prompts for generation."""

    def __init__(
        self,
        brand_voice_service: BrandVoiceService | None = None,
        embeddings_service: EmbeddingsService | None = None,
    ):
        self.embeddings = embeddings_service or EmbeddingsService()
        self.brand_voice = brand_voice_service or BrandVoiceService(
            embeddings_service=self.embeddings
        )

    async def retrieve_context(
        self, query: str, platform: str, top_k: int = 5
    ) -> list[dict[str, Any]]:
        """Full RAG pipeline: embed query, search pgvector, return ranked chunks."""
        query_embedding = await self.embeddings.create_embedding(query)
        results = self.embeddings.search_similar(
            query_embedding, top_k=top_k, threshold=0.4
        )

        # Boost platform-specific results
        if platform:
            for r in results:
                chunk_text = r.get("chunk_text", "").lower()
                metadata = r.get("metadata", {})
                if platform.lower() in chunk_text or platform.lower() in str(
                    metadata.get("section_header", "")
                ).lower():
                    r["similarity"] = r.get("similarity", 0.5) * 1.2

            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

        return results[:top_k]

    def retrieve_compliance_context(self) -> str:
        """Get all compliance rules as formatted text."""
        rails = self.brand_voice.get_compliance_rails()
        if not rails:
            return ""

        parts = []

        # Banned words
        banned = rails.get("banned_words", {})
        absolute = banned.get("absolute", [])
        if absolute:
            parts.append(
                f"ABSOLUTE BANNED WORDS (never use these): {', '.join(absolute)}"
            )

        contextual = banned.get("contextual", [])
        if contextual:
            ctx_lines = []
            for rule in contextual:
                ctx_lines.append(
                    f"  - '{rule['word']}' banned when: {rule.get('banned_context', 'any')}. "
                    f"Use instead: {rule.get('replacement', 'N/A')}"
                )
            parts.append("CONTEXTUAL BANS:\n" + "\n".join(ctx_lines))

        # Social rules
        social_rules = rails.get("social_specific_rules", [])
        if social_rules:
            rule_lines = [
                f"  - {r['rule']}: {r.get('description', '')}" for r in social_rules
            ]
            parts.append("SOCIAL RULES:\n" + "\n".join(rule_lines))

        # Sensitivity
        sensitivity = rails.get("sensitivity_topics", {})
        if sensitivity:
            empathy = sensitivity.get("requires_empathy_mode", [])
            if empathy:
                parts.append(
                    f"EMPATHY MODE TRIGGERS (be supportive, never pitch): {', '.join(empathy)}"
                )
            no_engage = sensitivity.get("do_not_engage", [])
            if no_engage:
                parts.append(
                    f"DO NOT ENGAGE WITH: {', '.join(no_engage)}"
                )

        return "\n\n".join(parts)

    def retrieve_personality(self) -> dict[str, Any]:
        """Get core personality traits."""
        return self.brand_voice.get_personality_config()

    async def assemble_system_prompt(
        self, platform: str, video_context: dict[str, Any]
    ) -> str:
        """Build complete system prompt for comment generation.

        Combines:
        - Brand personality
        - RAG-retrieved voice guidelines
        - Platform-specific rules
        - Banned words / compliance rules
        - Positive/negative examples
        """
        parts: list[str] = []

        # 1. Brand identity and personality
        personality = self.retrieve_personality()
        if personality:
            p = personality.get("personality", {})
            parts.append(
                f"# Brand Identity\n"
                f"You are MoneyLion's social media voice.\n"
                f"Personality Archetype: {p.get('archetype', 'The Irreverent Maverick')}\n"
                f"Core Identity: {p.get('core_identity', '')}\n"
            )

            # Voice pillars
            pillars = personality.get("voice_pillars", [])
            if pillars:
                pillar_lines = []
                for vp in pillars:
                    directives = vp.get("directives", [])
                    dir_text = "; ".join(directives) if directives else ""
                    pillar_lines.append(
                        f"- **{vp.get('name', '')}** ({vp.get('tone', '')}): "
                        f"{vp.get('description', '')}. Directives: {dir_text}"
                    )
                parts.append("# Voice Pillars\n" + "\n".join(pillar_lines))

            # Voice features
            features = personality.get("voice_features", [])
            if features:
                parts.append("# Voice Features\n" + "\n".join(f"- {f}" for f in features))

            # Tone guardrails
            guardrails = personality.get("tone_guardrails", {})
            we_are = guardrails.get("we_are", {})
            we_are_not = guardrails.get("we_are_not", {})
            if we_are or we_are_not:
                parts.append(
                    f"# Tone Guardrails\n"
                    f"We ARE: {json.dumps(we_are)}\n"
                    f"We are NOT: {json.dumps(we_are_not)}"
                )

        # 2. RAG-retrieved voice context relevant to this video
        query = _build_query_from_context(video_context)
        voice_context = await self.brand_voice.get_voice_context(query, platform)
        if voice_context:
            parts.append(f"# Relevant Brand Voice Context\n{voice_context}")

        # 3. Platform-specific rules
        playbook = self.brand_voice.get_platform_playbook(platform)
        if playbook:
            parts.append(f"# Platform Rules ({platform.upper()})\n{playbook}")

        # Character limit
        char_limit = PLATFORM_CHAR_LIMITS.get(platform.lower(), 300)
        platform_config = personality.get("platform_configs", {}).get(
            platform.lower(), {}
        )
        parts.append(
            f"# Character Limit\n"
            f"Maximum comment length: {char_limit} characters.\n"
            f"Formality level: {platform_config.get('formality', 5)}/10\n"
            f"Humor level: {platform_config.get('humor', 5)}/10\n"
            f"Emoji usage: {platform_config.get('emoji_usage', 'moderate')}\n"
            f"Slang allowed: {platform_config.get('slang_allowed', False)}"
        )

        # 4. Compliance rules and banned words
        compliance = self.retrieve_compliance_context()
        if compliance:
            parts.append(f"# Compliance Rules\n{compliance}")

        banned = self.brand_voice.get_banned_words()
        absolute_bans = banned.get("absolute", [])
        if absolute_bans:
            parts.append(
                f"# CRITICAL: Banned Words\n"
                f"NEVER use any of these words/phrases in your output:\n"
                f"{', '.join(absolute_bans)}"
            )

        # 5. Examples from copywriting reference
        ref = self.brand_voice.get_copywriting_reference()
        if ref:
            # Extract do/don't section
            examples = _extract_examples(ref)
            if examples:
                parts.append(f"# Examples\n{examples}")

        # 6. Core instructions
        parts.append(
            "# Instructions\n"
            "- Generate comments that sound human, not corporate\n"
            "- Match the platform's native language and energy\n"
            "- Never give specific financial advice\n"
            "- Never promise outcomes or guarantee anything\n"
            "- Never disparage competitors by name\n"
            "- If the content is about financial hardship, be empathetic and supportive. NEVER pitch a product.\n"
            "- Each comment should make someone feel: enlightened, entertained, curious, or understood\n"
            "- Prioritize engagement potential over information density"
        )

        return "\n\n".join(parts)


def _build_query_from_context(video_context: dict[str, Any]) -> str:
    """Build a search query from video context for RAG retrieval."""
    parts = []
    if video_context.get("description"):
        parts.append(video_context["description"])
    if video_context.get("title"):
        parts.append(video_context["title"])
    if video_context.get("hashtags"):
        parts.append(" ".join(video_context["hashtags"][:5]))
    if video_context.get("classification"):
        parts.append(video_context["classification"])
    return " ".join(parts) if parts else "general engagement"


def _extract_examples(copywriting_ref: str) -> str:
    """Extract do/don't examples from copywriting reference."""
    import re

    # Find the Do / Don't Pairs section
    match = re.search(
        r"## Do / Don't Pairs(.*?)(?=## |\Z)",
        copywriting_ref,
        re.DOTALL,
    )
    if match:
        section = match.group(1).strip()
        # Limit to avoid bloating the prompt
        lines = section.split("\n")
        if len(lines) > 50:
            lines = lines[:50]
        return "\n".join(lines)
    return ""
