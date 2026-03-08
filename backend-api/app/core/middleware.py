"""Middleware for correlation ID tracking."""
import contextvars
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable for correlation ID
_correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default="-"
)

logger = logging.getLogger(__name__)


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return _correlation_id.get()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware that adds correlation ID to each request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Use X-Correlation-ID header if provided, otherwise generate one
        correlation_id = request.headers.get(
            "X-Correlation-ID", str(uuid.uuid4())
        )
        _correlation_id.set(correlation_id)

        start_time = time.time()

        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "correlation_id": correlation_id,
            },
        )

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "correlation_id": correlation_id,
            },
        )

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        return response
