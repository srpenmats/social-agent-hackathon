from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Platform(BaseModel):
    id: int
    name: str
    auth_method: str | None = None
    status: str = "disconnected"
    credentials_encrypted: str | None = None
    session_health: str | None = None
    workers_status: dict[str, Any] | None = None
    connected_at: datetime | None = None
    updated_at: datetime | None = None


class DiscoveredVideo(BaseModel):
    id: int
    platform: str
    video_url: str
    creator: str | None = None
    description: str | None = None
    transcript: str | None = None
    hashtags: list[str] = []
    likes: int = 0
    comments_count: int = 0
    shares: int = 0
    classification: str | None = None
    discovered_at: datetime | None = None
    status: str = "new"
    engaged: bool = False


class GeneratedComment(BaseModel):
    id: int
    video_id: int
    text: str
    approach: str  # witty | helpful | supportive
    char_count: int = 0
    generated_at: datetime | None = None
    selected: bool = False


class RiskScore(BaseModel):
    id: int
    comment_id: int
    total_score: int = 0
    blocklist_score: int = 0
    context_score: int = 0
    ai_judge_score: int = 0
    reasoning: str | None = None
    routing_decision: str = "review"  # auto_approve | review | discard
    scored_at: datetime | None = None


class Engagement(BaseModel):
    id: int
    platform: str
    video_id: int | None = None
    comment_id: int | None = None
    comment_text: str
    risk_score: int = 0
    approval_path: str = "human"  # auto | human
    approved_by: str | None = None
    posted_at: datetime | None = None
    screenshot_url: str | None = None
    status: str = "pending"


class EngagementMetric(BaseModel):
    id: int
    engagement_id: int
    checked_at: datetime | None = None
    likes: int = 0
    replies: int = 0
    reply_texts: list[str] = []
    reply_sentiment: float | None = None
    impressions: int | None = None


class SavedComment(BaseModel):
    id: int
    engagement_id: int
    saved_by: str | None = None
    tags: list[str] = []
    notes: str | None = None
    saved_at: datetime | None = None


class ReviewQueueItem(BaseModel):
    id: int
    comment_id: int | None = None
    video_id: int | None = None
    proposed_text: str
    risk_score: int = 0
    risk_reasoning: str | None = None
    classification: str | None = None
    queued_at: datetime | None = None
    reviewed_by: str | None = None
    decision: str | None = None  # approve | reject
    decision_reason: str | None = None
    decided_at: datetime | None = None


class VoiceConfig(BaseModel):
    id: int
    voice_guide_md: str | None = None
    positive_examples: list[dict[str, Any]] = []
    negative_examples: list[dict[str, Any]] = []
    platform_adapters: dict[str, Any] = {}
    updated_at: datetime | None = None
    updated_by: str | None = None


class RiskConfig(BaseModel):
    id: int
    auto_approve_max: int = 30
    review_max: int = 65
    blocklist: dict[str, Any] = {}
    override_rules: list[dict[str, Any]] = []
    updated_at: datetime | None = None


class SystemConfig(BaseModel):
    id: int
    key: str
    value: dict[str, Any] = {}
    updated_at: datetime | None = None


class AuditLog(BaseModel):
    id: int
    user_id: str | None = None
    action: str
    entity_type: str | None = None
    entity_id: str | None = None
    details: dict[str, Any] = {}
    created_at: datetime | None = None


class BrandVoiceEmbedding(BaseModel):
    id: int
    document_name: str | None = None
    chunk_text: str | None = None
    chunk_index: int = 0
    metadata: dict[str, Any] = {}
    created_at: datetime | None = None


class CommentEmbedding(BaseModel):
    id: int
    comment_id: int
    created_at: datetime | None = None
