"""Tests for the BrandVoiceService."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.ai.brand_voice import BrandVoiceService


@pytest.fixture
def brand_voice_dir(tmp_path: Path) -> Path:
    """Create a temporary brand voice directory with test files."""
    # voice_config.json
    voice_config = {
        "personality": {
            "archetype": "The Irreverent Maverick",
            "description": "A challenger brand persona",
        },
        "positioning": {"statement": "We are the trusted source"},
        "voice_pillars": [
            {"id": "live_richly", "name": "Live Richly", "tone": "Confident"}
        ],
        "tone_guardrails": {"we_are": {"confident": ["proud"]}},
        "voice_features": ["Candid language"],
        "platform_configs": {
            "tiktok": {"formality": 2, "humor": 8},
            "instagram": {"formality": 4, "humor": 7},
        },
        "content_scoring": {"target_score": 4},
    }
    (tmp_path / "test:voice:voice_config.json").write_text(
        json.dumps(voice_config), encoding="utf-8"
    )

    # brand_voice.md
    brand_voice_md = """# MoneyLion Brand Voice Definition

## Brand Personality: The Irreverent Maverick

MoneyLion is the Irreverent Maverick.

## The Four Voice Pillars

### 1. Live Richly

Confident and inspiring.

### 2. Share The Secret

Enlightened and assured.

## Tone Guardrails

We are confident, not arrogant.
"""
    (tmp_path / "test:voice:brand_voice.md").write_text(
        brand_voice_md, encoding="utf-8"
    )

    # brand_guidelines.md
    brand_guidelines_md = """# MoneyLion Brand Guidelines

## 1. Banned Words & Phrases

### Absolute Bans

| Category | Banned Terms |
|---|---|
| **Financial terms** | free, guaranteed, borrow, payday |
| **Lion-themed** | roar, pounce, lion, pride |

## 2. Product Naming Rules

Use MoneyLion before product names.
"""
    (tmp_path / "test:voice:brand_guidelines.md").write_text(
        brand_guidelines_md, encoding="utf-8"
    )

    # compliance_rails.json
    compliance_rails = {
        "banned_words": {
            "absolute": ["free", "guaranteed", "borrow", "loan", "debt"],
            "contextual": [
                {
                    "word": "checking account",
                    "banned_context": "Describing RoarMoney",
                    "replacement": "banking account",
                }
            ],
        },
        "social_specific_rules": [
            {"rule": "no_financial_advice", "severity": "critical"}
        ],
    }
    (tmp_path / "test:guardrails:compliance_rails.json").write_text(
        json.dumps(compliance_rails), encoding="utf-8"
    )

    # platform_playbooks.md
    platform_playbooks_md = """# Platform Playbooks

## TikTok

TikTok is where culture moves fastest.

### Voice Calibration

Formality: Very Low

### What NOT to Do on TikTok

Don't use hashtags in comments.

## Instagram

Instagram is more curated than TikTok.

### Voice Calibration

Formality: Low-Medium

## X (Twitter)

X is where brand personality shines.
"""
    (tmp_path / "test:content:platform_playbooks.md").write_text(
        platform_playbooks_md, encoding="utf-8"
    )

    # copywriting_reference.md
    (tmp_path / "test:content:copywriting_reference.md").write_text(
        "# Copywriting Reference\n\nDo / Don't pairs.", encoding="utf-8"
    )

    # content_engine.md
    (tmp_path / "test:content:content_engine.md").write_text(
        "# Content Engine\n\nPipeline architecture.", encoding="utf-8"
    )

    # README.md
    (tmp_path / "test:README.md").write_text(
        "# MoneyLion Brand Voice Engine", encoding="utf-8"
    )

    # cash_kitty_config.json
    cash_kitty = {"character": "Cash Kitty", "identity": {"name": "Cash Kitty"}}
    (tmp_path / "test:cash_kitty_config.json").write_text(
        json.dumps(cash_kitty), encoding="utf-8"
    )

    return tmp_path


@pytest.fixture
def mock_embeddings():
    svc = MagicMock()
    svc.batch_create_embeddings = AsyncMock(return_value=[])
    svc.create_embedding = AsyncMock(return_value=[0.1] * 10)
    svc.store_embedding = MagicMock()
    svc.search_similar = MagicMock(return_value=[])
    svc.delete_all_embeddings = MagicMock()
    return svc


class TestMarkdownChunking:
    def test_splits_by_headers(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        text = """## Section One

Content for section one.

## Section Two

Content for section two.
"""
        chunks = svc.chunk_markdown_document(text, "test.md")
        assert len(chunks) >= 2
        assert any("Section One" in c["text"] for c in chunks)
        assert any("Section Two" in c["text"] for c in chunks)

    def test_preserves_metadata(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        text = """## My Section

Some content here.
"""
        chunks = svc.chunk_markdown_document(text, "test_file.md")
        assert len(chunks) >= 1
        meta = chunks[0]["metadata"]
        assert meta["source_file"] == "test_file.md"
        assert meta["section_header"] == "My Section"

    def test_handles_subsections(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        text = """## Parent

Intro.

### Child One

Child content.

### Child Two

