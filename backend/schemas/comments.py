from datetime import datetime

from pydantic import BaseModel, Field


class CommentFilterQuery(BaseModel):
    platform: str | None = None
    status: str | None = None
    category: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    risk_min: int | None = Field(None, ge=0, le=100)
    risk_max: int | None = Field(None, ge=0, le=100)
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class RiskBreakdown(BaseModel):
    total_score: int = 0
    blocklist_score: int = 0
    context_score: int = 0
    ai_judge_score: int = 0
    reasoning: str | None = None


class CommentDetail(BaseModel):
    id: int
    platform: str
    video_url: str | None = None
    comment_text: str
    approach: str | None = None
    risk_score: int = 0
    risk_breakdown: RiskBreakdown | None = None
    status: str = "pending"
    likes: int = 0
    replies: int = 0
    posted_at: datetime | None = None
    approval_path: str | None = None
    screenshots: list[str] = []


class CommentListResponse(BaseModel):
    items: list[CommentDetail] = []
    total: int = 0
    page: int = 1
    limit: int = 20


class CommentSaveRequest(BaseModel):
    tags: list[str] = []
    notes: str | None = None
