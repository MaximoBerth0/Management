import secrets
import uuid
from datetime import datetime, timedelta, timezone

from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings
from app.shared.exceptions.auth_errors import TokenExpired, TokenInvalid

"""
- create access JWT tokens.
- verify access token and refresh token types.
- decode JWT tokens.
"""

def create_token(
    *,
    subject: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(user_id: int) -> str:
    return create_token(
        subject=str(user_id),
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except ExpiredSignatureError:
        raise TokenExpired("expired token")
    except JWTError:
        raise TokenInvalid("invalid token")


def verify_access_token(token: str) -> dict:
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise TokenInvalid("incorrect token")

    return payload


def verify_refresh_token(token: str) -> dict:
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise TokenInvalid("incorrect token")

    return payload

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

