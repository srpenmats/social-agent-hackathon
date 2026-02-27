"""Tests for the EmbeddingsService."""

from __future__ import annotations

import math
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.ai.embeddings import EmbeddingsService, _cosine_similarity


class TestCosineSimilarity:
    def test_identical_vectors(self):
        v = [1.0, 0.0, 0.0]
        assert _cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert _cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert _cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_zero_vector(self):
        a = [0.0, 0.0]
        b = [1.0, 1.0]
        assert _cosine_similarity(a, b) == 0.0

    def test_known_similarity(self):
        a = [1.0, 1.0]
        b = [1.0, 0.0]
        expected = 1.0 / math.sqrt(2)
        assert _cosine_similarity(a, b) == pytest.approx(expected)


class TestEmbeddingsService:
    @patch("backend.services.ai.embeddings.get_settings")
    def test_init_warns_without_api_key(self, mock_settings, caplog):
        mock_settings.return_value = MagicMock(spec=[])
        import logging

        with caplog.at_level(logging.WARNING):
            svc = EmbeddingsService()
        assert svc.api_key is None

    @patch("backend.services.ai.embeddings.get_settings")
    def test_init_with_explicit_key(self, mock_settings):
        mock_settings.return_value = MagicMock(spec=[])
        svc = EmbeddingsService(api_key="test-key-123")
        assert svc.api_key == "test-key-123"

    @pytest.mark.asyncio
    @patch("backend.services.ai.embeddings.get_settings")
    async def test_create_embedding_no_key_raises(self, mock_settings):
        mock_settings.return_value = MagicMock(spec=[])
        svc = EmbeddingsService()
        with pytest.raises(RuntimeError, match="OpenAI API key not configured"):
            await svc.create_embedding("test")

    @pytest.mark.asyncio
    @patch("backend.services.ai.embeddings.get_settings")
    @patch("httpx.AsyncClient.post")
    async def test_create_embedding_success(self, mock_post, mock_settings):
        mock_settings.return_value = MagicMock(openai_api_key="test-key")
        embedding = [0.1] * 1536
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": embedding, "index": 0}]
        }
        mock_post.return_value = mock_response

        svc = EmbeddingsService(api_key="test-key")
        result = await svc.create_embedding("hello")
        assert len(result) == 1536
        assert result[0] == 0.1

    @pytest.mark.asyncio
    @patch("backend.services.ai.embeddings.get_settings")
    @patch("httpx.AsyncClient.post")
    async def test_batch_create_embeddings(self, mock_post, mock_settings):
        mock_settings.return_value = MagicMock(openai_api_key="test-key")
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2], "index": 0},
                {"embedding": [0.3, 0.4], "index": 1},
            ]
        }
        mock_post.return_value = mock_response

        svc = EmbeddingsService(api_key="test-key")
        results = await svc.batch_create_embeddings(["hello", "world"])
        assert len(results) == 2
        assert results[0] == [0.1, 0.2]
        assert results[1] == [0.3, 0.4]

    @pytest.mark.asyncio
    @patch("backend.services.ai.embeddings.get_settings")
    async def test_batch_create_empty_list(self, mock_settings):
        mock_settings.return_value = MagicMock(openai_api_key="test-key")
        svc = EmbeddingsService(api_key="test-key")
        results = await svc.batch_create_embeddings([])
        assert results == []

    @patch("backend.services.ai.embeddings.get_settings")
    @patch("backend.services.ai.embeddings.get_supabase_admin")
    def test_store_embedding(self, mock_db, mock_settings):
        mock_settings.return_value = MagicMock(openai_api_key="test-key")
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value.data = [
            {"id": 1, "document_name": "test.md"}
        ]
        mock_db.return_value.table.return_value = mock_table

        svc = EmbeddingsService(api_key="test-key")
        result = svc.store_embedding("test.md", "chunk text", 0, [0.1, 0.2], {})
        assert result["id"] == 1
        mock_table.insert.assert_called_once()

    @patch("backend.services.ai.embeddings.get_settings")
    @patch("backend.services.ai.embeddings.get_supabase_admin")
    def test_search_similar_python_fallback(self, mock_db, mock_settings):
        mock_settings.return_value = MagicMock(openai_api_key="test-key")

        # Make RPC fail so it falls back to Python
        mock_client = MagicMock()
        mock_client.rpc.side_effect = Exception("RPC not available")

        # Python fallback: return some embeddings
        mock_table = MagicMock()
        mock_table.select.return_value.execute.return_value.data = [
            {
                "id": 1,
                "document_name": "test.md",
                "chunk_text": "some text",
                "chunk_index": 0,
                "metadata": {},
                "embedding": [1.0, 0.0, 0.0],
            },
            {
                "id": 2,
                "document_name": "test2.md",
                "chunk_text": "other text",
                "chunk_index": 0,
                "metadata": {},
                "embedding": [0.0, 1.0, 0.0],
            },
        ]
        mock_client.table.return_value = mock_table
        mock_db.return_value = mock_client

        svc = EmbeddingsService(api_key="test-key")
        results = svc.search_similar([1.0, 0.0, 0.0], top_k=2, threshold=0.5)
        assert len(results) == 1  # Only the first one has similarity >= 0.5
        assert results[0]["id"] == 1
        assert results[0]["similarity"] == pytest.approx(1.0)

    @patch("backend.services.ai.embeddings.get_settings")
    @patch("backend.services.ai.embeddings.get_supabase_admin")
    def test_delete_all_embeddings(self, mock_db, mock_settings):
        mock_settings.return_value = MagicMock(openai_api_key="test-key")
        mock_table = MagicMock()
        mock_table.delete.return_value.neq.return_value.execute.return_value = None
        mock_db.return_value.table.return_value = mock_table

        svc = EmbeddingsService(api_key="test-key")
        svc.delete_all_embeddings()
        mock_table.delete.assert_called_once()
