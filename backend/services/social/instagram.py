"""Instagram Graph API integration.

Handles OAuth 2.0 via Facebook Login, comment posting, media insights,
and Explore discovery.  Rate-limited at 200 calls/user/hour.
"""

from datetime import datetime, timezone
from typing import Any

import httpx

from backend.config import get_settings
from backend.services.social.oauth import (
    build_oauth_url,
    decrypt_credentials,
    encrypt_credentials,
    generate_state_token,
    validate_token_expiry,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class InstagramAPIError(Exception):
    """Base Instagram API error."""

    def __init__(self, status_code: int, error_type: str, message: str) -> None:
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(f"Instagram API {status_code} ({error_type}): {message}")


class RateLimitError(InstagramAPIError):
    """Rate limit exceeded (HTTP 429)."""

    def __init__(self, retry_after: int = 60) -> None:
        self.retry_after = retry_after
        super().__init__(429, "rate_limit", f"Rate limit exceeded. Retry after {retry_after}s.")


class TokenExpiredError(InstagramAPIError):
    """Token has expired and could not be refreshed."""

    def __init__(self) -> None:
        super().__init__(401, "token_expired", "Access token expired and refresh failed.")


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

class _RateLimiter:
    """Simple fixed-window rate limiter: max_calls per window_seconds."""

    def __init__(self, max_calls: int = 200, window_seconds: int = 3600) -> None:
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = 0
        self.window_start = datetime.now(timezone.utc)

    def check(self) -> None:
        now = datetime.now(timezone.utc)
        elapsed = (now - self.window_start).total_seconds()
        if elapsed >= self.window_seconds:
            self.calls = 0
            self.window_start = now
        if self.calls >= self.max_calls:
            remaining = self.window_seconds - elapsed
            raise RateLimitError(retry_after=int(max(remaining, 1)))

    def track(self) -> None:
        self.calls += 1


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

GRAPH_API_BASE = "https://graph.facebook.com/v18.0"


class InstagramService:
    """Instagram Graph API integration."""

    def __init__(self, platform_id: str, supabase_client: Any) -> None:
        self._platform_id = platform_id
        self._supabase = supabase_client
        self._client = httpx.AsyncClient(base_url=GRAPH_API_BASE, timeout=httpx.Timeout(30.0))
        self._rate_limiter = _RateLimiter(max_calls=200, window_seconds=3600)

        # Loaded lazily from DB
        self._access_token: str | None = None
        self._page_token: str | None = None
        self._ig_user_id: str | None = None
        self._token_data: dict | None = None

    # -- internal helpers ---------------------------------------------------

    async def _load_credentials(self) -> None:
        if self._access_token:
            return
        row = (
            self._supabase.table("platforms")
            .select("credentials_encrypted")
            .eq("id", self._platform_id)
            .single()
            .execute()
        )
        data = row.data
        if not data or not data.get("credentials_encrypted"):
            raise InstagramAPIError(401, "not_connected", "Instagram not connected.")
        creds = decrypt_credentials(data["credentials_encrypted"])
        self._access_token = creds.get("access_token")
        self._page_token = creds.get("page_token")
        self._ig_user_id = creds.get("ig_user_id")
        self._token_data = creds

    async def _maybe_refresh_token(self) -> None:
        """Refresh token if it's nearing expiry."""
        await self._load_credentials()
        if not self._token_data:
            return
        expiry_info = validate_token_expiry(self._token_data)
        if not expiry_info["needs_refresh"]:
            return

        settings = get_settings()
        try:
            resp = await self._client.get(
                "/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": settings.instagram_app_id,
                    "client_secret": settings.instagram_app_secret,
                    "fb_exchange_token": self._access_token,
                },
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            await self._log_audit("ig_token_refresh_failed", {"error": str(exc)})
            raise TokenExpiredError() from exc

        new_token = data.get("access_token", self._access_token)
        expires_in = data.get("expires_in", 5184000)  # default 60 days
        new_creds = {
            **(self._token_data or {}),
            "access_token": new_token,
            "expires_at": (datetime.now(timezone.utc).timestamp() + expires_in),
        }
        encrypted = encrypt_credentials(new_creds)
        self._supabase.table("platforms").update({
            "credentials_encrypted": encrypted,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", self._platform_id).execute()

        self._access_token = new_token
        self._token_data = new_creds
        await self._log_audit("ig_token_refreshed", {"expires_in": expires_in})

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict:
        """Centralized Graph API request with rate limiting, auth, and retry."""
        await self._load_credentials()
        await self._maybe_refresh_token()
        self._rate_limiter.check()

        # Inject access token
        params = kwargs.pop("params", {})
        params.setdefault("access_token", self._page_token or self._access_token)
        kwargs["params"] = params

        try:
            response = await self._client.request(method, path, **kwargs)
            self._rate_limiter.track()
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            body = {}
            try:
                body = exc.response.json()
            except Exception:
                pass

            error_info = body.get("error", {})

            if status == 429:
                raise RateLimitError()
            if status == 401 or error_info.get("type") == "OAuthException":
                # Try refresh once, then retry
                try:
                    self._access_token = None  # force reload
                    self._token_data = None
                    await self._load_credentials()
                    await self._maybe_refresh_token()
                    params["access_token"] = self._page_token or self._access_token
                    kwargs["params"] = params
                    response = await self._client.request(method, path, **kwargs)
                    self._rate_limiter.track()
                    response.raise_for_status()
                    return response.json()
                except Exception:
                    raise TokenExpiredError() from exc

            await self._log_audit("ig_api_error", {"status": status, "error": error_info})
            raise InstagramAPIError(
                status,
                error_info.get("type", "unknown"),
                error_info.get("message", exc.response.text[:200]),
            ) from exc

    async def _update_platform_status(self, status: str, **extra: Any) -> None:
        update = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat(), **extra}
        self._supabase.table("platforms").update(update).eq("id", self._platform_id).execute()

    async def _log_audit(self, action: str, details: dict) -> None:
        try:
            self._supabase.table("audit_log").insert({
                "action": action,
                "entity_type": "instagram",
                "entity_id": str(self._platform_id),
                "details": details,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
        except Exception:
            pass

    # -- OAuth flow ---------------------------------------------------------

    async def get_auth_url(self) -> str:
        """Build Facebook/Instagram OAuth redirect URL."""
        settings = get_settings()
        state = generate_state_token()

        # Store state for CSRF validation on callback
        self._supabase.table("system_config").upsert({
            "key": f"ig_oauth_state_{self._platform_id}",
            "value": {"state": state, "created_at": datetime.now(timezone.utc).isoformat()},
        }).execute()

        redirect_uri = f"{settings.supabase_url}/auth/instagram/callback"
        return build_oauth_url(
            "https://www.facebook.com/v18.0/dialog/oauth",
            {
                "client_id": settings.instagram_app_id,
                "redirect_uri": redirect_uri,
                "state": state,
                "scope": "instagram_basic,instagram_content_publish,instagram_manage_comments,pages_read_engagement",
                "response_type": "code",
            },
        )

    async def handle_callback(self, code: str, state: str) -> dict:
        """Exchange OAuth code for tokens, validate, and store credentials."""
        # Validate CSRF state
        row = (
            self._supabase.table("system_config")
            .select("value")
            .eq("key", f"ig_oauth_state_{self._platform_id}")
            .single()
            .execute()
        )
        stored_state = (row.data or {}).get("value", {}).get("state")
        if not stored_state or stored_state != state:
            raise InstagramAPIError(400, "invalid_state", "CSRF state mismatch.")

        settings = get_settings()
        redirect_uri = f"{settings.supabase_url}/auth/instagram/callback"

        # Exchange code for access token
        resp = await self._client.get(
            "/oauth/access_token",
            params={
                "client_id": settings.instagram_app_id,
                "client_secret": settings.instagram_app_secret,
                "redirect_uri": redirect_uri,
                "code": code,
            },
        )
        resp.raise_for_status()
        token_data = resp.json()

        access_token = token_data["access_token"]

        # Get page token and IG user ID
        accounts_resp = await self._client.get(
            "/me/accounts", params={"access_token": access_token}
        )
        accounts_resp.raise_for_status()
        accounts = accounts_resp.json().get("data", [])

        page_token = None
        page_id = None
        ig_user_id = None
        username = None

        if accounts:
            page = accounts[0]
            page_token = page.get("access_token")
            page_id = page.get("id")

            # Get Instagram business account linked to the page
            ig_resp = await self._client.get(
                f"/{page_id}",
                params={
                    "fields": "instagram_business_account{id,username,followers_count}",
                    "access_token": page_token or access_token,
                },
            )
            ig_resp.raise_for_status()
            ig_data = ig_resp.json().get("instagram_business_account", {})
            ig_user_id = ig_data.get("id")
            username = ig_data.get("username")

        # Store encrypted credentials
        creds = {
            "access_token": access_token,
            "page_token": page_token,
            "page_id": page_id,
            "ig_user_id": ig_user_id,
            "expires_at": datetime.now(timezone.utc).timestamp() + token_data.get("expires_in", 5184000),
        }
        encrypted = encrypt_credentials(creds)

        self._supabase.table("platforms").update({
            "credentials_encrypted": encrypted,
            "status": "connected",
            "auth_method": "oauth",
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", self._platform_id).execute()

        # Cache locally
        self._access_token = access_token
        self._page_token = page_token
        self._ig_user_id = ig_user_id
        self._token_data = creds

        # Clean up state
        self._supabase.table("system_config").delete().eq(
            "key", f"ig_oauth_state_{self._platform_id}"
        ).execute()

        await self._log_audit("ig_connected", {"username": username, "page_id": page_id})
        return {"success": True, "username": username, "page_id": page_id}

    async def disconnect(self) -> bool:
        """Revoke Instagram tokens and mark as disconnected."""
        try:
            await self._load_credentials()
            if self._access_token:
                await self._client.delete(
                    "/me/permissions",
                    params={"access_token": self._access_token},
                )
        except Exception:
            pass  # Best-effort revocation

        self._supabase.table("platforms").update({
            "status": "disconnected",
            "credentials_encrypted": None,
            "session_health": None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", self._platform_id).execute()

        self._access_token = None
        self._page_token = None
        self._ig_user_id = None
        self._token_data = None

        await self._log_audit("ig_disconnected", {})
        return True

    async def test_connection(self) -> dict:
        """Verify that stored tokens are still valid."""
        try:
            await self._load_credentials()
            resp = await self._client.get(
                "/me/accounts",
                params={"access_token": self._access_token},
            )
            resp.raise_for_status()
            accounts = resp.json().get("data", [])
            expiry = validate_token_expiry(self._token_data or {})
            return {
                "connected": True,
                "username": accounts[0].get("name") if accounts else None,
                "token_valid": expiry["valid"],
                "expires_at": expiry["expires_at"],
            }
        except Exception as exc:
            return {
                "connected": False,
                "username": None,
                "token_valid": False,
                "expires_at": None,
                "error": str(exc),
            }

    # -- core methods -------------------------------------------------------

    async def get_user_profile(self) -> dict:
        """Fetch the connected Instagram business account profile."""
        await self._load_credentials()
        if not self._ig_user_id:
            raise InstagramAPIError(400, "no_ig_account", "No Instagram business account linked.")
        return await self._request(
            "GET",
            f"/{self._ig_user_id}",
            params={"fields": "id,username,followers_count,media_count,profile_picture_url"},
        )

    async def post_comment(self, media_id: str, text: str) -> dict:
        """Post a comment on an Instagram media item."""
        result = await self._request(
            "POST",
            f"/{media_id}/comments",
            data={"message": text},
        )
        await self._log_audit("ig_comment_posted", {"media_id": media_id, "comment_id": result.get("id")})
        return {"success": True, "comment_id": result.get("id")}

    async def get_comments(self, media_id: str) -> list[dict]:
        """Fetch comments on a media item."""
        result = await self._request(
            "GET",
            f"/{media_id}/comments",
            params={"fields": "id,text,timestamp,username,like_count"},
        )
        return result.get("data", [])

    async def get_media_insights(self, media_id: str) -> dict:
        """Fetch engagement metrics for a media item."""
        result = await self._request(
            "GET",
            f"/{media_id}/insights",
            params={"metric": "engagement,impressions,reach"},
        )
        metrics = {}
        for item in result.get("data", []):
            metrics[item["name"]] = item.get("values", [{}])[0].get("value", 0)
        return metrics

    async def search_explore(self, keywords: list[str]) -> list[dict]:
        """Search for content via hashtag-based discovery.

        Falls back to empty list if the endpoint is restricted.
        """
        await self._load_credentials()
        if not self._ig_user_id:
            return []

        results: list[dict] = []
        for keyword in keywords[:5]:  # Limit to 5 hashtags per call
            tag = keyword.strip().lstrip("#").lower()
            try:
                # Search for hashtag ID
                tag_search = await self._request(
                    "GET",
                    "/ig_hashtag_search",
                    params={"q": tag, "user_id": self._ig_user_id},
                )
                hashtag_id = (tag_search.get("data") or [{}])[0].get("id")
                if not hashtag_id:
                    continue
                # Get recent media for hashtag
                media = await self._request(
                    "GET",
                    f"/{hashtag_id}/recent_media",
                    params={
                        "user_id": self._ig_user_id,
                        "fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink",
                    },
                )
                results.extend(media.get("data", []))
            except InstagramAPIError:
                continue  # Endpoint may be restricted
        return results

    async def get_recent_media(self, user_id: str) -> list[dict]:
        """Get recent posts from a user (competitor monitoring)."""
        return (await self._request(
            "GET",
            f"/{user_id}/media",
            params={"fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink"},
        )).get("data", [])

    async def close(self) -> None:
        """Clean up the underlying HTTP client."""
        await self._client.aclose()
