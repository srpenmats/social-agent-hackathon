"""TikTok integration via OpenClaw browser automation.

TikTok does not offer a public commenting API, so all interactions go through
an OpenClaw browser session.  This module implements the interface contract
that OpenClaw fulfills — methods proxy HTTP calls to OPENCLAW_BASE_URL.
"""

from datetime import datetime, timezone
from typing import Any

import httpx

from backend.config import get_settings
from backend.services.social.oauth import decrypt_credentials, encrypt_credentials


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TikTokError(Exception):
    """Base exception for TikTok/OpenClaw errors."""


class OpenClawSessionError(TikTokError):
    """Browser session is dead or stale."""


class OpenClawTimeoutError(TikTokError):
    """OpenClaw request timed out."""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class TikTokService:
    """TikTok integration backed by OpenClaw browser automation."""

    STALE_THRESHOLD_SECONDS = 3600  # 1 hour without activity → stale

    def __init__(self, platform_id: str, supabase_client: Any) -> None:
        self._platform_id = platform_id
        self._supabase = supabase_client
        settings = get_settings()
        base_url = settings.openclaw_base_url or "http://localhost:9090"
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(30.0),
        )
        self._session_id: str | None = None

    # -- internal helpers ---------------------------------------------------

    async def _load_session_id(self) -> str:
        """Load session_id from encrypted platform credentials."""
        if self._session_id:
            return self._session_id

        row = (
            self._supabase.table("platforms")
            .select("credentials_encrypted")
            .eq("id", self._platform_id)
            .single()
            .execute()
        )
        data = row.data
        if data and data.get("credentials_encrypted"):
            creds = decrypt_credentials(data["credentials_encrypted"])
            self._session_id = creds.get("session_id")

        if not self._session_id:
            raise OpenClawSessionError("No active TikTok session. Please connect first.")
        return self._session_id

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        """Centralized request to OpenClaw with error handling and audit logging."""
        session_id = await self._load_session_id()
        headers = {"X-Session-Id": session_id}

        try:
            response = await self._client.request(
                method, path, headers=headers, json=json_body, params=params
            )
            response.raise_for_status()
            result = response.json()
        except httpx.TimeoutException as exc:
            await self._log_audit("openclaw_timeout", {"path": path, "error": str(exc)})
            raise OpenClawTimeoutError(f"OpenClaw timed out on {path}") from exc
        except httpx.HTTPStatusError as exc:
            await self._log_audit(
                "openclaw_error",
                {"path": path, "status": exc.response.status_code, "body": exc.response.text[:500]},
            )
            if exc.response.status_code in (401, 403):
                raise OpenClawSessionError("OpenClaw session expired or unauthorized") from exc
            raise TikTokError(f"OpenClaw error {exc.response.status_code}: {exc.response.text[:200]}") from exc
        except httpx.HTTPError as exc:
            await self._log_audit("openclaw_connection_error", {"path": path, "error": str(exc)})
            raise TikTokError(f"OpenClaw connection error: {exc}") from exc

        await self._log_audit("openclaw_request", {"method": method, "path": path, "status": "ok"})
        return result

    async def _save_credentials(self, creds: dict) -> None:
        encrypted = encrypt_credentials(creds)
        self._supabase.table("platforms").update(
            {"credentials_encrypted": encrypted, "updated_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", self._platform_id).execute()

    async def _update_platform_status(self, status: str, **extra: Any) -> None:
        update = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat(), **extra}
        self._supabase.table("platforms").update(update).eq("id", self._platform_id).execute()

    async def _log_audit(self, action: str, details: dict) -> None:
        try:
            self._supabase.table("audit_log").insert({
                "action": action,
                "entity_type": "tiktok",
                "entity_id": str(self._platform_id),
                "details": details,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
        except Exception:
            pass  # Never let audit logging break the main flow

    # -- public API ---------------------------------------------------------

    async def start_browser_session(self) -> dict:
        """Start a new OpenClaw browser session for TikTok login."""
        try:
            response = await self._client.post(
                "/sessions/start", json={"platform": "tiktok"}
            )
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPError as exc:
            raise TikTokError(f"Failed to start browser session: {exc}") from exc

        session_id = result.get("session_id")
        if not session_id:
            raise TikTokError("OpenClaw did not return a session_id")

        self._session_id = session_id
        await self._save_credentials({"session_id": session_id})
        await self._update_platform_status(
            "connected",
            auth_method="browser_session",
            session_health="healthy",
            connected_at=datetime.now(timezone.utc).isoformat(),
        )
        await self._log_audit("tiktok_session_started", {"session_id": session_id})
        return {"session_id": session_id, "status": "connected"}

    async def check_session_health(self) -> dict:
        """Ping OpenClaw to verify the browser session is alive."""
        session_id = await self._load_session_id()
        try:
            response = await self._client.get(
                f"/sessions/{session_id}/health",
                headers={"X-Session-Id": session_id},
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError:
            return {"healthy": False, "last_activity": None, "status": "dead"}

        last_activity_raw = data.get("last_activity")
        if last_activity_raw:
            if isinstance(last_activity_raw, (int, float)):
                last_activity = datetime.fromtimestamp(last_activity_raw, tz=timezone.utc)
            else:
                last_activity = datetime.fromisoformat(str(last_activity_raw).replace("Z", "+00:00"))
            age_seconds = (datetime.now(timezone.utc) - last_activity).total_seconds()
        else:
            last_activity = None
            age_seconds = float("inf")

        if not data.get("alive", False):
            status = "dead"
            healthy = False
        elif age_seconds > self.STALE_THRESHOLD_SECONDS:
            status = "stale"
            healthy = False
        else:
            status = "healthy"
            healthy = True

        await self._update_platform_status(
            "connected" if healthy else "connected",
            session_health=status,
        )
        return {
            "healthy": healthy,
            "last_activity": last_activity.isoformat() if last_activity else None,
            "status": status,
        }

    async def get_session_status(self) -> str:
        """Return session status as a simple string: healthy / stale / dead."""
        health = await self.check_session_health()
        return health["status"]

    async def disconnect(self) -> bool:
        """Kill the browser session and mark the platform as disconnected."""
        try:
            session_id = await self._load_session_id()
            await self._client.post(
                f"/sessions/{session_id}/stop",
                headers={"X-Session-Id": session_id},
            )
        except (OpenClawSessionError, httpx.HTTPError):
            pass  # Session may already be dead

        self._session_id = None
        await self._update_platform_status(
            "disconnected",
            session_health=None,
            credentials_encrypted=None,
        )
        # Clear credentials directly
        self._supabase.table("platforms").update({
            "credentials_encrypted": None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", self._platform_id).execute()

        await self._log_audit("tiktok_disconnected", {})
        return True

    async def scan_feed(self, keywords: list[str]) -> list[dict]:
        """Scan TikTok FYP/search for videos matching keywords."""
        return (await self._request(
            "POST", "/scan", json_body={"keywords": keywords}
        )).get("videos", [])

    async def post_comment(self, video_url: str, text: str) -> dict:
        """Post a comment on a TikTok video via OpenClaw."""
        result = await self._request(
            "POST",
            "/comment",
            json_body={"video_url": video_url, "text": text},
        )
        return {
            "success": result.get("success", False),
            "comment_url": result.get("comment_url"),
            "error": result.get("error"),
        }

    async def get_video_info(self, video_url: str) -> dict:
        """Fetch metadata for a TikTok video."""
        return await self._request("GET", "/videos/info", params={"url": video_url})

    async def download_video(self, video_url: str) -> dict:
        """Download a TikTok video for transcription."""
        return await self._request(
            "POST", "/videos/download", json_body={"url": video_url}
        )

    async def get_engagement_metrics(self, comment_url: str) -> dict:
        """Fetch engagement metrics for a posted comment."""
        return await self._request(
            "GET", "/comments/metrics", params={"url": comment_url}
        )

    async def close(self) -> None:
        """Clean up the underlying HTTP client."""
        await self._client.aclose()
