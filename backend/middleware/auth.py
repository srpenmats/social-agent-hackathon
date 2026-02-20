from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt

from backend.config import get_settings

ALGORITHM = "HS256"


def _extract_token(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    return auth.removeprefix("Bearer ")


def verify_jwt(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
    return payload


async def get_current_user(request: Request) -> dict:
    token = _extract_token(request)
    payload = verify_jwt(token)
    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("user_role", "viewer"),
    }


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_role(*roles: str):
    async def _check(user: CurrentUser) -> dict:
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user['role']}' not authorized. Required: {', '.join(roles)}",
            )
        return user
    return Depends(_check)
