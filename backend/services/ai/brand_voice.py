"""Brand voice ingestion and retrieval service.

Reads brand voice documents from the brand-voice/ directory, chunks them
appropriately (JSON by key, Markdown by header), creates embeddings, and
stores them in pgvector for RAG retrieval.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

fromdb.connection import get_supabase_admin
fromservices.ai.embeddings import EmbeddingsService

logger = logging.getLogger(__name__)

# Resolve brand-voice directory relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BRAND_VOICE_DIR = _PROJECT_ROOT / "brand-voice"

# File matching patterns (filenames contain colons)
FILE_PATTERNS: dict[str, str] = {
    "voice_config": "voice_config.json",
    "brand_voice": "brand_voice.md",
    "brand_guidelines": "brand_guidelines.md",
    "content_engine": "content_engine.md",
    "copywriting_reference": "copywriting_reference.md",
    "platform_playbooks": "platform_playbooks.md",
    "compliance_rails": "compliance_rails.json",
    "readme": "README.md",
    "cash_kitty": "cash_kitty_config.json",
}

# Document type classification
DOC_TYPES: dict[str, str] = {
    "voice_config": "voice",
    "brand_voice": "voice",
    "brand_guidelines": "guardrails",
    "content_engine": "content",
    "copywriting_reference": "content",
    "platform_playbooks": "content",
    "compliance_rails": "guardrails",
    "readme": "overview",
    "cash_kitty": "character",
}


def _find_file(directory: Path, suffix: str) -> Path | None:
    """Find a file in directory whose name ends with the given suffix."""
    if not directory.exists():
        return None
    for entry in directory.iterdir():
        if entry.name.endswith(suffix):
            return entry
    return None


def _read_file(path: Path) -> str:
    """Read file contents as text."""
    with open(path, encoding="utf-8") as f:
        return f.read()


class BrandVoiceService:
    """Ingest, chunk, embed, and retrieve brand voice documents."""

    def __init__(
        self,
        embeddings_service: EmbeddingsService | None = None,
        brand_voice_dir: Path | None = None,
    ):
        self.embeddings = embeddings_service or EmbeddingsService()
        self.brand_voice_dir = brand_voice_dir or BRAND_VOICE_DIR

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------

    def chunk_markdown_document(
        self,
        text: str,
        source_file: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> list[dict[str, Any]]:
        """Split markdown by ## and ### headers, preserving parent context."""
        chunks: list[dict[str, Any]] = []
        # Split on ## headers (keep the header with its content)
        sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Extract section header
            header_match = re.match(r"^(#{1,3})\s+(.+)$", section, re.MULTILINE)
            section_header = header_match.group(2).strip() if header_match else ""

            # If section is small enough, keep as one chunk
            if len(section) <= chunk_size:
                chunks.append(
                    {
                        "text": section,
                        "metadata": {
                            "source_file": source_file,
                            "section_header": section_header,
                            "doc_type": self._get_doc_type(source_file),
                        },
                    }
                )
                continue

            # Split large sections into sub-chunks by ### headers first
            subsections = re.split(r"(?=^### )", section, flags=re.MULTILINE)
            for subsection in subsections:
                subsection = subsection.strip()
                if not subsection:
                    continue

                sub_header_match = re.match(
                    r"^(#{1,3})\s+(.+)$", subsection, re.MULTILINE
                )
                sub_header = (
                    sub_header_match.group(2).strip() if sub_header_match else section_header
                )

                # If subsection fits, add as one chunk
                if len(subsection) <= chunk_size:
                    chunks.append(
                        {
                            "text": subsection,
                            "metadata": {
                                "source_file": source_file,
                                "section_header": sub_header,
                                "parent_header": section_header,
                                "doc_type": self._get_doc_type(source_file),
                            },
                        }
                    )
                    continue

                # Otherwise, split by paragraphs/lines with overlap
                words = subsection.split()
                start = 0
                while start < len(words):
                    end = min(start + chunk_size, len(words))
                    chunk_text = " ".join(words[start:end])
                    # Prepend parent header for context if not at start
                    if start > 0 and section_header:
                        chunk_text = f"## {section_header}\n### {sub_header}\n{chunk_text}"
                    chunks.append(
                        {
                            "text": chunk_text,
                            "metadata": {
                                "source_file": source_file,
                                "section_header": sub_header,
                                "parent_header": section_header,
                                "doc_type": self._get_doc_type(source_file),
                            },
                        }
                    )
                    start = end - overlap if end < len(words) else end

        return chunks

    def chunk_json_document(
        self,
        data: dict[str, Any],
        source_file: str,
    ) -> list[dict[str, Any]]:
        """Extract each top-level key as a separate chunk with metadata."""
        chunks: list[dict[str, Any]] = []
        for key, value in data.items():
            text = json.dumps(value, indent=2, ensure_ascii=False)
            chunks.append(
                {
                    "text": f"{key}: {text}",
                    "metadata": {
                        "source_file": source_file,
                        "section_header": key,
                        "doc_type": self._get_doc_type(source_file),
                        "key_path": key,
                    },
                }
            )
            # If the value is a large dict, also create sub-chunks for nested keys
            if isinstance(value, dict) and len(text) > 1000:
                for sub_key, sub_value in value.items():
                    sub_text = json.dumps(sub_value, indent=2, ensure_ascii=False)
                    chunks.append(
                        {
                            "text": f"{key}.{sub_key}: {sub_text}",
                            "metadata": {
                                "source_file": source_file,
                                "section_header": f"{key}.{sub_key}",
                                "parent_header": key,
                                "doc_type": self._get_doc_type(source_file),
                                "key_path": f"{key}.{sub_key}",
                            },
                        }
                    )
        return chunks

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    async def ingest_document(self, file_path: Path) -> int:
        """Process a single document: read, chunk, embed, store. Returns chunk count."""
        content = _read_file(file_path)
        filename = file_path.name

        if filename.endswith(".json"):
            data = json.loads(content)
            chunks = self.chunk_json_document(data, filename)
        else:
            chunks = self.chunk_markdown_document(content, filename)

        if not chunks:
            return 0

        # Batch embed all chunks
        texts = [c["text"] for c in chunks]
        embeddings = await self.embeddings.batch_create_embeddings(texts)

        # Store each chunk
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            self.embeddings.store_embedding(
                doc_name=filename,
                chunk_text=chunk["text"],
                chunk_index=idx,
                embedding=embedding,
                metadata=chunk["metadata"],
            )

        logger.info("Ingested %s: %d chunks", filename, len(chunks))
        return len(chunks)

    async def ingest_all_documents(self) -> dict[str, int]:
        """Read all brand-voice files, chunk, embed, and store."""
        results: dict[str, int] = {}
        for doc_key, suffix in FILE_PATTERNS.items():
            file_path = _find_file(self.brand_voice_dir, suffix)
            if file_path is None:
                logger.warning("Brand voice file not found: *%s", suffix)
                results[doc_key] = 0
                continue
            count = await self.ingest_document(file_path)
            results[doc_key] = count
        return results

    async def refresh_embeddings(self) -> dict[str, int]:
        """Delete all existing embeddings and re-ingest all documents."""
        self.embeddings.delete_all_embeddings()
        return await self.ingest_all_documents()

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    async def get_voice_context(
        self, query: str, platform: str | None = None
    ) -> str:
        """Retrieve relevant brand voice context for a given query/topic."""
        query_embedding = await self.embeddings.create_embedding(query)
        results = self.embeddings.search_similar(
            query_embedding, top_k=8, threshold=0.5
        )

        # Filter by platform if specified (platform playbook chunks)
        if platform:
            platform_results = [
                r
                for r in results
                if platform.lower() in r.get("chunk_text", "").lower()
                or r.get("metadata", {}).get("section_header", "").lower()
                == platform.lower()
            ]
            # Mix platform-specific results with general results
            general = [r for r in results if r not in platform_results]
            results = platform_results[:4] + general[:4]

        context_parts = []
        for r in results:
            context_parts.append(r.get("chunk_text", ""))

        return "\n\n---\n\n".join(context_parts)

    def get_platform_playbook(self, platform: str) -> str:
        """Retrieve platform-specific rules from the playbooks file."""
        file_path = _find_file(self.brand_voice_dir, "platform_playbooks.md")
        if not file_path:
            return ""

        content = _read_file(file_path)
        # Extract the platform section
        platform_map = {
            "tiktok": "TikTok",
            "instagram": "Instagram",
            "youtube": "YouTube",
            "x": "X (Twitter)",
        }
        platform_name = platform_map.get(platform.lower(), platform)

        # Find the section for this platform
        pattern = rf"^## {re.escape(platform_name)}$(.*?)(?=^## |\Z)"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            return f"## {platform_name}\n{match.group(1).strip()}"
        return ""

    def get_banned_words(self) -> dict[str, Any]:
        """Parse and return all banned words from guidelines and compliance rails."""
        absolute_bans: list[str] = []
        contextual_bans: list[dict[str, str]] = []

        # From compliance_rails.json
        rails_path = _find_file(self.brand_voice_dir, "compliance_rails.json")
        if rails_path:
            rails = json.loads(_read_file(rails_path))
            absolute_bans.extend(rails.get("banned_words", {}).get("absolute", []))
            contextual_bans.extend(
                rails.get("banned_words", {}).get("contextual", [])
            )

        # From brand_guidelines.md - parse the absolute bans table
        guidelines_path = _find_file(self.brand_voice_dir, "brand_guidelines.md")
        if guidelines_path:
            content = _read_file(guidelines_path)
            # Extract terms from the markdown table rows
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("|") and "**" in line:
                    # Parse table cells
                    cells = [c.strip() for c in line.split("|") if c.strip()]
                    if len(cells) >= 2:
                        terms_cell = cells[1]  # Second column has the terms
                        terms = [t.strip() for t in terms_cell.split(",")]
                        for term in terms:
                            cleaned = term.strip()
                            if cleaned and cleaned not in absolute_bans:
                                absolute_bans.append(cleaned)

        # Deduplicate
        absolute_bans = list(dict.fromkeys(absolute_bans))

        return {
            "absolute": absolute_bans,
            "contextual": contextual_bans,
        }

    def get_personality_config(self) -> dict[str, Any]:
        """Return the core personality archetype and voice pillars."""
        config_path = _find_file(self.brand_voice_dir, "voice_config.json")
        if not config_path:
            return {}

        config = json.loads(_read_file(config_path))
        return {
            "personality": config.get("personality", {}),
            "positioning": config.get("positioning", {}),
            "voice_pillars": config.get("voice_pillars", []),
            "tone_guardrails": config.get("tone_guardrails", {}),
            "voice_features": config.get("voice_features", []),
            "platform_configs": config.get("platform_configs", {}),
            "content_scoring": config.get("content_scoring", {}),
        }

    def get_compliance_rails(self) -> dict[str, Any]:
        """Return the full compliance rails configuration."""
        rails_path = _find_file(self.brand_voice_dir, "compliance_rails.json")
        if not rails_path:
            return {}
        return json.loads(_read_file(rails_path))

    def get_cash_kitty_config(self) -> dict[str, Any]:
        """Return the Cash Kitty character configuration."""
        config_path = _find_file(self.brand_voice_dir, "cash_kitty_config.json")
        if not config_path:
            return {}
        return json.loads(_read_file(config_path))

    def get_copywriting_reference(self) -> str:
        """Return the copywriting reference document for few-shot examples."""
        ref_path = _find_file(self.brand_voice_dir, "copywriting_reference.md")
        if not ref_path:
            return ""
        return _read_file(ref_path)

    async def update_voice_guide(self, content: str) -> None:
        """Update voice guide in DB and re-embed."""
        db = get_supabase_admin()
        db.table("voice_config").update(
            {"voice_guide_md": content}
        ).eq("id", 1).execute()
        # Re-ingest the voice documents to refresh embeddings
        await self.refresh_embeddings()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_doc_type(self, filename: str) -> str:
        """Classify a file into its document type."""
        for key, suffix in FILE_PATTERNS.items():
            if filename.endswith(suffix):
                return DOC_TYPES.get(key, "unknown")
        return "unknown"
