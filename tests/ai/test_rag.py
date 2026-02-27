"""Tests for the RAGService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.ai.rag import RAGService, _build_query_from_context


class TestBuildQueryFromContext:
    def test_combines_fields(self):
        ctx = {
            "title": "Budget tips",
            "description": "How to save money",
            "hashtags": ["#money", "#budgeting"],
            "classification": "finance-relevant",
        }
        query = _build_query_from_context(ctx)
        assert "How to save money" in query
        assert "Budget tips" in query
        assert "#money" in query
        assert "finance-relevant" in query

    def test_empty_context(self):
        query = _build_query_from_context({})
        assert query == "general engagement"

    def test_partial_context(self):
        ctx = {"description": "Viral dance video"}
        query = _build_query_from_context(ctx)
        assert query == "Viral dance video"


class TestRAGService:
    @pytest.fixture
    def mock_embeddings(self):
        svc = MagicMock()
        svc.create_embedding = AsyncMock(return_value=[0.1] * 10)
        svc.search_similar = MagicMock(
            return_value=[
                {
                    "id": 1,
                    "chunk_text": "MoneyLion is the Irreverent Maverick",
                    "similarity": 0.85,
                    "metadata": {"section_header": "Personality"},
                },
                {
                    "id": 2,
                    "chunk_text": "TikTok engagement rules",
                    "similarity": 0.75,
                    "metadata": {"section_header": "TikTok"},
                },
            ]
        )
        return svc

    @pytest.fixture
    def mock_brand_voice(self):
        svc = MagicMock()
        svc.get_personality_config.return_value = {
            "personality": {
                "archetype": "The Irreverent Maverick",
                "core_identity": "The anti-bank friend.",
            },
            "voice_pillars": [
                {
                    "name": "Live Richly",
                    "tone": "Confident",
                    "description": "Aspirational",
                    "directives": ["Don't be shy"],
                }
            ],
            "voice_features": ["Candid language"],
            "tone_guardrails": {
                "we_are": {"confident": ["proud"]},
                "we_are_not": {"arrogant": ["vain"]},
            },
            "platform_configs": {
                "tiktok": {"formality": 2, "humor": 8, "emoji_usage": "moderate", "slang_allowed": True}
            },
        }
        svc.get_voice_context = AsyncMock(return_value="Brand voice context here")
        svc.get_platform_playbook.return_value = "## TikTok\nBe funny and fast."
        svc.get_compliance_rails.return_value = {
            "banned_words": {
                "absolute": ["free", "guaranteed"],
                "contextual": [
                    {"word": "checking account", "banned_context": "RoarMoney", "replacement": "banking account"}
                ],
            },
            "social_specific_rules": [
                {"rule": "no_financial_advice", "description": "Never advise"}
            ],
            "sensitivity_topics": {
                "requires_empathy_mode": ["job loss"],
                "do_not_engage": ["partisan politics"],
            },
        }
        svc.get_banned_words.return_value = {
            "absolute": ["free", "guaranteed", "loan"],
            "contextual": [],
        }
        svc.get_copywriting_reference.return_value = (
            "# Copywriting Reference\n\n## Do / Don't Pairs\n\n"
            "| DO | DON'T |\n|---|---|\n"
            "| Be witty | Be corporate |\n"
        )
        return svc

    @pytest.mark.asyncio
    async def test_retrieve_context(self, mock_embeddings, mock_brand_voice):
        rag = RAGService(
            brand_voice_service=mock_brand_voice, embeddings_service=mock_embeddings
        )
        results = await rag.retrieve_context("budget tips", "tiktok", top_k=5)
        assert len(results) > 0
        mock_embeddings.create_embedding.assert_called_once_with("budget tips")
        mock_embeddings.search_similar.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_context_boosts_platform(self, mock_embeddings, mock_brand_voice):
        rag = RAGService(
            brand_voice_service=mock_brand_voice, embeddings_service=mock_embeddings
        )
        results = await rag.retrieve_context("engagement", "tiktok")
        # TikTok result should be boosted
        tiktok_result = [r for r in results if "TikTok" in r.get("chunk_text", "")]
        assert len(tiktok_result) > 0

    def test_retrieve_compliance_context(self, mock_embeddings, mock_brand_voice):
        rag = RAGService(
            brand_voice_service=mock_brand_voice, embeddings_service=mock_embeddings
        )
        compliance = rag.retrieve_compliance_context()
        assert "free" in compliance
        assert "guaranteed" in compliance
        assert "no_financial_advice" in compliance
        assert "job loss" in compliance
        assert "partisan politics" in compliance

    def test_retrieve_personality(self, mock_embeddings, mock_brand_voice):
        rag = RAGService(
            brand_voice_service=mock_brand_voice, embeddings_service=mock_embeddings
        )
        personality = rag.retrieve_personality()
        assert personality["personality"]["archetype"] == "The Irreverent Maverick"

    @pytest.mark.asyncio
    async def test_assemble_system_prompt_contains_all_sections(
        self, mock_embeddings, mock_brand_voice
    ):
        rag = RAGService(
            brand_voice_service=mock_brand_voice, embeddings_service=mock_embeddings
        )
        video_context = {
            "description": "Budget tips for 2026",
            "classification": "finance-relevant",
        }
        prompt = await rag.assemble_system_prompt("tiktok", video_context)

        # Should contain brand identity
        assert "Brand Identity" in prompt
        assert "Irreverent Maverick" in prompt

        # Should contain voice pillars
        assert "Voice Pillars" in prompt
        assert "Live Richly" in prompt

        # Should contain platform rules
        assert "Platform Rules" in prompt
        assert "TikTok" in prompt

        # Should contain character limit
        assert "150 characters" in prompt

        # Should contain compliance rules
        assert "Banned Words" in prompt
        assert "free" in prompt

        # Should contain instructions
        assert "Instructions" in prompt
        assert "Never give specific financial advice" in prompt

    @pytest.mark.asyncio
    async def test_assemble_system_prompt_different_platforms(
        self, mock_embeddings, mock_brand_voice
    ):
        rag = RAGService(
            brand_voice_service=mock_brand_voice, embeddings_service=mock_embeddings
        )
        video_context = {"description": "Test"}

        prompt_tiktok = await rag.assemble_system_prompt("tiktok", video_context)
        assert "150 characters" in prompt_tiktok

        # X has 280 char limit
        mock_brand_voice.get_platform_playbook.return_value = "## X\nBe sharp."
        mock_brand_voice.get_personality_config.return_value["platform_configs"]["x"] = {
            "formality": 2, "humor": 8, "emoji_usage": "low", "slang_allowed": True
        }
        prompt_x = await rag.assemble_system_prompt("x", video_context)
        assert "280 characters" in prompt_x
