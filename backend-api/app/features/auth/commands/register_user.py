"""
Register User Command (CQRS)
Handles user registration - modifies system state
"""
from sqlalchemy.orm import Session

from app.common.exceptions import ConflictException, InternalServerException
from app.core.security import hash_password
from app.features.auth.models.user import User
from app.features.auth.schemas.auth import RegisterRequest


class RegisterUserCommand:
    """
    Command to register a new user.

    CQRS Pattern: This is a COMMAND - it modifies system state.

    Business Rules:
    - Email must be unique across all users.
    - Password is hashed before storage.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    async def execute(self, data: RegisterRequest) -> User:
        """
        Execute user registration.

        Args:
            data: Validated registration data.

        Returns:
            The newly created User.

        Raises:
            ConflictException: If a user with the same email already exists.
            InternalServerException: If a database error occurs.
        """
        existing = self.db.query(User).filter(User.email == data.email).first()
        if existing is not None:
            raise ConflictException(
                message="Email already registered",
                detail=f"A user with email '{data.email}' already exists",
            )

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as exc:
            self.db.rollback()
            raise InternalServerException(
                message="Failed to register user",
                detail=str(exc),
            )
