"""X / Twitter API v2 integration.

Supports OAuth 2.0 with PKCE and API-key fallback authentication.
Implements sliding-window rate limiting per endpoint group.
"""

import time
from datetime import datetime, timezone
from typing import Any

import httpx

from config import get_settings
from services.social.oauth import (
    build_oauth_url,
    decrypt_credentials,
    encrypt_credentials,
    generate_pkce_pair,
    generate_state_token,
    validate_token_expiry,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TwitterAPIError(Exception):
    """Base Twitter API error."""

    def __init__(self, status_code: int, error_code: int | None, message: str) -> None:
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(f"Twitter API {status_code} (code={error_code}): {message}")


class RateLimitError(TwitterAPIError):
    """Rate limit exceeded (HTTP 429)."""

    def __init__(self, retry_after: int = 60) -> None:
        self.retry_after = retry_after
        super().__init__(429, 88, f"Rate limit exceeded. Retry after {retry_after}s.")


class TokenExpiredError(TwitterAPIError):
    """Token expired and refresh failed."""

    def __init__(self) -> None:
        super().__init__(401, 89, "Access token expired and refresh failed.")


# ---------------------------------------------------------------------------
# Sliding-window rate limiter
# ---------------------------------------------------------------------------

class _SlidingWindowLimiter:
    """Track rate limits per endpoint group using response headers."""

    def __init__(self) -> None:
        self._limits: dict[str, dict] = {
            "tweets_create": {"max": 200, "window": 900, "remaining": 200, "reset": 0},
            "tweets_search": {"max": 180, "window": 900, "remaining": 180, "reset": 0},
            "tweets_read": {"max": 300, "window": 900, "remaining": 300, "reset": 0},
        }

    def check(self, group: str) -> None:
        info = self._limits.get(group)
        if not info:
            return
        now = time.time()
        if now >= info["reset"]:
            # Window has elapsed — reset
            info["remaining"] = info["max"]
            info["reset"] = now + info["window"]
        if info["remaining"] <= 0:
            retry_after = max(int(info["reset"] - now), 1)
            raise RateLimitError(retry_after=retry_after)

    def update_from_headers(self, group: str, headers: httpx.Headers) -> None:
        info = self._limits.get(group)
        if not info:
            return
        remaining = headers.get("x-rate-limit-remaining")
        reset = headers.get("x-rate-limit-reset")
        if remaining is not None:
            info["remaining"] = int(remaining)
        if reset is not None:
            info["reset"] = int(reset)

    def track(self, group: str) -> None:
        info = self._limits.get(group)
        if info:
            info["remaining"] = max(info["remaining"] - 1, 0)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

TWITTER_API_BASE = "https://api.twitter.com"
TWITTER_AUTH_BASE = "https://twitter.com/i/oauth2/authorize"


class TwitterService:
    """X / Twitter API v2 integration."""

    def __init__(self, platform_id: str, supabase_client: Any) -> None:
        self._platform_id = platform_id
        self._supabase = supabase_client
        self._client = httpx.AsyncClient(
            base_url=TWITTER_API_BASE,
            timeout=httpx.Timeout(30.0),
        )
        self._rate_limiter = _SlidingWindowLimiter()

        # Credential cache (loaded lazily)
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._bearer_token: str | None = None
        self._auth_method: str | None = None  # "oauth" | "api_key"
        self._token_data: dict | None = None

    # -- internal helpers ---------------------------------------------------

    async def _load_credentials(self) -> None:
        if self._access_token or self._bearer_token:
            return
        row = (
            self._supabase.table("platforms")
            .select("credentials_encrypted, auth_method")
            .eq("id", self._platform_id)
            .single()
            .execute()
        )
        data = row.data
        if not data or not data.get("credentials_encrypted"):
            raise TwitterAPIError(401, None, "X/Twitter not connected.")
        creds = decrypt_credentials(data["credentials_encrypted"])
        self._auth_method = creds.get("auth_method", data.get("auth_method", "oauth"))
        self._access_token = creds.get("access_token")
        self._refresh_token = creds.get("refresh_token")
        self._bearer_token = creds.get("bearer_token")
        self._token_data = creds

    def _get_auth_headers(self) -> dict[str, str]:
        if self._auth_method == "api_key" and self._bearer_token:
            return {"Authorization": f"Bearer {self._bearer_token}"}
        if self._access_token:
            return {"Authorization": f"Bearer {self._access_token}"}
        raise TwitterAPIError(401, None, "No valid credentials loaded.")

    async def _refresh_access_token(self) -> bool:
        """Refresh OAuth 2.0 access token using stored refresh_token."""
        if not self._refresh_token:
            return False
        settings = get_settings()
        try:
            resp = await self._client.post(
                "/2/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                    "client_id": settings.twitter_client_id,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as exc:
            await self._log_audit("x_token_refresh_failed", {"error": str(exc)})
            return False

        new_creds = {
            "auth_method": "oauth",
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", self._refresh_token),
            "expires_at": datetime.now(timezone.utc).timestamp() + data.get("expires_in", 7200),
        }
        encrypted = encrypt_credentials(new_creds)
        self._supabase.table("platforms").update({
            "credentials_encrypted": encrypted,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", self._platform_id).execute()

        self._access_token = new_creds["access_token"]
        self._refresh_token = new_creds["refresh_token"]
        self._token_data = new_creds
        await self._log_audit("x_token_refreshed", {})
        return True

    async def _request(
        self,
        method: str,
        path: str,
        *,
        rate_group: str = "tweets_read",
        **kwargs: Any,
    ) -> dict:
        """Centralized Twitter API request with rate limiting and retry."""
        await self._load_credentials()

        # Check token expiry for OAuth
        if self._auth_method == "oauth" and self._token_data:
            expiry = validate_token_expiry(self._token_data)
            if expiry.get("needs_refresh") or not expiry.get("valid"):
                await self._refresh_access_token()

        self._rate_limiter.check(rate_group)
        kwargs.setdefault("headers", {}).update(self._get_auth_headers())

        try:
            response = await self._client.request(method, path, **kwargs)
            self._rate_limiter.update_from_headers(rate_group, response.headers)
            self._rate_limiter.track(rate_group)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            body: dict = {}
            try:
                body = exc.response.json()
            except Exception:
                pass

            if status == 429:
                retry_after = int(exc.response.headers.get("retry-after", "60"))
                raise RateLimitError(retry_after=retry_after)

            if status == 401:
                # Try refresh once
                if self._auth_method == "oauth" and await self._refresh_access_token():
                    kwargs["headers"].update(self._get_auth_headers())
                    response = await self._client.request(method, path, **kwargs)
                    self._rate_limiter.update_from_headers(rate_group, response.headers)
                    self._rate_limiter.track(rate_group)
                    response.raise_for_status()
                    return response.json()
                raise TokenExpiredError() from exc

            # Map X API v2 error codes
            errors = body.get("errors", [])
            error_code = errors[0].get("code") if errors else None
            error_msg = body.get("detail", body.get("title", exc.response.text[:200]))
            await self._log_audit("x_api_error", {"status": status, "error": error_msg})
            raise TwitterAPIError(status, error_code, error_msg) from exc

    async def _update_platform_status(self, status: str, **extra: Any) -> None:
        update = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat(), **extra}
        self._supabase.table("platforms").update(update).eq("id", self._platform_id).execute()

    async def _log_audit(self, action: str, details: dict) -> None:
        try:
            self._supabase.table("audit_log").insert({
                "action": action,
                "entity_type": "twitter",
                "entity_id": str(self._platform_id),
                "details": details,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
        except Exception:
            pass

    # -- OAuth 2.0 PKCE flow -----------------------------------------------

    async def get_auth_url(self) -> str:
        """Build X OAuth 2.0 authorization URL with PKCE."""
        settings = get_settings()
        code_verifier, code_challenge = generate_pkce_pair()
        state = generate_state_token()

        # Store PKCE verifier + state for the callback
        self._supabase.table("system_config").upsert({
            "key": f"x_oauth_state_{self._platform_id}",
            "value": {
                "state": state,
                "code_verifier": code_verifier,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        }).execute()

        redirect_uri = f"{settings.supabase_url}/auth/twitter/callback"
        return build_oauth_url(
            TWITTER_AUTH_BASE,
            {
                "response_type": "code",
                "client_id": settings.twitter_client_id,
                "redirect_uri": redirect_uri,
                "scope": "tweet.read tweet.write users.read offline.access",
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            },
        )

    async def handle_callback(self, code: str, state: str) -> dict:
        """Exchange authorization code for tokens (PKCE flow)."""
        # Retrieve stored PKCE state
        row = (
            self._supabase.table("system_config")
            .select("value")
            .eq("key", f"x_oauth_state_{self._platform_id}")
            .single()
            .execute()
        )
        stored = (row.data or {}).get("value", {})
        if not stored or stored.get("state") != state:
            raise TwitterAPIError(400, None, "CSRF state mismatch.")

        code_verifier = stored["code_verifier"]
        settings = get_settings()
        redirect_uri = f"{settings.supabase_url}/auth/twitter/callback"

        # Exchange code for tokens
        resp = await self._client.post(
            "/2/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
                "client_id": settings.twitter_client_id,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        token_data = resp.json()

        creds = {
            "auth_method": "oauth",
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": datetime.now(timezone.utc).timestamp() + token_data.get("expires_in", 7200),
        }

        # Validate by fetching user profile
        self._access_token = creds["access_token"]
        self._refresh_token = creds["refresh_token"]
        self._auth_method = "oauth"
        self._token_data = creds

        user = await self._request("GET", "/2/users/me", rate_group="tweets_read",
                                   params={"user.fields": "username,name,public_metrics"})
        user_data = user.get("data", {})

        encrypted = encrypt_credentials(creds)
        self._supabase.table("platforms").update({
            "credentials_encrypted": encrypted,
            "status": "connected",
            "auth_method": "oauth",
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", self._platform_id).execute()

        # Clean up state
        self._supabase.table("system_config").delete().eq(
            "key", f"x_oauth_state_{self._platform_id}"
        ).execute()

        await self._log_audit("x_connected", {"username": user_data.get("username"), "method": "oauth"})
        return {
            "success": True,
            "username": user_data.get("username"),
            "user_id": user_data.get("id"),
        }

    # -- API Key fallback ---------------------------------------------------

    async def connect_with_api_key(
        self, api_key: str, api_secret: str, bearer_token: str
    ) -> dict:
        """Connect using direct API key + bearer token (no OAuth)."""
        # Validate the bearer token
        self._bearer_token = bearer_token
        self._auth_method = "api_key"
        try:
            resp = await self._client.get(
                "/2/users/me",
                headers={"Authorization": f"Bearer {bearer_token}"},
                params={"user.fields": "username,name,public_metrics"},
            )
            resp.raise_for_status()
            user_data = resp.json().get("data", {})
        except httpx.HTTPError as exc:
            self._bearer_token = None
            self._auth_method = None
            raise TwitterAPIError(401, None, f"Bearer token validation failed: {exc}") from exc

        creds = {
            "auth_method": "api_key",
            "api_key": api_key,
            "api_secret": api_secret,
            "bearer_token": bearer_token,
        }
        encrypted = encrypt_credentials(creds)
        self._supabase.table("platforms").update({
            "credentials_encrypted": encrypted,
            "status": "connected",
            "auth_method": "api_key",
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", self._platform_id).execute()

        self._token_data = creds
        await self._log_audit("x_connected", {"username": user_data.get("username"), "method": "api_key"})
        return {
            "success": True,
            "username": user_data.get("username"),
            "user_id": user_data.get("id"),
        }

    # -- disconnect / test --------------------------------------------------

    async def disconnect(self) -> bool:
        """Revoke tokens and disconnect."""
        try:
            await self._load_credentials()
            if self._auth_method == "oauth" and self._access_token:
                settings = get_settings()
                await self._client.post(
                    "/2/oauth2/revoke",
                    data={"token": self._access_token, "client_id": settings.twitter_client_id},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
        except Exception:
            pass

        self._supabase.table("platforms").update({
            "status": "disconnected",
            "credentials_encrypted": None,
            "session_health": None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", self._platform_id).execute()

        self._access_token = None
        self._refresh_token = None
        self._bearer_token = None
        self._auth_method = None
        self._token_data = None

        await self._log_audit("x_disconnected", {})
        return True

    async def test_connection(self) -> dict:
        """Verify that stored credentials are still valid."""
        try:
            data = await self._request(
                "GET", "/2/users/me",
                rate_group="tweets_read",
                params={"user.fields": "username,name,public_metrics,verified"},
            )
            user = data.get("data", {})
            expiry = validate_token_expiry(self._token_data or {})
            return {
                "connected": True,
                "username": user.get("username"),
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
        """Fetch the authenticated user's profile."""
        data = await self._request(
            "GET", "/2/users/me",
            rate_group="tweets_read",
            params={"user.fields": "name,username,profile_image_url,public_metrics,verified"},
        )
        return data.get("data", {})

    async def post_reply(self, tweet_id: str, text: str) -> dict:
        """Post a reply to a tweet."""
        result = await self._request(
            "POST", "/2/tweets",
            rate_group="tweets_create",
            json={"text": text, "reply": {"in_reply_to_tweet_id": tweet_id}},
        )
        reply_data = result.get("data", {})
        await self._log_audit(
            "x_reply_posted",
            {"tweet_id": tweet_id, "reply_id": reply_data.get("id")},
        )
        return {"success": True, "tweet_id": reply_data.get("id")}

    async def search_tweets(self, query: str, max_results: int = 50) -> list[dict]:
        """Search recent tweets via API v2."""
        data = await self._request(
            "GET", "/2/tweets/search/recent",
            rate_group="tweets_search",
            params={
                "query": query,
                "max_results": min(max_results, 100),
                "tweet.fields": "created_at,public_metrics,author_id,conversation_id",
                "expansions": "author_id",
                "user.fields": "username,public_metrics",
            },
        )
        return data.get("data", [])

    async def get_tweet_metrics(self, tweet_id: str) -> dict:
        """Fetch detailed metrics for a single tweet."""
        data = await self._request(
            "GET", f"/2/tweets/{tweet_id}",
            rate_group="tweets_read",
            params={"tweet.fields": "public_metrics,non_public_metrics,organic_metrics,created_at"},
        )
        return data.get("data", {}).get("public_metrics", {})

    async def get_user_tweets(self, user_id: str) -> list[dict]:
        """Get recent tweets from a user (competitor monitoring)."""
        data = await self._request(
            "GET", f"/2/users/{user_id}/tweets",
            rate_group="tweets_read",
            params={
                "max_results": 50,
                "tweet.fields": "created_at,public_metrics,conversation_id",
            },
        )
        return data.get("data", [])

    async def get_thread_context(self, tweet_id: str) -> list[dict]:
        """Fetch the full conversation thread for a tweet."""
        data = await self._request(
            "GET", "/2/tweets/search/recent",
            rate_group="tweets_search",
            params={
                "query": f"conversation_id:{tweet_id}",
                "max_results": 100,
                "tweet.fields": "created_at,public_metrics,author_id,in_reply_to_user_id",
                "expansions": "author_id",
                "user.fields": "username",
            },
        )
        return data.get("data", [])

    async def close(self) -> None:
        """Clean up the underlying HTTP client."""
        await self._client.aclose()
