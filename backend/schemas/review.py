from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ReviewDecision(str, Enum):
    approve = "approve"
    reject = "reject"


class VideoContext(BaseModel):
    video_url: str | None = None
    creator: str | None = None
    description: str | None = None
    classification: str | None = None


class ReviewItem(BaseModel):
    id: int
    comment_id: int | None = None
    video_id: int | None = None
    proposed_text: str
    risk_score: int = 0
    risk_reasoning: str | None = None
    classification: str | None = None
    queued_at: datetime | None = None
    video_context: VideoContext | None = None


class ReviewQueueResponse(BaseModel):
    items: list[ReviewItem] = []
    pending_count: int = 0
    avg_wait_min: float = 0.0
    sla_breaches: int = 0


class ReviewDecisionRequest(BaseModel):
    decision: ReviewDecision
    reason: str | None = None
    edited_text: str | None = None


class ReviewHistoryItem(BaseModel):
    id: int
    proposed_text: str
    decision: str | None = None
    decision_reason: str | None = None
    reviewed_by: str | None = None
    queued_at: datetime | None = None
    decided_at: datetime | None = None


class ReviewHistoryStats(BaseModel):
    approved: int = 0
    rejected: int = 0
    avg_time_seconds: float = 0.0


class ReviewHistoryResponse(BaseModel):
    items: list[ReviewHistoryItem] = []
    stats: ReviewHistoryStats = ReviewHistoryStats()
