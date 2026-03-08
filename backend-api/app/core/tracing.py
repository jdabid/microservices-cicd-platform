"""
OpenTelemetry Distributed Tracing Configuration

Configures TracerProvider with OTLP exporter for Jaeger integration.
Instruments FastAPI, SQLAlchemy, and Redis for end-to-end tracing.
"""
import logging
from typing import Optional

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings

logger = logging.getLogger(__name__)

# Module-level flag to prevent double instrumentation
_tracing_initialized: bool = False


def _build_resource() -> Resource:
    """Build OpenTelemetry resource with service metadata."""
    return Resource.create(
        {
            "service.name": settings.OTEL_SERVICE_NAME,
            "service.version": "0.1.0",
            "deployment.environment": settings.ENVIRONMENT,
        }
    )


def _create_tracer_provider() -> TracerProvider:
    """Create and configure the TracerProvider with OTLP exporter."""
    resource = _build_resource()
    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True,
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    return provider


def setup_tracing(app: FastAPI) -> None:
    """
    Initialize OpenTelemetry tracing and instrument the FastAPI application.

    This function sets up the global TracerProvider with an OTLP exporter
    pointing to Jaeger, then instruments the FastAPI app for automatic
    span creation on each request.

    Args:
        app: The FastAPI application instance to instrument.
    """
    global _tracing_initialized

    if _tracing_initialized:
        logger.warning("Tracing already initialized, skipping duplicate setup")
        return

    if not settings.OTEL_TRACING_ENABLED:
        logger.info("OpenTelemetry tracing is disabled (OTEL_TRACING_ENABLED=false)")
        return

    provider = _create_tracer_provider()
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)

    _tracing_initialized = True
    logger.info(
        "OpenTelemetry tracing initialized: exporter=%s, service=%s",
        settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        settings.OTEL_SERVICE_NAME,
    )


def instrument_sqlalchemy(engine: AsyncEngine) -> None:
    """
    Instrument a SQLAlchemy async engine for distributed tracing.

    Args:
        engine: The SQLAlchemy AsyncEngine to instrument.
    """
    if not settings.OTEL_TRACING_ENABLED:
        return

    SQLAlchemyInstrumentor().instrument(
        engine=engine.sync_engine,
    )
    logger.info("SQLAlchemy engine instrumented for tracing")


def instrument_redis() -> None:
    """Instrument Redis client for distributed tracing."""
    if not settings.OTEL_TRACING_ENABLED:
        return

    RedisInstrumentor().instrument()
    logger.info("Redis client instrumented for tracing")


def shutdown_tracing() -> None:
    """Gracefully shut down the tracer provider, flushing pending spans."""
    provider: Optional[TracerProvider] = trace.get_tracer_provider()  # type: ignore[assignment]
    if provider and hasattr(provider, "shutdown"):
        provider.shutdown()
        logger.info("OpenTelemetry tracer provider shut down")
