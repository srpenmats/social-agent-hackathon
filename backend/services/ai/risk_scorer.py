"""3-layer risk scoring engine for comment evaluation.

Layer 1: Blocklist scan (ComplianceChecker) - 40% weight
Layer 2: Context contamination (video/topic safety) - 30% weight
Layer 3: AI judge (Claude-based assessment) - 30% weight
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

fromconfig import get_settings
fromdb.connection import get_supabase_admin
fromservices.ai.compliance import ComplianceChecker

logger = logging.getLogger(__name__)

CLAUDE_MODEL = "claude-sonnet-4-5-20250514"

# Default risk routing thresholds
DEFAULT_AUTO_APPROVE_MAX = 30
DEFAULT_REVIEW_MAX = 65

# Layer weights
WEIGHT_BLOCKLIST = 0.40
WEIGHT_CONTEXT = 0.30
WEIGHT_AI_JUDGE = 0.30

# Sensitive topics that increase context risk
CONTROVERSIAL_TOPICS = [
    "politics",
    "religion",
    "tragedy",
    "disaster",
    "shooting",
    "war",
    "terrorism",
    "scandal",
    "lawsuit",
    "investigation",
    "discrimination",
    "abuse",
]

RISKY_HASHTAGS = [
    "#politics",
    "#election",
    "#controversy",
    "#scandal",
    "#boycott",
    "#cancelled",
    "#canceled",
    "#protest",
    "#riot",
    "#conspiracy",
]

AI_JUDGE_SYSTEM_PROMPT = """You are a brand safety risk assessor for MoneyLion, a fintech company.
Your job is to evaluate whether a social media comment could damage MoneyLion's brand reputation.

Evaluate on these dimensions:
1. Could this be interpreted as financial advice? (high risk)
2. Does it make promises or guarantees? (high risk)
3. Could it be seen as insensitive or offensive? (high risk)
4. Does it disparage competitors? (medium risk)
5. Could it attract regulatory scrutiny? (high risk)
6. Is it appropriate for the context of the video/post? (varies)
7. Does it maintain professional brand standards while being casual? (low-medium risk)

