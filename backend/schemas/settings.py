from typing import Any

from pydantic import BaseModel, Field


# --- Voice ---

class VoiceConfigResponse(BaseModel):
    voice_guide_md: str | None = None
    positive_examples: list[dict[str, Any]] = []
    negative_examples: list[dict[str, Any]] = []
    platform_adapters: dict[str, Any] = {}


class VoiceConfigUpdateRequest(BaseModel):
    voice_guide_md: str | None = None
    positive_examples: list[dict[str, Any]] | None = None
    negative_examples: list[dict[str, Any]] | None = None
    platform_adapters: dict[str, Any] | None = None


class VoiceTestRequest(BaseModel):
    video_context: str


class VoiceTestCandidate(BaseModel):
    text: str
    approach: str
    char_count: int = 0


class VoiceTestResponse(BaseModel):
    candidates: list[VoiceTestCandidate] = []


# --- Risk ---

class RiskConfigResponse(BaseModel):
    auto_approve_max: int = 30
    review_max: int = 65
    blocklist: dict[str, Any] = {}
    override_rules: list[dict[str, Any]] = []


class RiskConfigUpdateRequest(BaseModel):
    auto_approve_max: int | None = Field(None, ge=0, le=100)
    review_max: int | None = Field(None, ge=0, le=100)
    blocklist: dict[str, Any] | None = None
    override_rules: list[dict[str, Any]] | None = None


# --- Discovery ---

class DiscoveryConfigResponse(BaseModel):
    keywords: dict[str, Any] = {}
    schedule: dict[str, Any] = {}
    thresholds: dict[str, Any] = {}


class DiscoveryConfigUpdateRequest(BaseModel):
    keywords: dict[str, Any] | None = None
    schedule: dict[str, Any] | None = None
    thresholds: dict[str, Any] | None = None


# --- Execution ---

class ExecutionConfigResponse(BaseModel):
    rate_limits: dict[str, Any] = {}
    behavior: dict[str, Any] = {}
    schedule: dict[str, Any] = {}
    supervised_mode: bool = False


class ExecutionConfigUpdateRequest(BaseModel):
    rate_limits: dict[str, Any] | None = None
    behavior: dict[str, Any] | None = None
    schedule: dict[str, Any] | None = None
    supervised_mode: bool | None = None


# --- Kill Switch ---

class KillSwitchRequest(BaseModel):
    active: bool
    reason: str | None = None
