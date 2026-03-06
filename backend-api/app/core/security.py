"""
JWT Authentication & Password Hashing Utilities
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.common.exceptions import UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token.
        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT string.
    """
    to_encode: dict[str, Any] = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Args:
        token: The JWT string to verify.

    Returns:
        Decoded token payload.

    Raises:
        UnauthorizedException: If the token is invalid or expired.
    """
    try:
        payload: dict = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("sub") is None:
            raise UnauthorizedException(
                message="Invalid token", detail="Token payload missing 'sub' claim"
            )
        return payload
    except JWTError as exc:
        raise UnauthorizedException(
            message="Invalid token", detail=str(exc)
        )


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return pwd_context.verify(plain, hashed)
