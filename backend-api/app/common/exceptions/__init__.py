"""
Centralized Exception System
Custom exception classes for consistent error handling across the application.
"""


class AppException(Exception):
    """Base application exception with structured error response support."""

    def __init__(
        self,
        status_code: int = 500,
        message: str = "Internal Server Error",
        detail: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.detail = detail
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found - HTTP 404."""

    def __init__(
        self,
        message: str = "Not Found",
        detail: str | None = None,
    ) -> None:
        super().__init__(status_code=404, message=message, detail=detail)


class BadRequestException(AppException):
    """Bad request - HTTP 400."""

    def __init__(
        self,
        message: str = "Bad Request",
        detail: str | None = None,
    ) -> None:
        super().__init__(status_code=400, message=message, detail=detail)


class UnauthorizedException(AppException):
    """Unauthorized access - HTTP 401."""

    def __init__(
        self,
        message: str = "Unauthorized",
        detail: str | None = None,
    ) -> None:
        super().__init__(status_code=401, message=message, detail=detail)


class ForbiddenException(AppException):
    """Forbidden access - HTTP 403."""

    def __init__(
        self,
        message: str = "Forbidden",
        detail: str | None = None,
    ) -> None:
        super().__init__(status_code=403, message=message, detail=detail)


class ConflictException(AppException):
    """Resource conflict - HTTP 409."""

    def __init__(
        self,
        message: str = "Conflict",
        detail: str | None = None,
    ) -> None:
        super().__init__(status_code=409, message=message, detail=detail)


class InternalServerException(AppException):
    """Internal server error - HTTP 500."""

    def __init__(
        self,
        message: str = "Internal Server Error",
        detail: str | None = None,
    ) -> None:
        super().__init__(status_code=500, message=message, detail=detail)
