"""
Unit tests for core security utilities (JWT + password hashing)
"""
import pytest
from datetime import timedelta
from unittest.mock import patch

from app.core.security import (
    create_access_token,
    verify_token,
    hash_password,
    verify_password,
)
from app.common.exceptions import UnauthorizedException


class TestPasswordHashing:
    """Tests for password hash and verify functions."""

    def test_hash_password_returns_bcrypt_hash(self) -> None:
        # Arrange
        plain = "SecurePass1"

        # Act
        hashed = hash_password(plain)

        # Assert
        assert hashed != plain
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self) -> None:
        # Arrange
        plain = "SecurePass1"
        hashed = hash_password(plain)

        # Act & Assert
        assert verify_password(plain, hashed) is True

    def test_verify_password_incorrect(self) -> None:
        # Arrange
        hashed = hash_password("SecurePass1")

        # Act & Assert
        assert verify_password("WrongPassword1", hashed) is False

    def test_hash_password_unique_salts(self) -> None:
        # Arrange
        plain = "SecurePass1"

        # Act
        hash1 = hash_password(plain)
        hash2 = hash_password(plain)

        # Assert - different salts produce different hashes
        assert hash1 != hash2
        assert verify_password(plain, hash1) is True
        assert verify_password(plain, hash2) is True


class TestJWT:
    """Tests for JWT create and verify functions."""

    def test_create_and_verify_token(self) -> None:
        # Arrange
        data = {"sub": "user@example.com"}

        # Act
        token = create_access_token(data)
        payload = verify_token(token)

        # Assert
        assert payload["sub"] == "user@example.com"
        assert "exp" in payload

    def test_create_token_with_custom_expiry(self) -> None:
        # Arrange
        data = {"sub": "user@example.com"}
        delta = timedelta(minutes=5)

        # Act
        token = create_access_token(data, expires_delta=delta)
        payload = verify_token(token)

        # Assert
        assert payload["sub"] == "user@example.com"

    def test_verify_token_invalid_raises(self) -> None:
        # Act & Assert
        with pytest.raises(UnauthorizedException):
            verify_token("not.a.valid.token")

    def test_verify_token_missing_sub_raises(self) -> None:
        # Arrange - token without 'sub' claim
        token = create_access_token({"sub": "user@example.com"})

        # Patch decode to return payload without sub
        with patch("app.core.security.jwt.decode", return_value={"exp": 9999999999}):
            with pytest.raises(UnauthorizedException):
                verify_token(token)

    def test_create_token_preserves_extra_data(self) -> None:
        # Arrange
        data = {"sub": "user@example.com", "role": "admin"}

        # Act
        token = create_access_token(data)
        payload = verify_token(token)

        # Assert
        assert payload["role"] == "admin"
