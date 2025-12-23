import uuid
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.shared.exceptions import InvalidToken, TokenExpired
from jose import ExpiredSignatureError, JWTError, jwt

"""
- create access and refresh JWT tokens.
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


def create_refresh_token(user_id: int) -> str:
    return create_token(
        subject=str(user_id),
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


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
        raise InvalidToken("invalid token")


def verify_access_token(token: str) -> dict:
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise InvalidToken("incorrect token")

    return payload


def verify_refresh_token(token: str) -> dict:
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise InvalidToken("incorrect token")

    return payload
