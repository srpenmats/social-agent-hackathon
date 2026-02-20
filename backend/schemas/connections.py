from datetime import datetime
from typing import Any

from pydantic import BaseModel


class PlatformConnectionResponse(BaseModel):
    platform: str
    status: str = "disconnected"
    connected: bool = False
    auth_method: str | None = None
    account_info: dict[str, Any] | None = None
    session_health: str | None = None
    workers_status: dict[str, Any] | None = None
    connected_at: datetime | None = None


class ConnectRequest(BaseModel):
    platform: str
    auth_method: str
    credentials: dict[str, Any] = {}


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str | None = None


class ConnectionTestResponse(BaseModel):
    healthy: bool = False
    details: str | None = None