Respond with ONLY a JSON object:
{
    "score": <0-100 integer, higher = more risky>,
    "reasoning": "<1-2 sentence explanation>"
}
"""


class RiskScorer:
    """3-layer risk scoring system for evaluating comments before publishing."""

    def __init__(self, compliance_checker: ComplianceChecker | None = None):
        self.compliance = compliance_checker or ComplianceChecker()
        settings = get_settings()
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def score_comment(
        self,
        comment_text: str,
        video_context: dict[str, Any],
        platform: str,
    ) -> dict[str, Any]:
        """Full 3-layer risk assessment.

        Returns:
            {
                "total_score": int (0-100),
                "blocklist_score": int (0-100),
                "context_score": int (0-100),
                "ai_judge_score": int (0-100),
                "reasoning": str,
                "routing_decision": str,
                "violations": list,
            }
        """
        # Layer 1: Blocklist/compliance scan
        compliance_result = self.compliance.full_compliance_check(
            comment_text, platform
        )
        blocklist_score = compliance_result["score"]

        # Layer 2: Context contamination
        context_score = self.score_context(video_context)

        # Layer 3: AI judge
        ai_result = await self.ai_judge(comment_text, video_context)
        ai_judge_score = ai_result.get("score", 50)

        # Weighted total
        total_score = int(
            blocklist_score * WEIGHT_BLOCKLIST
            + context_score * WEIGHT_CONTEXT
            + ai_judge_score * WEIGHT_AI_JUDGE
        )
        total_score = min(100, max(0, total_score))

        # Build reasoning
        reasoning_parts = []
        if blocklist_score > 0:
            violations = compliance_result.get("violations", [])
            viol_summary = "; ".join(
                v.get("rule", "")[:60] for v in violations[:3]
            )
            reasoning_parts.append(f"Compliance: {viol_summary}")
        if context_score > 30:
            reasoning_parts.append(f"Context risk: {context_score}/100")
        if ai_result.get("reasoning"):
            reasoning_parts.append(f"AI judge: {ai_result['reasoning']}")
        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "Low risk"

        # Route the comment
        routing_decision = self.route_comment(total_score)

        # Override: product mentions always require review
        product_violations = [
            v
            for v in compliance_result.get("violations", [])
            if v.get("category") == "product_mention"
        ]
        if product_violations and routing_decision == "auto_approve":
            routing_decision = "human_review"

        return {
            "total_score": total_score,
            "blocklist_score": blocklist_score,
            "context_score": context_score,
            "ai_judge_score": ai_judge_score,
            "reasoning": reasoning,
            "routing_decision": routing_decision,
            "violations": compliance_result.get("violations", []),
        }

    def route_comment(self, risk_score: int) -> str:
        """Determine routing based on current thresholds."""
        auto_approve_max, review_max = self._get_thresholds()

        if risk_score <= auto_approve_max:
            return "auto_approve"
        elif risk_score <= review_max:
            return "human_review"
        else:
            return "auto_discard"

    def score_context(self, video_context: dict[str, Any]) -> int:
        """Layer 2: Assess video/post context risk (0-100)."""
        score = 0

        # Check description for controversial topics
        description = (video_context.get("description") or "").lower()
        title = (video_context.get("title") or "").lower()
        combined_text = f"{title} {description}"

        for topic in CONTROVERSIAL_TOPICS:
            if topic in combined_text:
                score += 15

        # Check hashtags
        hashtags = video_context.get("hashtags", [])
        for tag in hashtags:
            if tag.lower() in RISKY_HASHTAGS:
                score += 10

        # Check classification
        classification = (video_context.get("classification") or "").lower()
        if "sensitive" in classification or "controversial" in classification:
            score += 25

        return min(100, score)

    async def ai_judge(
        self, comment_text: str, video_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Layer 3: Claude-based risk assessment (0-100 + reasoning)."""
        user_prompt = (
            f"Video/post context: {json.dumps(video_context, default=str)}\n\n"
            f"Proposed comment: {comment_text}\n\n"
            f"Could this comment damage MoneyLion's brand? Score 0-100 with reasoning."
        )

        try:
            message = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=256,
                system=AI_JUDGE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            response_text = message.content[0].text.strip()

            # Handle markdown code blocks
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                json_lines = [l for l in lines if not l.startswith("```")]
                response_text = "\n".join(json_lines)

            result = json.loads(response_text)
            return {
                "score": min(100, max(0, int(result.get("score", 50)))),
                "reasoning": result.get("reasoning", ""),
            }
        except Exception as e:
            logger.warning("AI judge failed: %s. Defaulting to score 50.", e)
            return {"score": 50, "reasoning": f"AI judge unavailable: {e}"}

    def get_risk_analytics(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """Aggregate risk scoring stats for the dashboard."""
        db = get_supabase_admin()
        result = (
            db.table("risk_scores")
            .select("total_score,routing_decision,scored_at")
            .gte("scored_at", start_date)
            .lte("scored_at", end_date)
            .execute()
        )

        if not result.data:
            return {
                "total_scored": 0,
                "avg_score": 0,
                "routing_breakdown": {},
                "score_distribution": {},
            }

        scores = result.data
        total = len(scores)
        avg_score = sum(s["total_score"] for s in scores) / total

        routing_counts: dict[str, int] = {}
        for s in scores:
            decision = s.get("routing_decision", "unknown")
            routing_counts[decision] = routing_counts.get(decision, 0) + 1

        # Score distribution in buckets
        buckets = {"0-30": 0, "31-65": 0, "66-100": 0}
        for s in scores:
            sc = s["total_score"]
            if sc <= 30:
                buckets["0-30"] += 1
            elif sc <= 65:
                buckets["31-65"] += 1
            else:
                buckets["66-100"] += 1

        return {
            "total_scored": total,
            "avg_score": round(avg_score, 1),
            "routing_breakdown": routing_counts,
            "score_distribution": buckets,
        }

    def _get_thresholds(self) -> tuple[int, int]:
        """Load risk thresholds from risk_config table."""
        try:
            db = get_supabase_admin()
            result = db.table("risk_config").select("auto_approve_max,review_max").limit(1).execute()
            if result.data:
                config = result.data[0]
                return (
                    config.get("auto_approve_max", DEFAULT_AUTO_APPROVE_MAX),
                    config.get("review_max", DEFAULT_REVIEW_MAX),
                )
        except Exception as e:
            logger.warning("Failed to load risk thresholds: %s. Using defaults.", e)

        return DEFAULT_AUTO_APPROVE_MAX, DEFAULT_REVIEW_MAX
