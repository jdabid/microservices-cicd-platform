"""
Unit tests for the centralized exception system.
Tests each custom exception type and every exception handler.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.common.exceptions import (
    AppException,
    NotFoundException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
    InternalServerException,
)
from app.common.exceptions.schemas import ErrorResponse
from app.common.exceptions.handlers import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _fake_request() -> Request:
    """Create a minimal fake ASGI request for handler tests."""
    scope = {"type": "http", "method": "GET", "path": "/test"}
    return Request(scope)


# ---------------------------------------------------------------------------
# Exception class tests
# ---------------------------------------------------------------------------

class TestAppException:
    """Tests for the base AppException."""

    def test_default_values(self) -> None:
        exc = AppException()
        assert exc.status_code == 500
        assert exc.message == "Internal Server Error"
        assert exc.detail is None

    def test_custom_values(self) -> None:
        exc = AppException(status_code=418, message="Teapot", detail="I'm a teapot")
        assert exc.status_code == 418
        assert exc.message == "Teapot"
        assert exc.detail == "I'm a teapot"

    def test_is_exception(self) -> None:
        exc = AppException()
        assert isinstance(exc, Exception)


class TestNotFoundException:
    def test_default_values(self) -> None:
        exc = NotFoundException()
        assert exc.status_code == 404
        assert exc.message == "Not Found"
        assert exc.detail is None

    def test_custom_detail(self) -> None:
        exc = NotFoundException(detail="Patient not found")
        assert exc.status_code == 404
        assert exc.detail == "Patient not found"

    def test_inherits_app_exception(self) -> None:
        assert isinstance(NotFoundException(), AppException)


class TestBadRequestException:
    def test_default_values(self) -> None:
        exc = BadRequestException()
        assert exc.status_code == 400
        assert exc.message == "Bad Request"

    def test_custom_values(self) -> None:
        exc = BadRequestException(message="Invalid input", detail="Field X is required")
        assert exc.status_code == 400
        assert exc.message == "Invalid input"
        assert exc.detail == "Field X is required"

    def test_inherits_app_exception(self) -> None:
        assert isinstance(BadRequestException(), AppException)


class TestUnauthorizedException:
    def test_default_values(self) -> None:
        exc = UnauthorizedException()
        assert exc.status_code == 401
        assert exc.message == "Unauthorized"

    def test_custom_detail(self) -> None:
        exc = UnauthorizedException(detail="Token expired")
        assert exc.detail == "Token expired"

    def test_inherits_app_exception(self) -> None:
        assert isinstance(UnauthorizedException(), AppException)


class TestForbiddenException:
    def test_default_values(self) -> None:
        exc = ForbiddenException()
        assert exc.status_code == 403
        assert exc.message == "Forbidden"

    def test_custom_detail(self) -> None:
        exc = ForbiddenException(detail="Insufficient permissions")
        assert exc.detail == "Insufficient permissions"

    def test_inherits_app_exception(self) -> None:
        assert isinstance(ForbiddenException(), AppException)


class TestConflictException:
    def test_default_values(self) -> None:
        exc = ConflictException()
        assert exc.status_code == 409
        assert exc.message == "Conflict"

    def test_custom_detail(self) -> None:
        exc = ConflictException(detail="Resource already exists")
        assert exc.detail == "Resource already exists"

    def test_inherits_app_exception(self) -> None:
        assert isinstance(ConflictException(), AppException)


class TestInternalServerException:
    def test_default_values(self) -> None:
        exc = InternalServerException()
        assert exc.status_code == 500
        assert exc.message == "Internal Server Error"

    def test_custom_detail(self) -> None:
        exc = InternalServerException(detail="Database unavailable")
        assert exc.detail == "Database unavailable"

    def test_inherits_app_exception(self) -> None:
        assert isinstance(InternalServerException(), AppException)


# ---------------------------------------------------------------------------
# ErrorResponse schema tests
# ---------------------------------------------------------------------------

class TestErrorResponseSchema:
    def test_full_response(self) -> None:
        resp = ErrorResponse(status_code=404, message="Not Found", detail="Item 1 missing")
        assert resp.status_code == 404
        assert resp.message == "Not Found"
        assert resp.detail == "Item 1 missing"

    def test_detail_optional(self) -> None:
        resp = ErrorResponse(status_code=500, message="Internal Server Error")
        assert resp.detail is None

    def test_model_dump(self) -> None:
        resp = ErrorResponse(status_code=400, message="Bad Request", detail="oops")
        data = resp.model_dump()
        assert data == {"status_code": 400, "message": "Bad Request", "detail": "oops"}


# ---------------------------------------------------------------------------
# Handler tests
# ---------------------------------------------------------------------------

class TestAppExceptionHandler:
    @pytest.mark.asyncio
    async def test_handles_app_exception(self) -> None:
        exc = AppException(status_code=500, message="Server Error", detail="boom")
        response = await app_exception_handler(_fake_request(), exc)
        assert response.status_code == 500
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 500
        assert body["message"] == "Server Error"
        assert body["detail"] == "boom"

    @pytest.mark.asyncio
    async def test_handles_not_found(self) -> None:
        exc = NotFoundException(detail="Patient 42 not found")
        response = await app_exception_handler(_fake_request(), exc)
        assert response.status_code == 404
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 404
        assert body["message"] == "Not Found"
        assert body["detail"] == "Patient 42 not found"

    @pytest.mark.asyncio
    async def test_handles_bad_request(self) -> None:
        exc = BadRequestException(detail="Invalid email")
        response = await app_exception_handler(_fake_request(), exc)
        assert response.status_code == 400
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 400
        assert body["message"] == "Bad Request"
        assert body["detail"] == "Invalid email"

    @pytest.mark.asyncio
    async def test_handles_unauthorized(self) -> None:
        exc = UnauthorizedException(detail="Missing token")
        response = await app_exception_handler(_fake_request(), exc)
        assert response.status_code == 401
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 401
        assert body["message"] == "Unauthorized"

    @pytest.mark.asyncio
    async def test_handles_forbidden(self) -> None:
        exc = ForbiddenException(detail="Admin only")
        response = await app_exception_handler(_fake_request(), exc)
        assert response.status_code == 403
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 403
        assert body["message"] == "Forbidden"

    @pytest.mark.asyncio
    async def test_handles_conflict(self) -> None:
        exc = ConflictException(detail="Duplicate entry")
        response = await app_exception_handler(_fake_request(), exc)
        assert response.status_code == 409
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 409
        assert body["message"] == "Conflict"

    @pytest.mark.asyncio
    async def test_handles_internal_server(self) -> None:
        exc = InternalServerException(detail="DB down")
        response = await app_exception_handler(_fake_request(), exc)
        assert response.status_code == 500
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 500
        assert body["detail"] == "DB down"

    @pytest.mark.asyncio
    async def test_detail_none_when_not_provided(self) -> None:
        exc = NotFoundException()
        response = await app_exception_handler(_fake_request(), exc)
        import json
        body = json.loads(response.body)
        assert body["detail"] is None


class TestValidationExceptionHandler:
    @pytest.mark.asyncio
    async def test_handles_validation_error(self) -> None:
        errors = [
            {
                "type": "missing",
                "loc": ("body", "patient_name"),
                "msg": "Field required",
                "input": {},
                "url": "https://errors.pydantic.dev/2/v/missing",
            }
        ]
        exc = RequestValidationError(errors=errors)
        response = await validation_exception_handler(_fake_request(), exc)
        assert response.status_code == 422
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 422
        assert body["message"] == "Validation Error"
        assert "patient_name" in body["detail"]
        assert "Field required" in body["detail"]

    @pytest.mark.asyncio
    async def test_handles_multiple_validation_errors(self) -> None:
        errors = [
            {
                "type": "missing",
                "loc": ("body", "name"),
                "msg": "Field required",
                "input": {},
                "url": "https://errors.pydantic.dev/2/v/missing",
            },
            {
                "type": "value_error",
                "loc": ("body", "email"),
                "msg": "Invalid email format",
                "input": "bad",
                "url": "https://errors.pydantic.dev/2/v/value_error",
            },
        ]
        exc = RequestValidationError(errors=errors)
        response = await validation_exception_handler(_fake_request(), exc)
        import json
        body = json.loads(response.body)
        assert "name" in body["detail"]
        assert "email" in body["detail"]


class TestHTTPExceptionHandler:
    @pytest.mark.asyncio
    async def test_handles_http_exception(self) -> None:
        exc = HTTPException(status_code=404, detail="Not found")
        response = await http_exception_handler(_fake_request(), exc)
        assert response.status_code == 404
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 404
        assert body["message"] == "Not found"
        assert body["detail"] is None

    @pytest.mark.asyncio
    async def test_handles_http_exception_no_detail(self) -> None:
        exc = HTTPException(status_code=500)
        response = await http_exception_handler(_fake_request(), exc)
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 500
        assert body["message"] == "Internal Server Error"


class TestGeneralExceptionHandler:
    @pytest.mark.asyncio
    async def test_handles_generic_exception(self) -> None:
        exc = RuntimeError("something went wrong")
        response = await general_exception_handler(_fake_request(), exc)
        assert response.status_code == 500
        import json
        body = json.loads(response.body)
        assert body["status_code"] == 500
        assert body["message"] == "Internal Server Error"
        assert body["detail"] == "An unexpected error occurred."

    @pytest.mark.asyncio
    async def test_does_not_leak_exception_details(self) -> None:
        exc = ValueError("secret database password exposed")
        response = await general_exception_handler(_fake_request(), exc)
        import json
        body = json.loads(response.body)
        assert "secret" not in body["message"]
        assert "secret" not in (body["detail"] or "")
