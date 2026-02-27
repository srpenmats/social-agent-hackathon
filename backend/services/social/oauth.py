"""Shared OAuth utilities for social platform integrations.

Provides PKCE generation, CSRF state tokens, Fernet credential encryption,
token expiry validation, and OAuth URL construction.
"""

import base64
import hashlib
import json
import secrets
from datetime import datetime, timezone
from urllib.parse import urlencode

from cryptography.fernet import Fernet, InvalidToken

from config import get_settings


def _get_fernet() -> Fernet:
    key = get_settings().encryption_key
    if not key:
        raise RuntimeError(
            "ENCRYPTION_KEY not set. Generate one with: "
            "python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge (S256).

    Returns (code_verifier, code_challenge) tuple.
    """
    code_verifier = secrets.token_urlsafe(32)  # 43-char URL-safe string
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


def generate_state_token() -> str:
    """Generate a CSRF-safe state parameter for OAuth flows."""
    return secrets.token_urlsafe(32)


def encrypt_credentials(data: dict) -> str:
    """Fernet-encrypt a credentials dict. Returns base64-encoded ciphertext."""
    f = _get_fernet()
    plaintext = json.dumps(data).encode("utf-8")
    return f.encrypt(plaintext).decode("utf-8")


def decrypt_credentials(encrypted: str) -> dict:
    """Decrypt a Fernet-encrypted credentials string back to a dict.

    Raises ValueError on invalid or expired tokens.
    """
    f = _get_fernet()
    try:
        plaintext = f.decrypt(encrypted.encode("utf-8"))
        return json.loads(plaintext.decode("utf-8"))
    except (InvalidToken, json.JSONDecodeError) as exc:
        raise ValueError(f"Failed to decrypt credentials: {exc}") from exc


def validate_token_expiry(
    token_data: dict, threshold_days: int = 7
) -> dict:
    """Check whether a token is still valid or needs refreshing.

    Expects token_data to contain an 'expires_at' key (ISO-8601 string or
    unix timestamp).  Returns a status dict.
    """
    expires_raw = token_data.get("expires_at")
    if expires_raw is None:
        return {
            "valid": True,
            "expires_at": None,
            "needs_refresh": False,
            "days_remaining": None,
        }

    if isinstance(expires_raw, (int, float)):
        expires_at = datetime.fromtimestamp(expires_raw, tz=timezone.utc)
    elif isinstance(expires_raw, str):
        expires_at = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
    else:
        expires_at = expires_raw

    now = datetime.now(timezone.utc)
    remaining = expires_at - now
    days_remaining = remaining.total_seconds() / 86400

    return {
        "valid": days_remaining > 0,
        "expires_at": expires_at.isoformat(),
        "needs_refresh": 0 < days_remaining <= threshold_days,
        "days_remaining": round(days_remaining, 1),
    }


def build_oauth_url(base_url: str, params: dict) -> str:
    """Construct an OAuth redirect URL with query parameters."""
    return f"{base_url}?{urlencode(params)}"
