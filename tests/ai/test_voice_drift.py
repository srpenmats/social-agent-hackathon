"""Tests for the VoiceDriftMonitor."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.ai.voice_drift import (
    DRIFT_ALERT_THRESHOLD,
    SEVERE_DRIFT_THRESHOLD,
    VoiceDriftMonitor,
    _compute_trend,
)


class TestComputeTrend:
    def test_improving(self):
        scores = [0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
        assert _compute_trend(scores) == "improving"

    def test_declining(self):
        scores = [0.85, 0.80, 0.75, 0.7, 0.65, 0.6]
        assert _compute_trend(scores) == "declining"

    def test_stable(self):
        scores = [0.75, 0.76, 0.74, 0.75, 0.76, 0.75]
        assert _compute_trend(scores) == "stable"

    def test_too_few_scores(self):
        assert _compute_trend([0.8]) == "stable"
        assert _compute_trend([0.8, 0.7]) == "stable"

    def test_empty(self):
        assert _compute_trend([]) == "stable"


@pytest.fixture
def mock_embeddings():
    svc = MagicMock()
    svc.create_embedding = AsyncMock(return_value=[0.5] * 10)
    svc.store_comment_embedding = MagicMock()
    return svc


@pytest.fixture
def mock_brand_voice():
    svc = MagicMock()
    svc.refresh_embeddings = AsyncMock()
    return svc


class TestVoiceDriftMonitor:
    @pytest.mark.asyncio
    async def test_compute_drift_score(self, mock_embeddings, mock_brand_voice):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )

        # Mock brand voice embeddings
        with patch.object(monitor, "_get_brand_voice_embeddings") as mock_get:
            mock_get.return_value = [
                {"id": 1, "embedding": [0.5] * 10},
                {"id": 2, "embedding": [0.5] * 10},
            ]
            score = await monitor.compute_drift_score("Test comment")
            assert score == pytest.approx(1.0)  # Identical vectors

    @pytest.mark.asyncio
    async def test_compute_drift_score_no_brand_embeddings(
        self, mock_embeddings, mock_brand_voice
    ):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )
        with patch.object(monitor, "_get_brand_voice_embeddings") as mock_get:
            mock_get.return_value = []
            score = await monitor.compute_drift_score("Test comment")
            assert score == 1.0  # Default to aligned

    @pytest.mark.asyncio
    async def test_track_comment(self, mock_embeddings, mock_brand_voice):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )
        with patch.object(monitor, "_get_brand_voice_embeddings") as mock_get:
            mock_get.return_value = [{"id": 1, "embedding": [0.5] * 10}]
            with patch("backend.services.ai.voice_drift.get_supabase_admin") as mock_db:
                mock_table = MagicMock()
                mock_table.update.return_value.eq.return_value.execute.return_value = None
                mock_db.return_value.table.return_value = mock_table

                score = await monitor.track_comment(42, "Great comment")
                assert score == pytest.approx(1.0)
                mock_embeddings.store_comment_embedding.assert_called_once_with(
                    42, [0.5] * 10
                )

    def test_get_drift_timeline(self, mock_embeddings, mock_brand_voice):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )
        with patch("backend.services.ai.voice_drift.get_supabase_admin") as mock_db:
            mock_table = MagicMock()
            mock_table.select.return_value.gte.return_value.not_.is_.return_value.order.return_value.execute.return_value.data = [
                {"created_at": "2026-02-01T10:00:00Z", "drift_score": 0.8},
                {"created_at": "2026-02-01T14:00:00Z", "drift_score": 0.85},
                {"created_at": "2026-02-02T10:00:00Z", "drift_score": 0.75},
            ]
            mock_db.return_value.table.return_value = mock_table

            result = monitor.get_drift_timeline(days=30)
            assert result["dates"] == ["2026-02-01", "2026-02-02"]
            assert len(result["scores"]) == 2
            # Feb 1 avg: (0.8 + 0.85) / 2 = 0.825
            assert result["scores"][0] == pytest.approx(0.825)
            # Feb 2 avg: 0.75
            assert result["scores"][1] == pytest.approx(0.75)

    def test_get_drift_timeline_empty(self, mock_embeddings, mock_brand_voice):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )
        with patch("backend.services.ai.voice_drift.get_supabase_admin") as mock_db:
            mock_table = MagicMock()
            mock_table.select.return_value.gte.return_value.not_.is_.return_value.order.return_value.execute.return_value.data = []
            mock_db.return_value.table.return_value = mock_table

            result = monitor.get_drift_timeline()
            assert result["dates"] == []
            assert result["scores"] == []
            assert result["trend"] == "stable"

    def test_get_current_drift(self, mock_embeddings, mock_brand_voice):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )
        with patch("backend.services.ai.voice_drift.get_supabase_admin") as mock_db:
            mock_table = MagicMock()
            mock_table.select.return_value.not_.is_.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"comment_id": 1, "drift_score": 0.85, "created_at": "2026-02-01T10:00:00Z"},
                {"comment_id": 2, "drift_score": 0.4, "created_at": "2026-02-01T12:00:00Z"},
                {"comment_id": 3, "drift_score": 0.78, "created_at": "2026-02-01T14:00:00Z"},
            ]
            mock_db.return_value.table.return_value = mock_table

            result = monitor.get_current_drift()
            assert result["comment_count"] == 3
            assert result["min_score"] == 0.4
            assert result["max_score"] == 0.85
            # Outlier: comment_id=2 with 0.4 < SEVERE_DRIFT_THRESHOLD
            assert len(result["outliers"]) == 1
            assert result["outliers"][0]["comment_id"] == 2

    def test_get_current_drift_empty(self, mock_embeddings, mock_brand_voice):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )
        with patch("backend.services.ai.voice_drift.get_supabase_admin") as mock_db:
            mock_table = MagicMock()
            mock_table.select.return_value.not_.is_.return_value.order.return_value.limit.return_value.execute.return_value.data = []
            mock_db.return_value.table.return_value = mock_table

            result = monitor.get_current_drift()
            assert result["avg_score"] == 1.0
            assert result["comment_count"] == 0

    def test_run_daily_check_no_alert(self, mock_embeddings, mock_brand_voice):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )
        with patch.object(monitor, "get_current_drift") as mock_current:
            mock_current.return_value = {
                "avg_score": 0.85,
                "comment_count": 50,
                "outliers": [],
            }
            snapshot = monitor.run_daily_check()
            assert snapshot["alert"] is None
            assert snapshot["avg_drift_score"] == 0.85

    def test_run_daily_check_warning_alert(self, mock_embeddings, mock_brand_voice):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )
        with patch.object(monitor, "get_current_drift") as mock_current:
            mock_current.return_value = {
                "avg_score": 0.65,
                "comment_count": 50,
                "outliers": [],
            }
            with patch.object(monitor, "_store_alert"):
                snapshot = monitor.run_daily_check()
                assert snapshot["alert"] is not None
                assert snapshot["alert"]["severity"] == "warning"

    def test_run_daily_check_critical_alert(self, mock_embeddings, mock_brand_voice):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )
        with patch.object(monitor, "get_current_drift") as mock_current:
            mock_current.return_value = {
                "avg_score": 0.4,
                "comment_count": 50,
                "outliers": [{"comment_id": 1}],
            }
            with patch.object(monitor, "_store_alert"):
                snapshot = monitor.run_daily_check()
                assert snapshot["alert"] is not None
                assert snapshot["alert"]["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_recalibrate(self, mock_embeddings, mock_brand_voice):
        monitor = VoiceDriftMonitor(
            embeddings_service=mock_embeddings,
            brand_voice_service=mock_brand_voice,
        )
        with patch("backend.services.ai.voice_drift.get_supabase_admin") as mock_db:
            mock_table = MagicMock()
            # Return some comment embeddings
            mock_table.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"id": 1, "comment_id": 10, "embedding": [0.5] * 10},
                {"id": 2, "comment_id": 20, "embedding": [0.5] * 10},
            ]
            mock_table.update.return_value.eq.return_value.execute.return_value = None
            mock_db.return_value.table.return_value = mock_table

            with patch.object(monitor, "_get_brand_voice_embeddings") as mock_get:
                mock_get.return_value = [{"id": 1, "embedding": [0.5] * 10}]

                result = await monitor.recalibrate()
                assert result["recalibrated"] == 2
                mock_brand_voice.refresh_embeddings.assert_called_once()
