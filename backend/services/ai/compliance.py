"""Compliance checking service for content validation.

Enforces banned words, product naming rules, character limits, and social-specific
rules from brand_guidelines.md and compliance_rails.json.
"""

from __future__ import annotations

import logging
import re
from typing import Any

fromdb.connection import get_supabase_admin
fromservices.ai.brand_voice import BrandVoiceService

logger = logging.getLogger(__name__)

# Character limits per platform
PLATFORM_CHAR_LIMITS: dict[str, int] = {
    "tiktok": 150,
    "instagram": 300,
    "x": 280,
    "youtube": 500,
}

# MoneyLion product names for mention detection
PRODUCT_NAMES = [
    "MoneyLion",
    "RoarMoney",
    "Instacash",
    "Credit Builder Plus",
    "WOW",
    "Shake 'N' Bank",
    "Financial Heartbeat",
    "Debit Mastercard",
]

# Known misspellings to reject
PRODUCT_MISSPELLINGS = [
    "InstaCash",
    "Insta cash",
    "Insta Cash",
    "Roar Money",
    "Roarmoney",
    "Roar money",
    "MoneyLion's RoarMoney",
    "RoarMoney by MoneyLion",
]


class ComplianceChecker:
    """Check content against brand compliance rules before publishing."""

    def __init__(self, brand_voice_service: BrandVoiceService | None = None):
        self.brand_voice = brand_voice_service or BrandVoiceService()
        self._rules: dict[str, Any] | None = None

    def load_rules(self) -> dict[str, Any]:
        """Parse compliance_rails.json and brand_guidelines.md into structured rules."""
        if self._rules is not None:
            return self._rules

        banned = self.brand_voice.get_banned_words()
        rails = self.brand_voice.get_compliance_rails()

        self._rules = {
            "absolute_bans": banned.get("absolute", []),
            "contextual_bans": banned.get("contextual", []),
            "misspellings": PRODUCT_MISSPELLINGS,
            "social_rules": rails.get("social_specific_rules", []),
            "sensitivity_topics": rails.get("sensitivity_topics", {}),
            "disclaimer_triggers": rails.get("disclaimer_triggers", {}).get(
                "triggers", []
            ),
            "content_classification": rails.get("content_classification", {}),
        }
        return self._rules

    def check_blocklist(self, text: str) -> dict[str, Any]:
        """Scan text against all absolute banned words/phrases.

        Uses word boundary matching to avoid false positives
        (e.g., "lowering" should not trigger "low").
        """
        rules = self.load_rules()
        matches: list[str] = []
        text_lower = text.lower()

        for banned_word in rules["absolute_bans"]:
            banned_lower = banned_word.lower()
            # Use word boundary matching for single words
            # For multi-word phrases, use substring matching
            if " " in banned_lower:
                if banned_lower in text_lower:
                    matches.append(banned_word)
            else:
                pattern = rf"\b{re.escape(banned_lower)}\b"
                if re.search(pattern, text_lower):
                    matches.append(banned_word)

        score = min(100, len(matches) * 25)
        return {
            "passed": len(matches) == 0,
            "matches": matches,
            "score": score,
        }

    def check_banned_words(self, text: str) -> dict[str, Any]:
        """Check against both absolute and contextual bans."""
        # Start with absolute bans
        blocklist_result = self.check_blocklist(text)
        violations: list[dict[str, str]] = []

        for match in blocklist_result["matches"]:
            violations.append(
                {
                    "category": "absolute_ban",
                    "matched_text": match,
                    "rule": f"'{match}' is absolutely banned in all MoneyLion content",
                }
            )

        # Check contextual bans
        rules = self.load_rules()
        text_lower = text.lower()
        for ctx_ban in rules["contextual_bans"]:
            word = ctx_ban.get("word", "").lower()
            if word and word in text_lower:
                violations.append(
                    {
                        "category": "contextual_ban",
                        "matched_text": ctx_ban["word"],
                        "rule": f"'{ctx_ban['word']}' banned when: {ctx_ban.get('banned_context', 'any context')}",
                        "suggestion": ctx_ban.get("replacement", ""),
                    }
                )

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "score": blocklist_result["score"],
        }

    def check_character_limit(self, text: str, platform: str) -> dict[str, Any]:
        """Verify text is within platform character limits."""
        limit = PLATFORM_CHAR_LIMITS.get(platform.lower(), 300)
        char_count = len(text)
        passed = char_count <= limit

        return {
            "passed": passed,
            "char_count": char_count,
            "limit": limit,
            "over_by": max(0, char_count - limit),
        }

    def check_product_mentions(self, text: str) -> dict[str, Any]:
        """Flag any MoneyLion product mentions for human review."""
        mentions: list[str] = []
        misspellings: list[str] = []

        # Check for correct product names
        for product in PRODUCT_NAMES:
            if product.lower() in text.lower():
                mentions.append(product)

        # Check for misspellings
        for misspelling in PRODUCT_MISSPELLINGS:
            if misspelling in text:
                misspellings.append(misspelling)

        requires_review = len(mentions) > 0
        has_errors = len(misspellings) > 0

        return {
            "passed": not has_errors,
            "mentions": mentions,
            "misspellings": misspellings,
            "requires_review": requires_review,
        }

    def check_sensitivity(self, text: str) -> dict[str, Any]:
        """Check if text touches sensitive topics."""
        rules = self.load_rules()
        sensitivity = rules.get("sensitivity_topics", {})

        empathy_triggers: list[str] = []
        do_not_engage: list[str] = []
        text_lower = text.lower()

        for trigger in sensitivity.get("requires_empathy_mode", []):
            if trigger.lower() in text_lower:
                empathy_triggers.append(trigger)

        for topic in sensitivity.get("do_not_engage", []):
            if topic.lower().replace("_", " ") in text_lower:
                do_not_engage.append(topic)

        return {
            "passed": len(do_not_engage) == 0,
            "empathy_mode": len(empathy_triggers) > 0,
            "empathy_triggers": empathy_triggers,
            "do_not_engage": do_not_engage,
        }

    def full_compliance_check(
        self, text: str, platform: str
    ) -> dict[str, Any]:
        """Run all compliance checks. Returns comprehensive result."""
        violations: list[dict[str, str]] = []
        suggestions: list[str] = []
        total_score = 0

        # 1. Banned words (absolute + contextual)
        banned_result = self.check_banned_words(text)
        violations.extend(banned_result["violations"])
        total_score += banned_result["score"]
        for v in banned_result["violations"]:
            if v.get("suggestion"):
                suggestions.append(
                    f"Replace '{v['matched_text']}' with: {v['suggestion']}"
                )

        # 2. Character limit
        char_result = self.check_character_limit(text, platform)
        if not char_result["passed"]:
            violations.append(
                {
                    "category": "character_limit",
                    "matched_text": f"{char_result['char_count']} chars",
                    "rule": f"Exceeds {platform} limit of {char_result['limit']} chars by {char_result['over_by']}",
                }
            )
            suggestions.append(
                f"Shorten by {char_result['over_by']} characters for {platform}"
            )
            total_score += 15

        # 3. Product mentions
        product_result = self.check_product_mentions(text)
        if product_result["misspellings"]:
            for ms in product_result["misspellings"]:
                violations.append(
                    {
                        "category": "product_misspelling",
                        "matched_text": ms,
                        "rule": "Product name misspelled",
                    }
                )
                total_score += 20
        if product_result["requires_review"]:
            violations.append(
                {
                    "category": "product_mention",
                    "matched_text": ", ".join(product_result["mentions"]),
                    "rule": "Product mentions require human review",
                }
            )
            total_score += 10

        # 4. Sensitivity
        sensitivity_result = self.check_sensitivity(text)
        if sensitivity_result["do_not_engage"]:
            for topic in sensitivity_result["do_not_engage"]:
                violations.append(
                    {
                        "category": "sensitivity",
                        "matched_text": topic,
                        "rule": "Topic is on the do-not-engage list",
                    }
                )
                total_score += 30
        if sensitivity_result["empathy_mode"]:
            violations.append(
                {
                    "category": "empathy_required",
                    "matched_text": ", ".join(sensitivity_result["empathy_triggers"]),
                    "rule": "Content touches sensitive topic - use empathy mode, never pitch",
                }
            )
            total_score += 5

        total_score = min(100, total_score)
        passed = len([v for v in violations if v["category"] not in ("product_mention", "empathy_required")]) == 0

        return {
            "passed": passed,
            "violations": violations,
            "score": total_score,
            "suggestions": suggestions,
        }

    def update_blocklist(
        self, category: str, action: str, pattern: str
    ) -> None:
        """Add or remove a blocklist pattern, persisted via Supabase."""
        db = get_supabase_admin()

        # Get current risk_config
        result = db.table("risk_config").select("*").limit(1).execute()
        if not result.data:
            return

        config = result.data[0]
        blocklist = config.get("blocklist", {})

        if category not in blocklist:
            blocklist[category] = []

        if action == "add" and pattern not in blocklist[category]:
            blocklist[category].append(pattern)
        elif action == "remove" and pattern in blocklist[category]:
            blocklist[category].remove(pattern)

        db.table("risk_config").update({"blocklist": blocklist}).eq(
            "id", config["id"]
        ).execute()

        # Invalidate cached rules
        self._rules = None
