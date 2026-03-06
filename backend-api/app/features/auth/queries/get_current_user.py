"""
Get Current User Query (CQRS)
Retrieves the authenticated user from a verified JWT
"""
from sqlalchemy.orm import Session

from app.common.exceptions import UnauthorizedException
from app.features.auth.models.user import User


class GetCurrentUserQuery:
    """
    Query to fetch the currently authenticated user.

    CQRS Pattern: This is a QUERY - it does not modify system state.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    async def execute(self, email: str) -> User:
        """
        Retrieve the user identified by the JWT subject claim.

        Args:
            email: The email extracted from the token's 'sub' claim.

        Returns:
            The authenticated User.

        Raises:
            UnauthorizedException: If the user does not exist or is inactive.
        """
        user = self.db.query(User).filter(User.email == email).first()

        if user is None:
            raise UnauthorizedException(
                message="User not found",
                detail="The user associated with this token no longer exists",
            )

        if not user.is_active:
            raise UnauthorizedException(
                message="Account disabled",
                detail="This user account has been deactivated",
            )

        return user