More child content.
"""
        chunks = svc.chunk_markdown_document(text, "test.md", chunk_size=50)
        # With small chunk_size, subsections should split out
        assert len(chunks) >= 2


class TestJsonChunking:
    def test_top_level_keys_as_chunks(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        data = {
            "personality": {"archetype": "Maverick"},
            "positioning": {"statement": "Trusted source"},
        }
        chunks = svc.chunk_json_document(data, "config.json")
        # At least 2 top-level chunks
        assert len(chunks) >= 2
        texts = [c["text"] for c in chunks]
        assert any("personality" in t for t in texts)
        assert any("positioning" in t for t in texts)

    def test_nested_keys_for_large_values(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        # Create a large nested dict
        large_value = {f"key_{i}": f"value_{i}" * 50 for i in range(10)}
        data = {"big_section": large_value}
        chunks = svc.chunk_json_document(data, "config.json")
        # Should have the top-level chunk + sub-chunks
        assert len(chunks) > 1

    def test_metadata_includes_key_path(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        data = {"personality": {"archetype": "Maverick"}}
        chunks = svc.chunk_json_document(data, "config.json")
        assert chunks[0]["metadata"]["key_path"] == "personality"


class TestGetBannedWords:
    def test_returns_absolute_bans(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        banned = svc.get_banned_words()
        absolute = banned["absolute"]
        assert "free" in absolute
        assert "guaranteed" in absolute
        assert "borrow" in absolute
        assert "loan" in absolute
        assert "debt" in absolute

    def test_returns_contextual_bans(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        banned = svc.get_banned_words()
        contextual = banned["contextual"]
        assert len(contextual) >= 1
        assert contextual[0]["word"] == "checking account"

    def test_deduplicates_absolute_bans(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        banned = svc.get_banned_words()
        absolute = banned["absolute"]
        # Should not have duplicates
        assert len(absolute) == len(set(absolute))


class TestGetPersonalityConfig:
    def test_returns_archetype(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        config = svc.get_personality_config()
        assert config["personality"]["archetype"] == "The Irreverent Maverick"

    def test_returns_voice_pillars(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        config = svc.get_personality_config()
        assert len(config["voice_pillars"]) >= 1
        assert config["voice_pillars"][0]["name"] == "Live Richly"

    def test_returns_platform_configs(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        config = svc.get_personality_config()
        assert "tiktok" in config["platform_configs"]
        assert config["platform_configs"]["tiktok"]["humor"] == 8


class TestGetPlatformPlaybook:
    def test_returns_tiktok_section(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        playbook = svc.get_platform_playbook("tiktok")
        assert "TikTok" in playbook
        assert "culture moves fastest" in playbook

    def test_returns_instagram_section(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        playbook = svc.get_platform_playbook("instagram")
        assert "Instagram" in playbook
        assert "curated" in playbook

    def test_returns_empty_for_unknown(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        playbook = svc.get_platform_playbook("unknown_platform")
        assert playbook == ""


class TestIngestDocument:
    @pytest.mark.asyncio
    async def test_ingest_json_document(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        # Find the voice config file
        json_file = None
        for f in brand_voice_dir.iterdir():
            if f.name.endswith("voice_config.json"):
                json_file = f
                break
        assert json_file is not None

        # Mock batch embeddings to return correct number
        mock_embeddings.batch_create_embeddings = AsyncMock(
            side_effect=lambda texts: [[0.1] * 10] * len(texts)
        )

        count = await svc.ingest_document(json_file)
        assert count > 0
        assert mock_embeddings.store_embedding.call_count == count

    @pytest.mark.asyncio
    async def test_ingest_markdown_document(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        md_file = None
        for f in brand_voice_dir.iterdir():
            if f.name.endswith("brand_voice.md"):
                md_file = f
                break
        assert md_file is not None

        mock_embeddings.batch_create_embeddings = AsyncMock(
            side_effect=lambda texts: [[0.1] * 10] * len(texts)
        )

        count = await svc.ingest_document(md_file)
        assert count > 0
        assert mock_embeddings.store_embedding.call_count == count

    @pytest.mark.asyncio
    async def test_ingest_all_documents(self, brand_voice_dir, mock_embeddings):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        mock_embeddings.batch_create_embeddings = AsyncMock(
            side_effect=lambda texts: [[0.1] * 10] * len(texts)
        )

        results = await svc.ingest_all_documents()
        # All 9 documents should be processed
        total = sum(results.values())
        assert total > 0
        # Each document should have at least 1 chunk
        found = sum(1 for v in results.values() if v > 0)
        assert found >= 7  # At least 7 of 9 files found

    @pytest.mark.asyncio
    async def test_refresh_embeddings_deletes_first(
        self, brand_voice_dir, mock_embeddings
    ):
        svc = BrandVoiceService(
            embeddings_service=mock_embeddings, brand_voice_dir=brand_voice_dir
        )
        mock_embeddings.batch_create_embeddings = AsyncMock(
            side_effect=lambda texts: [[0.1] * 10] * len(texts)
        )

        await svc.refresh_embeddings()
        mock_embeddings.delete_all_embeddings.assert_called_once()
