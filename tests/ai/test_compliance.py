"""Tests for the ComplianceChecker."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

fromservices.ai.compliance import ComplianceChecker


@pytest.fixture
def mock_brand_voice():
    svc = MagicMock()
    svc.get_banned_words.return_value = {
        "absolute": [
            "free",
            "guaranteed",
            "borrow",
            "payday",
            "payday loan",
            "debt",
            "loan",
            "roar",
            "pounce",
            "lion",
            "pride",
            "low",
            "cheap",
        ],
        "contextual": [
            {
                "word": "checking account",
                "banned_context": "Describing RoarMoney",
                "replacement": "banking account",
            },
            {
                "word": "get paid early",
                "banned_context": "Without qualifier",
                "replacement": "get paid up to 2 days early",
            },
        ],
    }
    svc.get_compliance_rails.return_value = {
        "social_specific_rules": [
            {"rule": "no_financial_advice", "severity": "critical"},
        ],
        "sensitivity_topics": {
            "requires_empathy_mode": ["job loss", "bankruptcy", "medical debt"],
            "do_not_engage": ["partisan politics", "religious debates"],
        },
        "disclaimer_triggers": {"triggers": []},
        "content_classification": {},
    }
    return svc


@pytest.fixture
def checker(mock_brand_voice):
    return ComplianceChecker(brand_voice_service=mock_brand_voice)


class TestCheckBlocklist:
    def test_detects_absolute_ban(self, checker):
        result = checker.check_blocklist("Get free money now!")
        assert not result["passed"]
        assert "free" in result["matches"]

    def test_case_insensitive(self, checker):
        result = checker.check_blocklist("This is GUARANTEED to work")
        assert not result["passed"]
        assert "guaranteed" in result["matches"]

    def test_word_boundary_matching(self, checker):
        # "lowering" should NOT trigger "low"
        result = checker.check_blocklist("Lowering your expenses is smart")
        assert result["passed"]
        assert len(result["matches"]) == 0

    def test_exact_word_low_triggers(self, checker):
        result = checker.check_blocklist("This is a low effort post")
        assert not result["passed"]
        assert "low" in result["matches"]

    def test_multi_word_phrase(self, checker):
        result = checker.check_blocklist("This is like a payday loan scheme")
        assert not result["passed"]
        assert "payday loan" in result["matches"]

    def test_clean_text_passes(self, checker):
        result = checker.check_blocklist(
            "The financial confidence is immaculate."
        )
        assert result["passed"]
        assert len(result["matches"]) == 0

    def test_score_increases_with_matches(self, checker):
        result = checker.check_blocklist("Get free guaranteed loans with no debt")
        assert result["score"] > 0
        assert len(result["matches"]) >= 3

    def test_lion_themed_bans(self, checker):
        result = checker.check_blocklist("Time to roar about our pride!")
        assert not result["passed"]
        assert "roar" in result["matches"]
        assert "pride" in result["matches"]


class TestCheckBannedWords:
    def test_includes_absolute_violations(self, checker):
        result = checker.check_banned_words("Get free money")
        assert not result["passed"]
        assert any(v["category"] == "absolute_ban" for v in result["violations"])

    def test_contextual_ban_checking_account(self, checker):
        result = checker.check_banned_words("Open a checking account today")
        violations = result["violations"]
        contextual = [v for v in violations if v["category"] == "contextual_ban"]
        assert len(contextual) == 1
        assert contextual[0]["matched_text"] == "checking account"

    def test_contextual_ban_get_paid_early(self, checker):
        result = checker.check_banned_words("You can get paid early with this")
        contextual = [
            v for v in result["violations"] if v["category"] == "contextual_ban"
        ]
        assert len(contextual) == 1

    def test_clean_text(self, checker):
        result = checker.check_banned_words("Building credit is a marathon.")
        assert result["passed"]


class TestCheckCharacterLimit:
    def test_tiktok_under_limit(self, checker):
        result = checker.check_character_limit("Short comment", "tiktok")
        assert result["passed"]
        assert result["over_by"] == 0

    def test_tiktok_over_limit(self, checker):
        long_text = "A" * 200
        result = checker.check_character_limit(long_text, "tiktok")
        assert not result["passed"]
        assert result["limit"] == 150
        assert result["over_by"] == 50

    def test_instagram_limit(self, checker):
        text = "A" * 250
        result = checker.check_character_limit(text, "instagram")
        assert result["passed"]  # 250 < 300

    def test_x_limit(self, checker):
        text = "A" * 281
        result = checker.check_character_limit(text, "x")
        assert not result["passed"]
        assert result["limit"] == 280

    def test_unknown_platform_default(self, checker):
        result = checker.check_character_limit("Short", "unknown")
        assert result["passed"]
        assert result["limit"] == 300


class TestCheckProductMentions:
    def test_detects_moneylion(self, checker):
        result = checker.check_product_mentions("Check out MoneyLion!")
        assert result["requires_review"]
        assert "MoneyLion" in result["mentions"]

    def test_detects_instacash(self, checker):
        result = checker.check_product_mentions("Instacash is great")
        assert result["requires_review"]
        assert "Instacash" in result["mentions"]

    def test_detects_misspelling(self, checker):
        result = checker.check_product_mentions("Try InstaCash today")
        assert not result["passed"]
        assert "InstaCash" in result["misspellings"]

    def test_detects_roar_money_misspelling(self, checker):
        result = checker.check_product_mentions("Roar Money is cool")
        assert not result["passed"]
        assert "Roar Money" in result["misspellings"]

    def test_no_product_mentions(self, checker):
        result = checker.check_product_mentions("Budget tips for everyone")
        assert result["passed"]
        assert not result["requires_review"]


class TestCheckSensitivity:
    def test_empathy_trigger(self, checker):
        result = checker.check_sensitivity("Sorry to hear about the job loss")
        assert result["empathy_mode"]
        assert "job loss" in result["empathy_triggers"]

    def test_do_not_engage(self, checker):
        result = checker.check_sensitivity(
            "This is about partisan politics"
        )
        assert not result["passed"]
        assert len(result["do_not_engage"]) > 0

    def test_clean_text(self, checker):
        result = checker.check_sensitivity("Great savings tip!")
        assert result["passed"]
        assert not result["empathy_mode"]


class TestFullComplianceCheck:
    def test_clean_short_comment_passes(self, checker):
        result = checker.full_compliance_check(
            "The financial confidence is immaculate.", "tiktok"
        )
        assert result["passed"]
        assert result["score"] == 0

    def test_banned_word_fails(self, checker):
        result = checker.full_compliance_check("Get free money!", "tiktok")
        assert not result["passed"]
        assert result["score"] > 0
        assert any(
            v["category"] == "absolute_ban" for v in result["violations"]
        )

    def test_over_character_limit_adds_violation(self, checker):
        long_text = "A" * 200
        result = checker.full_compliance_check(long_text, "tiktok")
        char_violations = [
            v for v in result["violations"] if v["category"] == "character_limit"
        ]
        assert len(char_violations) == 1

    def test_product_mention_adds_review_violation(self, checker):
        result = checker.full_compliance_check(
            "MoneyLion rocks!", "tiktok"
        )
        product_violations = [
            v for v in result["violations"] if v["category"] == "product_mention"
        ]
        assert len(product_violations) == 1
        # Product mention alone doesn't fail compliance (just requires review)

    def test_misspelling_fails(self, checker):
        result = checker.full_compliance_check("Try InstaCash!", "tiktok")
        assert not result["passed"]

    def test_suggestions_include_replacements(self, checker):
        result = checker.full_compliance_check(
            "Open a checking account with us", "tiktok"
        )
        # Should have suggestion for "checking account"
        assert len(result["suggestions"]) > 0

    def test_multiple_violations_compound_score(self, checker):
        result = checker.full_compliance_check(
            "Get free guaranteed payday loans now!", "tiktok"
        )
        assert result["score"] > 50
