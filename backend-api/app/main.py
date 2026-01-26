"""
FastAPI Main Application
Vertical Slice Architecture + CQRS Pattern
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings

# from app.features.appointments.router import router as appointments_router

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Microservices platform with Vertical Slice Architecture and CQRS",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app)


# Include routers (Vertical Slices)
# app.include_router(
#     appointments_router,
#     prefix=f"{settings.API_V1_PREFIX}/appointments",
#     tags=["Appointments"]
# )


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
        "metrics": "/metrics"
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
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probe

    Should check:
    - Database connectivity
    - Redis connectivity
    - Any critical dependencies

    Returns 200 when ready to serve traffic
    """
    # TODO: Add database connectivity check
    # TODO: Add Redis connectivity check

    return {
        "status": "ready",
        "service": "backend-api",
        "checks": {
            "database": "ok",  # TODO: Implement actual check
            "redis": "ok"  # TODO: Implement actual check
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )