"""
Auth Router
FastAPI endpoints that use Commands and Queries (CQRS)
"""
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.common.dependencies.database import get_db
from app.common.dependencies.auth import get_current_user
from app.features.auth.models.user import User
from app.features.auth.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.features.auth.commands.register_user import RegisterUserCommand
from app.features.auth.commands.login_user import LoginUserCommand
from app.core.config import settings

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register User",
    tags=["Commands"],
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def register(
    request: Request,
    data: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Register a new user account."""
    command = RegisterUserCommand(db)
    user = await command.execute(data)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    tags=["Commands"],
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate and receive a JWT access token."""
    command = LoginUserCommand(db)
    return await command.execute(data)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    tags=["Queries"],
)
async def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)
