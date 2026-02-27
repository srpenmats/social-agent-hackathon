"""Tests for the RiskScorer."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.ai.risk_scorer import (
    DEFAULT_AUTO_APPROVE_MAX,
    DEFAULT_REVIEW_MAX,
    RiskScorer,
)


@pytest.fixture
def mock_compliance():
    checker = MagicMock()
    checker.full_compliance_check.return_value = {
        "passed": True,
        "violations": [],
        "score": 0,
        "suggestions": [],
    }
    return checker


@pytest.fixture
def mock_ai_response_low_risk():
    msg = MagicMock()
    msg.content = [
        MagicMock(text=json.dumps({"score": 10, "reasoning": "Low risk cultural comment"}))
    ]
    return msg


@pytest.fixture
def mock_ai_response_high_risk():
    msg = MagicMock()
    msg.content = [
        MagicMock(
            text=json.dumps(
                {"score": 85, "reasoning": "Could be interpreted as financial advice"}
            )
        )
    ]
    return msg


class TestRouteComment:
    @patch("backend.services.ai.risk_scorer.get_settings")
    def test_auto_approve(self, mock_settings, mock_compliance):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance
            scorer._get_thresholds = MagicMock(
                return_value=(DEFAULT_AUTO_APPROVE_MAX, DEFAULT_REVIEW_MAX)
            )
            assert scorer.route_comment(10) == "auto_approve"
            assert scorer.route_comment(30) == "auto_approve"

    @patch("backend.services.ai.risk_scorer.get_settings")
    def test_human_review(self, mock_settings, mock_compliance):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance
            scorer._get_thresholds = MagicMock(
                return_value=(DEFAULT_AUTO_APPROVE_MAX, DEFAULT_REVIEW_MAX)
            )
            assert scorer.route_comment(31) == "human_review"
            assert scorer.route_comment(50) == "human_review"
            assert scorer.route_comment(65) == "human_review"

    @patch("backend.services.ai.risk_scorer.get_settings")
    def test_auto_discard(self, mock_settings, mock_compliance):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance
            scorer._get_thresholds = MagicMock(
                return_value=(DEFAULT_AUTO_APPROVE_MAX, DEFAULT_REVIEW_MAX)
            )
            assert scorer.route_comment(66) == "auto_discard"
            assert scorer.route_comment(100) == "auto_discard"


class TestScoreContext:
    @patch("backend.services.ai.risk_scorer.get_settings")
    def test_clean_context(self, mock_settings, mock_compliance):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance

            ctx = {
                "description": "Fun dance video",
                "hashtags": ["#dance", "#fun"],
            }
            score = scorer.score_context(ctx)
            assert score == 0

    @patch("backend.services.ai.risk_scorer.get_settings")
    def test_controversial_topic(self, mock_settings, mock_compliance):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance

            ctx = {
                "description": "The politics of money in religion",
                "hashtags": [],
            }
            score = scorer.score_context(ctx)
            assert score >= 30  # Both "politics" and "religion"

    @patch("backend.services.ai.risk_scorer.get_settings")
    def test_risky_hashtags(self, mock_settings, mock_compliance):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance

            ctx = {
                "description": "My take",
                "hashtags": ["#politics", "#boycott"],
            }
            score = scorer.score_context(ctx)
            assert score >= 20

    @patch("backend.services.ai.risk_scorer.get_settings")
    def test_sensitive_classification(self, mock_settings, mock_compliance):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance

            ctx = {
                "description": "Discussion",
                "classification": "controversial",
            }
            score = scorer.score_context(ctx)
            assert score >= 25

    @patch("backend.services.ai.risk_scorer.get_settings")
    def test_score_capped_at_100(self, mock_settings, mock_compliance):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance

            # Many triggers should still cap at 100
            ctx = {
                "description": "politics religion tragedy disaster war terrorism scandal",
                "hashtags": ["#politics", "#boycott", "#controversy"],
                "classification": "controversial",
            }
            score = scorer.score_context(ctx)
            assert score == 100


class TestAiJudge:
    @pytest.mark.asyncio
    @patch("backend.services.ai.risk_scorer.get_settings")
    async def test_low_risk_response(
        self, mock_settings, mock_compliance, mock_ai_response_low_risk
    ):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance
            scorer.client = MagicMock()
            scorer.client.messages.create.return_value = mock_ai_response_low_risk

            result = await scorer.ai_judge("Great comment", {"description": "Fun video"})
            assert result["score"] == 10
            assert "Low risk" in result["reasoning"]

    @pytest.mark.asyncio
    @patch("backend.services.ai.risk_scorer.get_settings")
    async def test_high_risk_response(
        self, mock_settings, mock_compliance, mock_ai_response_high_risk
    ):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance
            scorer.client = MagicMock()
            scorer.client.messages.create.return_value = mock_ai_response_high_risk

            result = await scorer.ai_judge(
                "You should invest in this", {"description": "Finance talk"}
            )
            assert result["score"] == 85

    @pytest.mark.asyncio
    @patch("backend.services.ai.risk_scorer.get_settings")
    async def test_api_error_returns_default(self, mock_settings, mock_compliance):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance
            scorer.client = MagicMock()
            scorer.client.messages.create.side_effect = Exception("API error")

            result = await scorer.ai_judge("Test", {})
            assert result["score"] == 50  # Default on failure


class TestScoreComment:
    @pytest.mark.asyncio
    @patch("backend.services.ai.risk_scorer.get_settings")
    async def test_low_risk_comment(
        self, mock_settings, mock_compliance, mock_ai_response_low_risk
    ):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")
        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance
            scorer.client = MagicMock()
            scorer.client.messages.create.return_value = mock_ai_response_low_risk
            scorer._get_thresholds = MagicMock(
                return_value=(DEFAULT_AUTO_APPROVE_MAX, DEFAULT_REVIEW_MAX)
            )

            result = await scorer.score_comment(
                "The financial confidence is immaculate.",
                {"description": "Savings milestone video"},
                "tiktok",
            )
            assert result["total_score"] <= 30
            assert result["routing_decision"] == "auto_approve"
            assert "blocklist_score" in result
            assert "context_score" in result
            assert "ai_judge_score" in result

    @pytest.mark.asyncio
    @patch("backend.services.ai.risk_scorer.get_settings")
    async def test_high_risk_comment(
        self, mock_settings, mock_ai_response_high_risk
    ):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")

        # Compliance finds violations
        mock_compliance = MagicMock()
        mock_compliance.full_compliance_check.return_value = {
            "passed": False,
            "violations": [
                {"category": "absolute_ban", "matched_text": "free", "rule": "Banned word"}
            ],
            "score": 50,
            "suggestions": [],
        }

        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance
            scorer.client = MagicMock()
            scorer.client.messages.create.return_value = mock_ai_response_high_risk
            scorer._get_thresholds = MagicMock(
                return_value=(DEFAULT_AUTO_APPROVE_MAX, DEFAULT_REVIEW_MAX)
            )

            result = await scorer.score_comment(
                "Get free guaranteed money!",
                {"description": "Discussion about politics and religion"},
                "tiktok",
            )
            assert result["total_score"] > 30
            assert result["routing_decision"] in ("human_review", "auto_discard")

    @pytest.mark.asyncio
    @patch("backend.services.ai.risk_scorer.get_settings")
    async def test_product_mention_forces_review(
        self, mock_settings, mock_ai_response_low_risk
    ):
        mock_settings.return_value = MagicMock(anthropic_api_key="test")

        mock_compliance = MagicMock()
        mock_compliance.full_compliance_check.return_value = {
            "passed": True,
            "violations": [
                {
                    "category": "product_mention",
                    "matched_text": "MoneyLion",
                    "rule": "Product mentions require human review",
                }
            ],
            "score": 10,
            "suggestions": [],
        }

        with patch.object(RiskScorer, "__init__", lambda self, **kw: None):
            scorer = RiskScorer.__new__(RiskScorer)
            scorer.compliance = mock_compliance
            scorer.client = MagicMock()
            scorer.client.messages.create.return_value = mock_ai_response_low_risk
            scorer._get_thresholds = MagicMock(
                return_value=(DEFAULT_AUTO_APPROVE_MAX, DEFAULT_REVIEW_MAX)
            )

            result = await scorer.score_comment(
                "MoneyLion knows what's up",
                {"description": "Finance video"},
                "tiktok",
            )
            # Even though total score might be low, product mention forces review
            assert result["routing_decision"] == "human_review"
