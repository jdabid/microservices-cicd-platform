"""
Auth Dependencies for FastAPI
Provides the get_current_user dependency for protected endpoints.
"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.common.dependencies.database import get_db
from app.core.security import verify_token
from app.features.auth.models.user import User
from app.features.auth.queries.get_current_user import GetCurrentUserQuery

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that extracts and validates the JWT from the
    Authorization header, then returns the corresponding User.

    Args:
        token: Bearer token extracted by OAuth2PasswordBearer.
        db: Database session.

    Returns:
        The authenticated User instance.
    """
    payload = verify_token(token)
    email: str = payload["sub"]
    query = GetCurrentUserQuery(db)
    return await query.execute(email)
