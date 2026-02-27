"""Tests for the CommentGenerator."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.ai.comment_generator import CommentGenerator


@pytest.fixture
def mock_rag():
    svc = MagicMock()
    svc.assemble_system_prompt = AsyncMock(return_value="You are MoneyLion's voice.")
    return svc


@pytest.fixture
def mock_anthropic_response():
    """Create a mock Anthropic API response."""
    candidates = [
        {
            "text": "The financial confidence is immaculate.",
            "approach": "witty",
            "voice_pillar": "Live Richly",
            "confidence_score": 8,
        },
        {
            "text": "One step at a time. You're further ahead than you realize.",
            "approach": "supportive",
            "voice_pillar": "Share The Secret",
            "confidence_score": 7,
        },
        {
            "text": "Credit building is a marathon, not a sprint.",
            "approach": "helpful",
            "voice_pillar": "No Bull$hit",
            "confidence_score": 7,
        },
    ]
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text=json.dumps(candidates))]
    return mock_msg


class TestCommentGenerator:
    @pytest.mark.asyncio
    @patch("backend.services.ai.comment_generator.get_settings")
    async def test_generate_candidates(self, mock_settings, mock_rag, mock_anthropic_response):
        mock_settings.return_value = MagicMock(anthropic_api_key="test-key")

        with patch.object(CommentGenerator, "__init__", lambda self, **kwargs: None):
            gen = CommentGenerator.__new__(CommentGenerator)
            gen.rag = mock_rag
            gen.client = MagicMock()
            gen.client.messages.create.return_value = mock_anthropic_response

            video_context = {
                "description": "How to save money in 2026",
                "creator": "FinanceGuru",
                "followers": 50000,
                "likes": 10000,
                "comments_count": 500,
                "shares": 200,
                "hashtags": ["#money", "#saving"],
                "classification": "finance-relevant",
            }

            candidates = await gen.generate_candidates(video_context, "tiktok", 3)
            assert len(candidates) == 3
            assert candidates[0]["approach"] == "witty"
            assert candidates[1]["approach"] == "supportive"
            assert candidates[2]["approach"] == "helpful"
            # All should have char_count
            for c in candidates:
                assert "char_count" in c

    @pytest.mark.asyncio
    @patch("backend.services.ai.comment_generator.get_settings")
    async def test_character_limit_enforcement(self, mock_settings, mock_rag):
        mock_settings.return_value = MagicMock(anthropic_api_key="test-key")

        long_text = "A" * 200  # Over TikTok 150 limit
        long_candidates = [
            {"text": long_text, "approach": "witty", "voice_pillar": "test", "confidence_score": 8}
        ]
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=json.dumps(long_candidates))]

        with patch.object(CommentGenerator, "__init__", lambda self, **kwargs: None):
            gen = CommentGenerator.__new__(CommentGenerator)
            gen.rag = mock_rag
            gen.client = MagicMock()
            gen.client.messages.create.return_value = mock_msg

            candidates = await gen.generate_candidates({}, "tiktok", 1)
            assert len(candidates) == 1
            assert len(candidates[0]["text"]) <= 150

    @pytest.mark.asyncio
    @patch("backend.services.ai.comment_generator.get_settings")
    async def test_select_best_candidate(self, mock_settings, mock_rag):
        mock_settings.return_value = MagicMock(anthropic_api_key="test-key")

        with patch.object(CommentGenerator, "__init__", lambda self, **kwargs: None):
            gen = CommentGenerator.__new__(CommentGenerator)
            gen.rag = mock_rag
            gen.client = MagicMock()

            candidates = [
                {"text": "Short witty comment", "confidence_score": 8, "approach": "witty"},
                {"text": "A longer supportive comment that is more detailed", "confidence_score": 7, "approach": "supportive"},
                {"text": "Helpful", "confidence_score": 9, "approach": "helpful"},
            ]

            best = await gen.select_best_candidate(candidates, {})
            # Highest confidence (9) + short bonus (1) = 10 for "Helpful"
            assert best["text"] == "Helpful"
            assert best["selected"] is True

    @pytest.mark.asyncio
    @patch("backend.services.ai.comment_generator.get_settings")
    async def test_select_best_single_candidate(self, mock_settings, mock_rag):
        mock_settings.return_value = MagicMock(anthropic_api_key="test-key")

        with patch.object(CommentGenerator, "__init__", lambda self, **kwargs: None):
            gen = CommentGenerator.__new__(CommentGenerator)
            gen.rag = mock_rag

            candidates = [{"text": "Only one", "confidence_score": 5}]
            best = await gen.select_best_candidate(candidates, {})
            assert best["text"] == "Only one"

    @pytest.mark.asyncio
    @patch("backend.services.ai.comment_generator.get_settings")
    async def test_select_best_empty_list(self, mock_settings, mock_rag):
        mock_settings.return_value = MagicMock(anthropic_api_key="test-key")

        with patch.object(CommentGenerator, "__init__", lambda self, **kwargs: None):
            gen = CommentGenerator.__new__(CommentGenerator)
            gen.rag = mock_rag

            best = await gen.select_best_candidate([], {})
            assert best == {}

    @pytest.mark.asyncio
    @patch("backend.services.ai.comment_generator.get_settings")
    async def test_test_voice(self, mock_settings, mock_rag, mock_anthropic_response):
        mock_settings.return_value = MagicMock(anthropic_api_key="test-key")

        with patch.object(CommentGenerator, "__init__", lambda self, **kwargs: None):
            gen = CommentGenerator.__new__(CommentGenerator)
            gen.rag = mock_rag
            gen.client = MagicMock()
            gen.client.messages.create.return_value = mock_anthropic_response

            candidates = await gen.test_voice(
                {"description": "Test video about money"},
                platform="tiktok",
            )
            assert len(candidates) == 3
            # test_voice should not store to DB (no db_id)
            for c in candidates:
                assert "db_id" not in c

    @pytest.mark.asyncio
    @patch("backend.services.ai.comment_generator.get_settings")
    async def test_generate_with_edit(self, mock_settings, mock_rag):
        mock_settings.return_value = MagicMock(anthropic_api_key="test-key")

        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text="Revised comment text")]

        with patch.object(CommentGenerator, "__init__", lambda self, **kwargs: None):
            gen = CommentGenerator.__new__(CommentGenerator)
            gen.rag = mock_rag
            gen.client = MagicMock()
            gen.client.messages.create.return_value = mock_msg

            result = await gen.generate_with_edit(
                "Original comment",
                "Make it funnier",
                platform="tiktok",
            )
            assert result == "Revised comment text"

    @pytest.mark.asyncio
    @patch("backend.services.ai.comment_generator.get_settings")
    async def test_handles_code_block_response(self, mock_settings, mock_rag):
        """Test that JSON wrapped in markdown code blocks is handled."""
        mock_settings.return_value = MagicMock(anthropic_api_key="test-key")

        candidates = [{"text": "Test", "approach": "witty", "voice_pillar": "test", "confidence_score": 7}]
        wrapped = f"```json\n{json.dumps(candidates)}\n```"
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=wrapped)]

        with patch.object(CommentGenerator, "__init__", lambda self, **kwargs: None):
            gen = CommentGenerator.__new__(CommentGenerator)
            gen.rag = mock_rag
            gen.client = MagicMock()
            gen.client.messages.create.return_value = mock_msg

            result = await gen.generate_candidates({}, "tiktok", 1)
            assert len(result) == 1
            assert result[0]["text"] == "Test"
