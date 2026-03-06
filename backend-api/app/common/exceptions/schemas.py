"""
Error Response Schema
Pydantic v2 model for structured JSON error responses.
"""
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Structured error response returned by all exception handlers."""

    status_code: int
    message: str
    detail: str | None = None
