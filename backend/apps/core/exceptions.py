"""
Unified API error format — SPECIFICATION §4.2.2 / §4.2.6.

Every error response body is::

    {"error": {"code": "...", "message": "...", "field": "...",
               "details": {...}, "trace_id": "..."}}
"""

from __future__ import annotations

import uuid

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404, JsonResponse
from rest_framework import exceptions, status
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler as drf_exception_handler


class ServiceError(exceptions.APIException):
    """Business rule violation raised from the service layer."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "SERVICE_ERROR"
    default_detail = "The request violates a business rule."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        field: str | None = None,
        details=None,
        status_code: int | None = None,
    ):
        super().__init__(detail=message or self.default_detail)
        self.error_code = code or self.default_code
        self.field = field
        self.details = details if details is not None else {}
        if status_code is not None:
            self.status_code = status_code


class ConflictError(ServiceError):
    """409 — optimistic lock mismatch or dependent rows prevent the change."""

    status_code = status.HTTP_409_CONFLICT
    default_code = "CONFLICT"
    default_detail = "The resource was modified or is referenced elsewhere."


def new_trace_id(request=None) -> str:
    if request is not None:
        incoming = request.META.get("HTTP_X_REQUEST_ID")
        if incoming:
            return incoming[:64]
    return uuid.uuid4().hex


def error_body(
    code: str,
    message: str,
    *,
    field: str | None = None,
    details=None,
    trace_id: str | None = None,
) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "field": field,
            "details": details if details is not None else {},
            "trace_id": trace_id or new_trace_id(),
        }
    }


def error_response(
    code: str, message: str, http_status: int, *, request=None, **kwargs
) -> JsonResponse:
    """Plain Django JsonResponse in the §4.2.2 format (used by middleware)."""
    trace_id = new_trace_id(request)
    response = JsonResponse(
        error_body(code, message, trace_id=trace_id, **kwargs), status=http_status
    )
    response["X-Trace-ID"] = trace_id
    return response


def _first_message(data):
    if isinstance(data, dict):
        for value in data.values():
            message = _first_message(value)
            if message:
                return message
        return None
    if isinstance(data, (list, tuple)):
        for value in data:
            message = _first_message(value)
            if message:
                return message
        return None
    return str(data) if data is not None else None


def _first_field(data):
    if isinstance(data, dict):
        for key in data:
            if key not in ("non_field_errors", "__all__", "detail"):
                return key
    return None


_AUTH_CODES = {
    "no_active_account": "AUTH_INVALID_CREDENTIALS",
    "token_not_valid": "AUTH_TOKEN_INVALID",
    "user_not_found": "AUTH_TOKEN_INVALID",
    "user_inactive": "AUTH_USER_INACTIVE",
}


def _classify(exc, data):
    """Return (code, message, field, details) for a handled exception."""
    if isinstance(exc, ServiceError):
        return exc.error_code, str(exc.detail), exc.field, exc.details
    if isinstance(exc, exceptions.ValidationError):
        return (
            "VALIDATION_ERROR",
            _first_message(data) or "Invalid input.",
            _first_field(data),
            data,
        )
    if isinstance(exc, exceptions.NotAuthenticated):
        return "AUTH_NOT_AUTHENTICATED", _first_message(data), None, {}
    if isinstance(exc, exceptions.AuthenticationFailed):
        raw_code = None
        if isinstance(data, dict):
            raw_code = data.get("code")
        if raw_code is None:
            codes = exc.get_codes()
            raw_code = codes if isinstance(codes, str) else None
        code = _AUTH_CODES.get(str(raw_code), "AUTH_TOKEN_INVALID")
        message = data.get("detail") if isinstance(data, dict) else None
        return code, str(message or _first_message(data)), None, {}
    if isinstance(exc, exceptions.PermissionDenied):
        return "AUTH_PERMISSION_DENIED", _first_message(data), None, {}
    if isinstance(exc, exceptions.NotFound):
        return "NOT_FOUND", _first_message(data), None, {}
    if isinstance(exc, exceptions.MethodNotAllowed):
        return "METHOD_NOT_ALLOWED", _first_message(data), None, {}
    if isinstance(exc, exceptions.ParseError):
        return "PARSE_ERROR", _first_message(data), None, {}
    if isinstance(exc, exceptions.Throttled):
        return "THROTTLED", _first_message(data), None, {}
    code = getattr(exc, "default_code", "ERROR")
    return str(code).upper(), _first_message(data) or "Error.", None, {}


def api_exception_handler(exc, context):
    """DRF EXCEPTION_HANDLER producing the §4.2.2 error envelope."""
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))
    elif isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    request = context.get("request")
    trace_id = new_trace_id(request)
    code, message, field, details = _classify(exc, response.data)
    response.data = error_body(
        code, message or "Error.", field=field, details=details, trace_id=trace_id
    )
    response["X-Trace-ID"] = trace_id
    return response
