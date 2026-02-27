"""Voice drift monitoring service.

Tracks cosine similarity between generated comments and brand voice
embeddings over time, detecting when the agent's output drifts away
from the intended brand voice.
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Any

fromdb.connection import get_supabase_admin
fromservices.ai.brand_voice import BrandVoiceService
fromservices.ai.embeddings import EmbeddingsService, _cosine_similarity

logger = logging.getLogger(__name__)

DRIFT_ALERT_THRESHOLD = 0.7
SEVERE_DRIFT_THRESHOLD = 0.5
RECENT_COMMENTS_COUNT = 50


class VoiceDriftMonitor:
    """Track how closely generated comments align with brand voice over time."""

    def __init__(
        self,
        embeddings_service: EmbeddingsService | None = None,
        brand_voice_service: BrandVoiceService | None = None,
    ):
        self.embeddings = embeddings_service or EmbeddingsService()
        self.brand_voice = brand_voice_service or BrandVoiceService(
            embeddings_service=self.embeddings
        )

    async def compute_drift_score(self, comment_text: str) -> float:
        """Calculate cosine similarity between comment and brand voice embeddings.

        Returns 0.0-1.0 (1.0 = perfect alignment with brand voice).
        """
        # Create embedding for the comment
        comment_embedding = await self.embeddings.create_embedding(comment_text)

        # Get all brand voice embeddings
        brand_embeddings = self._get_brand_voice_embeddings()
        if not brand_embeddings:
            logger.warning("No brand voice embeddings found for drift calculation")
            return 1.0  # Assume aligned if no reference exists

        # Compute average similarity against all brand voice chunks
        similarities = []
        for be in brand_embeddings:
            emb = be.get("embedding")
            if emb:
                sim = _cosine_similarity(comment_embedding, emb)
                similarities.append(sim)

        if not similarities:
            return 1.0

        return sum(similarities) / len(similarities)

    async def track_comment(self, comment_id: int, comment_text: str) -> float:
        """Track a generated comment's drift from brand voice.

        Creates embedding, stores it, computes drift score, stores the score.
        Returns the drift score.
        """
        # Create and store the comment embedding
        embedding = await self.embeddings.create_embedding(comment_text)
        self.embeddings.store_comment_embedding(comment_id, embedding)

        # Compute drift score
        brand_embeddings = self._get_brand_voice_embeddings()
        if not brand_embeddings:
            return 1.0

        similarities = []
        for be in brand_embeddings:
            emb = be.get("embedding")
            if emb:
                sim = _cosine_similarity(embedding, emb)
                similarities.append(sim)

        drift_score = sum(similarities) / len(similarities) if similarities else 1.0

        # Store the drift score as metadata on the comment embedding
        try:
            db = get_supabase_admin()
            db.table("comment_embeddings").update(
                {"drift_score": drift_score}
            ).eq("comment_id", comment_id).execute()
        except Exception as e:
            logger.warning("Failed to store drift score: %s", e)

        return drift_score

    def get_drift_timeline(self, days: int = 30) -> dict[str, Any]:
        """Return daily average drift scores for chart visualization.

        Returns:
            {
                "dates": ["2026-02-01", ...],
                "scores": [0.82, 0.79, ...],
                "trend": "improving" | "declining" | "stable",
            }
        """
        db = get_supabase_admin()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        result = (
            db.table("comment_embeddings")
            .select("created_at,drift_score")
            .gte("created_at", cutoff)
            .not_.is_("drift_score", "null")
            .order("created_at")
            .execute()
        )

        if not result.data:
            return {"dates": [], "scores": [], "trend": "stable"}

        # Group by date
        daily: dict[str, list[float]] = {}
        for row in result.data:
            date_str = row["created_at"][:10]  # YYYY-MM-DD
            score = row.get("drift_score", 0)
            if date_str not in daily:
                daily[date_str] = []
            daily[date_str].append(score)

        dates = sorted(daily.keys())
        scores = [
            round(sum(daily[d]) / len(daily[d]), 3) for d in dates
        ]

        # Determine trend
        trend = _compute_trend(scores)

        return {"dates": dates, "scores": scores, "trend": trend}

    def get_current_drift(self) -> dict[str, Any]:
        """Compute drift score for the last N comments.

        Returns avg, min, max, and outlier comments.
        """
        db = get_supabase_admin()
        result = (
            db.table("comment_embeddings")
            .select("comment_id,drift_score,created_at")
            .not_.is_("drift_score", "null")
            .order("created_at", desc=True)
            .limit(RECENT_COMMENTS_COUNT)
            .execute()
        )

        if not result.data:
            return {
                "avg_score": 1.0,
                "min_score": 1.0,
                "max_score": 1.0,
                "comment_count": 0,
                "outliers": [],
            }

        scores = [r["drift_score"] for r in result.data]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)

        # Outliers: comments with drift score below SEVERE_DRIFT_THRESHOLD
        outliers = [
            {
                "comment_id": r["comment_id"],
                "drift_score": r["drift_score"],
                "created_at": r["created_at"],
            }
            for r in result.data
            if r["drift_score"] < SEVERE_DRIFT_THRESHOLD
        ]

        return {
            "avg_score": round(avg_score, 3),
            "min_score": round(min_score, 3),
            "max_score": round(max_score, 3),
            "comment_count": len(scores),
            "outliers": outliers,
        }

    def run_daily_check(self) -> dict[str, Any]:
        """Background job: check drift, create alerts if needed.

        Returns daily snapshot with alert status.
        """
        current = self.get_current_drift()
        avg_score = current["avg_score"]

        alert = None
        if avg_score < SEVERE_DRIFT_THRESHOLD:
            alert = {
                "severity": "critical",
                "message": f"Voice drift severe: avg similarity {avg_score:.2f} (threshold: {SEVERE_DRIFT_THRESHOLD})",
            }
        elif avg_score < DRIFT_ALERT_THRESHOLD:
            alert = {
                "severity": "warning",
                "message": f"Voice drift detected: avg similarity {avg_score:.2f} (threshold: {DRIFT_ALERT_THRESHOLD})",
            }

        # Store alert in system_config if needed
        if alert:
            self._store_alert(alert)

        snapshot = {
            "date": datetime.now(timezone.utc).isoformat()[:10],
            "avg_drift_score": avg_score,
            "comment_count": current["comment_count"],
            "outlier_count": len(current["outliers"]),
            "alert": alert,
        }

        return snapshot

    async def recalibrate(self) -> dict[str, Any]:
        """Re-compute all drift scores after voice config change.

        1. Re-embed voice documents
        2. Re-score all recent comments against new embeddings
        """
        # Re-embed voice documents
        await self.brand_voice.refresh_embeddings()

        # Get all recent comment embeddings
        db = get_supabase_admin()
        result = (
            db.table("comment_embeddings")
            .select("id,comment_id,embedding")
            .order("created_at", desc=True)
            .limit(200)
            .execute()
        )

        if not result.data:
            return {"recalibrated": 0}

        # Get fresh brand voice embeddings
        brand_embeddings = self._get_brand_voice_embeddings()
        if not brand_embeddings:
            return {"recalibrated": 0}

        brand_embs = [be["embedding"] for be in brand_embeddings if be.get("embedding")]

        recalibrated = 0
        for row in result.data:
            comment_emb = row.get("embedding")
            if not comment_emb:
                continue

            # Compute new drift score
            similarities = [_cosine_similarity(comment_emb, be) for be in brand_embs]
            new_score = sum(similarities) / len(similarities) if similarities else 1.0

            try:
                db.table("comment_embeddings").update(
                    {"drift_score": round(new_score, 4)}
                ).eq("id", row["id"]).execute()
                recalibrated += 1
            except Exception as e:
                logger.warning("Failed to update drift score for %s: %s", row["id"], e)

        return {"recalibrated": recalibrated}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_brand_voice_embeddings(self) -> list[dict[str, Any]]:
        """Fetch all brand voice embeddings from the database."""
        try:
            db = get_supabase_admin()
            result = (
                db.table("brand_voice_embeddings")
                .select("id,embedding")
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            logger.warning("Failed to fetch brand voice embeddings: %s", e)
            return []

    def _store_alert(self, alert: dict[str, str]) -> None:
        """Store a drift alert in system_config."""
        try:
            db = get_supabase_admin()
            db.table("system_config").upsert(
                {
                    "key": "voice_drift_alert",
                    "value": {
                        "alert": alert,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                },
                on_conflict="key",
            ).execute()
        except Exception as e:
            logger.warning("Failed to store drift alert: %s", e)


def _compute_trend(scores: list[float]) -> str:
    """Determine trend direction from a list of daily scores."""
    if len(scores) < 3:
        return "stable"

    # Compare first half avg to second half avg
    mid = len(scores) // 2
    first_half = sum(scores[:mid]) / mid
    second_half = sum(scores[mid:]) / (len(scores) - mid)

    diff = second_half - first_half
    if diff > 0.03:
        return "improving"
    elif diff < -0.03:
        return "declining"
    return "stable"
