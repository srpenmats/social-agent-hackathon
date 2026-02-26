from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Timeframe(str, Enum):
    day = "24h"
    week = "7d"
    month = "30d"


class TimeframeQuery(BaseModel):
    timeframe: Timeframe = Timeframe.day


class PlatformSummary(BaseModel):
    platform: str
    comments_posted: int = 0
    avg_likes: float = 0.0
    sentiment_score: float = 0.0
    trending_status: str = "green"  # green | yellow | red


class OverviewResponse(BaseModel):
    total_engagements: int = 0
    avg_engagement_rate: float = 0.0
    approval_rate: float = 0.0
    active_platforms: int = 0
    platform_summaries: list[PlatformSummary] = []


class PlatformStatsResponse(BaseModel):
    kpis: dict = {}
    category_breakdown: list[dict] = []
    timeline_data: list[dict] = []
    top_comments: list[dict] = []


class EngagementTimelinePoint(BaseModel):
    timestamp: datetime
    comments_posted: int = 0
    engagement_rate: float = 0.0
    platform: str | None = None


class EngagementTimelineResponse(BaseModel):
    data_points: list[EngagementTimelinePoint] = []


class HashtagPerformance(BaseModel):
    tag: str
    comment_count: int = 0
    avg_likes: float = 0.0
    engagement_rate: float = 0.0


class HashtagPerformanceResponse(BaseModel):
    hashtags: list[HashtagPerformance] = []
