from datetime import datetime
from typing import Any

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Ingest schemas (NeoClaw -> Dashboard)
# ---------------------------------------------------------------------------

class VideoIngestRequest(BaseModel):
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


class VideoIngestResponse(BaseModel):
    video_id: int
    classification: str | None = None
    comment_candidates: list[dict[str, Any]] = []


class BulkIngestRequest(BaseModel):
    videos: list[VideoIngestRequest]


class BulkIngestResponse(BaseModel):
    results: list[VideoIngestResponse] = []
    errors: list[str] = []


class MetricsIngestRequest(BaseModel):
    engagement_id: int
    likes: int = 0
    replies: int = 0
    reply_texts: list[str] = []
    impressions: int | None = None
    checked_at: datetime | None = None


class CommentResultRequest(BaseModel):
    task_id: int
    platform: str
    video_url: str
    comment_text: str
    success: bool
    screenshot_url: str | None = None
    error_message: str | None = None


class PlatformHealthRequest(BaseModel):
    platform: str
    session_health: str  # healthy, stale, dead
    workers_status: dict[str, Any] = {}
    last_activity: datetime | None = None


class TrendingIngestRequest(BaseModel):
    platform: str
    topics: list[str] = []
    hashtags: list[str] = []
    scraped_at: datetime | None = None


# ---------------------------------------------------------------------------
# Task schemas (Dashboard -> NeoClaw)
# ---------------------------------------------------------------------------

class TaskResponse(BaseModel):
    task_id: int
    type: str
    platform: str | None = None
    payload: dict[str, Any]
    priority: int
    expires_at: str | None = None


class TaskCompleteRequest(BaseModel):
    result: dict[str, Any] = {}


class TaskFailRequest(BaseModel):
    error: str
    should_retry: bool = True


# ---------------------------------------------------------------------------
# Status schemas
# ---------------------------------------------------------------------------

class HeartbeatRequest(BaseModel):
    agent_id: str
    active_sessions: list[dict[str, Any]] = []
    current_task_id: int | None = None
    system_stats: dict[str, Any] | None = None


class AgentConfigResponse(BaseModel):
    kill_switch_active: bool = False
    rate_limits: dict[str, Any] = {}
    posting_windows: dict[str, Any] = {}
    keywords: list[str] = []
    voice_config_summary: str | None = None
