"""
Exception Handlers
Centralized handlers registered with FastAPI to return consistent JSON error responses.
"""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.common.exceptions import AppException
from app.common.exceptions.schemas import ErrorResponse


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle AppException and all its subclasses."""
    error = ErrorResponse(
        status_code=exc.status_code,
        message=exc.message,
        detail=exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic / FastAPI request validation errors."""
    errors = exc.errors()
    detail = "; ".join(
        f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in errors
    )
    error = ErrorResponse(
        status_code=422,
        message="Validation Error",
        detail=detail,
    )
    return JSONResponse(
        status_code=422,
        content=error.model_dump(),
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Handle Starlette/FastAPI HTTPException."""
    error = ErrorResponse(
        status_code=exc.status_code,
        message=str(exc.detail) if exc.detail else "HTTP Error",
        detail=None,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(),
    )


async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle any unhandled exceptions as 500 Internal Server Error."""
    error = ErrorResponse(
        status_code=500,
        message="Internal Server Error",
        detail="An unexpected error occurred.",
    )
    return JSONResponse(
        status_code=500,
        content=error.model_dump(),
    )
