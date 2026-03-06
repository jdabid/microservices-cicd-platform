"""
Unit tests for auth commands (register and login)
"""
import pytest

from app.common.exceptions import ConflictException, UnauthorizedException
from app.core.security import hash_password
from app.features.auth.commands.login_user import LoginUserCommand
from app.features.auth.commands.register_user import RegisterUserCommand
from app.features.auth.models.user import User
from app.features.auth.schemas.auth import LoginRequest, RegisterRequest


class TestRegisterUserCommand:
    """Tests for the RegisterUserCommand."""

    @pytest.mark.asyncio
    async def test_register_success(self, db_session) -> None:
        # Arrange
        command = RegisterUserCommand(db_session)
        data = RegisterRequest(
            email="new@example.com",
            password="StrongPass1",
            full_name="New User",
        )

        # Act
        user = await command.execute(data)

        # Assert
        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.full_name == "New User"
        assert user.is_active is True
        assert user.hashed_password != "StrongPass1"

    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises(self, db_session) -> None:
        # Arrange - create existing user
        existing = User(
            email="dup@example.com",
            hashed_password=hash_password("Password1"),
            full_name="Existing",
        )
        db_session.add(existing)
        db_session.commit()

        command = RegisterUserCommand(db_session)
        data = RegisterRequest(
            email="dup@example.com",
            password="StrongPass1",
            full_name="Duplicate",
        )

        # Act & Assert
        with pytest.raises(ConflictException):
            await command.execute(data)


class TestLoginUserCommand:
    """Tests for the LoginUserCommand."""

    @pytest.mark.asyncio
    async def test_login_success(self, db_session) -> None:
        # Arrange
        user = User(
            email="login@example.com",
            hashed_password=hash_password("ValidPass1"),
            full_name="Login User",
        )
        db_session.add(user)
        db_session.commit()

        command = LoginUserCommand(db_session)
        data = LoginRequest(email="login@example.com", password="ValidPass1")

        # Act
        result = await command.execute(data)

        # Assert
        assert result.access_token is not None
        assert len(result.access_token) > 0
        assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password_raises(self, db_session) -> None:
        # Arrange
        user = User(
            email="wrong@example.com",
            hashed_password=hash_password("ValidPass1"),
            full_name="Wrong Pass",
        )
        db_session.add(user)
        db_session.commit()

        command = LoginUserCommand(db_session)
        data = LoginRequest(email="wrong@example.com", password="BadPassword1")

        # Act & Assert
        with pytest.raises(UnauthorizedException):
            await command.execute(data)

    @pytest.mark.asyncio
    async def test_login_nonexistent_user_raises(self, db_session) -> None:
        # Arrange
        command = LoginUserCommand(db_session)
        data = LoginRequest(email="ghost@example.com", password="AnyPass123")

        # Act & Assert
        with pytest.raises(UnauthorizedException):
            await command.execute(data)

    @pytest.mark.asyncio
    async def test_login_inactive_user_raises(self, db_session) -> None:
        # Arrange
        user = User(
            email="inactive@example.com",
            hashed_password=hash_password("ValidPass1"),
            full_name="Inactive User",
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        command = LoginUserCommand(db_session)
        data = LoginRequest(email="inactive@example.com", password="ValidPass1")

        # Act & Assert
        with pytest.raises(UnauthorizedException):
            await command.execute(data)
