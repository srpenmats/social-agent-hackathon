"""Embeddings service for creating, storing, and searching vector embeddings."""

from __future__ import annotations

import logging
import math
from typing import Any

import httpx

fromconfig import get_settings
fromdb.connection import get_supabase_admin

logger = logging.getLogger(__name__)

OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"
DEFAULT_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class EmbeddingsService:
    """Create embeddings via OpenAI API and store/search in Supabase pgvector."""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        settings = get_settings()
        self.api_key = api_key or getattr(settings, "openai_api_key", None)
        if not self.api_key:
            logger.warning(
                "No OpenAI API key configured. Embeddings service will fail on create_embedding calls. "
                "Set OPENAI_API_KEY in environment."
            )
        self.model = model

    async def create_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text."""
        if not self.api_key:
            raise RuntimeError(
                "OpenAI API key not configured. Set OPENAI_API_KEY in environment."
            )
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                OPENAI_EMBEDDINGS_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"input": text, "model": self.model},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]

    async def batch_create_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts in a single API call."""
        if not self.api_key:
            raise RuntimeError(
                "OpenAI API key not configured. Set OPENAI_API_KEY in environment."
            )
        if not texts:
            return []
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                OPENAI_EMBEDDINGS_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"input": texts, "model": self.model},
            )
            resp.raise_for_status()
            data = resp.json()
            # Sort by index to maintain order
            sorted_items = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in sorted_items]

    def store_embedding(
        self,
        doc_name: str,
        chunk_text: str,
        chunk_index: int,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Store an embedding in the brand_voice_embeddings table."""
        db = get_supabase_admin()
        row = {
            "document_name": doc_name,
            "chunk_text": chunk_text,
            "chunk_index": chunk_index,
            "embedding": embedding,
            "metadata": metadata or {},
        }
        result = db.table("brand_voice_embeddings").insert(row).execute()
        return result.data[0] if result.data else row

    def store_comment_embedding(
        self,
        comment_id: int,
        embedding: list[float],
    ) -> dict[str, Any]:
        """Store a comment embedding in the comment_embeddings table."""
        db = get_supabase_admin()
        row = {
            "comment_id": comment_id,
            "embedding": embedding,
        }
        result = db.table("comment_embeddings").insert(row).execute()
        return result.data[0] if result.data else row

    def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        """Search for similar brand voice chunks using cosine similarity.

        Tries Supabase RPC function first, falls back to Python-based similarity.
        """
        db = get_supabase_admin()
        try:
            result = db.rpc(
                "match_brand_voice_embeddings",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": threshold,
                    "match_count": top_k,
                },
            ).execute()
            if result.data:
                return result.data
        except Exception:
            logger.info(
                "RPC match_brand_voice_embeddings not available, using Python fallback"
            )

        return self._search_similar_python(query_embedding, top_k, threshold)

    def _search_similar_python(
        self,
        query_embedding: list[float],
        top_k: int,
        threshold: float,
    ) -> list[dict[str, Any]]:
        """Fallback: fetch all embeddings and compute similarity in Python."""
        db = get_supabase_admin()
        result = (
            db.table("brand_voice_embeddings")
            .select("id,document_name,chunk_text,chunk_index,metadata,embedding")
            .execute()
        )
        if not result.data:
            return []

        scored = []
        for row in result.data:
            emb = row.get("embedding")
            if not emb:
                continue
            sim = _cosine_similarity(query_embedding, emb)
            if sim >= threshold:
                scored.append(
                    {
                        "id": row["id"],
                        "document_name": row["document_name"],
                        "chunk_text": row["chunk_text"],
                        "chunk_index": row["chunk_index"],
                        "metadata": row.get("metadata", {}),
                        "similarity": sim,
                    }
                )

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    def delete_all_embeddings(self) -> None:
        """Delete all brand voice embeddings (for re-ingestion)."""
        db = get_supabase_admin()
        db.table("brand_voice_embeddings").delete().neq("id", 0).execute()
