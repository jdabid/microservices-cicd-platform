"""
FastAPI Main Application
Vertical Slice Architecture + CQRS Pattern
"""
import logging

import redis.asyncio as aioredis
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from starlette.exceptions import HTTPException

from app.core.config import settings
from app.common.database.session import AsyncSessionLocal
from app.core.logging import setup_logging
from app.core.middleware import CorrelationIdMiddleware
from app.common.exceptions import AppException
from app.common.exceptions.handlers import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from app.features.appointments.router import router as appointments_router
from app.features.auth.router import router as auth_router
from app.features.patients.router import router as patients_router

# Configure structured JSON logging
setup_logging()

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready microservices API with Vertical Slice Architecture and CQRS pattern",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Rate limiter state
app.state.limiter = limiter


def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"status_code": 429, "message": "Rate limit exceeded", "detail": str(exc.detail)},
    )


app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - environment-specific (no wildcards in production)
cors_origins = settings.BACKEND_CORS_ORIGINS
if settings.ENVIRONMENT == "production" and "*" in cors_origins:
    cors_origins = [o for o in cors_origins if o != "*"]

app.add_middleware(CorrelationIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app)

# Include feature routers (Vertical Slices)
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Auth"]
)
app.include_router(
    appointments_router,
    prefix=f"{settings.API_V1_PREFIX}/appointments",
    tags=["Appointments"]
)
app.include_router(
    patients_router,
    prefix=f"{settings.API_V1_PREFIX}/patients",
    tags=["Patients"]
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Microservices CI/CD Platform API",
        "version": "0.1.0",
        "architecture": "Vertical Slice Architecture",
        "pattern": "CQRS (Command Query Responsibility Segregation)",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "features": [
            "auth",
            "appointments",
            "patients"
        ]
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness probe

    Returns 200 if application is running
    """
    return {
        "status": "healthy",
        "service": "backend-api",
        "version": "0.1.0"
    }


@app.get("/ready")
async def readiness_check() -> JSONResponse:
    """
    Readiness check endpoint for Kubernetes readiness probe.

    Checks:
    - Database (PostgreSQL) connectivity via SELECT 1
    - Redis connectivity via PING

    Returns 200 when all dependencies are reachable, 503 otherwise.
    """
    logger = logging.getLogger(__name__)
    checks: dict[str, str] = {}

    # Check database connectivity
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        logger.error("Readiness probe: database check failed: %s", exc)
        checks["database"] = "failed"

    # Check Redis connectivity
    try:
        redis_client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_connect_timeout=2,
        )
        try:
            await redis_client.ping()
            checks["redis"] = "ok"
        finally:
            await redis_client.aclose()
    except Exception as exc:
        logger.error("Readiness probe: redis check failed: %s", exc)
        checks["redis"] = "failed"

    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503
    body = {
        "status": "ready" if all_ok else "not_ready",
        "checks": checks,
    }

    return JSONResponse(content=body, status_code=status_code)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )