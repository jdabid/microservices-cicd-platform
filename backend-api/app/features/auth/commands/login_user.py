"""
Login User Command (CQRS)
Handles user authentication and JWT creation
"""
from sqlalchemy.orm import Session

from app.common.exceptions import UnauthorizedException
from app.core.security import create_access_token, verify_password
from app.features.auth.models.user import User
from app.features.auth.schemas.auth import LoginRequest, TokenResponse


class LoginUserCommand:
    """
    Command to authenticate a user and issue a JWT.

    CQRS Pattern: This is a COMMAND - it produces a side-effect (token issuance).

    Business Rules:
    - Email must belong to an existing, active user.
    - Password must match the stored hash.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    async def execute(self, data: LoginRequest) -> TokenResponse:
        """
        Authenticate the user and return a JWT.

        Args:
            data: Login credentials.

        Returns:
            TokenResponse with access_token.

        Raises:
            UnauthorizedException: If credentials are invalid or account is inactive.
        """
        user = self.db.query(User).filter(User.email == data.email).first()

        if user is None or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException(
                message="Invalid credentials",
                detail="Incorrect email or password",
            )

        if not user.is_active:
            raise UnauthorizedException(
                message="Account disabled",
                detail="This user account has been deactivated",
            )

        token = create_access_token(data={"sub": user.email})
        return TokenResponse(access_token=token)
