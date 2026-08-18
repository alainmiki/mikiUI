"""Error handling system for MikiUI.

Provides structured exceptions and helpers for consistent error responses.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

logger = logging.getLogger(__name__)


class MikiUIError(Exception):
    """Base exception for all MikiUI errors."""

    status_code: int = 500
    error_type: str = "server_error"
    message: str = "An unexpected error occurred."

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": self.error_type,
            "message": self.message,
        }


class ValidationError(MikiUIError):
    """Raised when form or input validation fails."""

    status_code = 422
    error_type = "validation_error"
    message = "Validation failed"

    def __init__(self, errors: dict[str, str] | None = None) -> None:
        self.errors = errors or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["fields"] = self.errors
        return data


class NotFoundError(MikiUIError):
    """Raised when a requested resource does not exist."""

    status_code = 404
    error_type = "not_found"
    message = "Resource not found"

    def __init__(self, resource: str = "resource") -> None:
        self.resource = resource
        super().__init__(f"{resource} not found")

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["resource"] = self.resource
        return data


class PermissionError(MikiUIError):
    """Raised when the caller lacks required permissions."""

    status_code = 403
    error_type = "permission_denied"
    message = "Permission denied"


class RateLimitError(MikiUIError):
    """Raised when a caller exceeds rate limits."""

    status_code = 429
    error_type = "rate_limit_exceeded"
    message = "Rate limit exceeded"

    def __init__(self, retry_after: int = 60) -> None:
        self.retry_after = retry_after
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["retry_after"] = self.retry_after
        return data


class ServerError(MikiUIError):
    """Raised for unhandled internal errors."""

    status_code = 500
    error_type = "server_error"
    message = "Internal server error"


async def error_response(error: MikiUIError, request: Request, app: Any | None = None) -> JSONResponse | HTMLResponse:
    """Convert a :class:`MikiUIError` into the appropriate response.

    Returns JSON for API routes and HTML for page routes.
    """
    payload = error.to_dict()
    is_api = request.headers.get("accept", "").startswith("application/json") or request.url.path.startswith("/api/")
    if is_api:
        return JSONResponse(payload, status_code=error.status_code)
    if app is not None:
        handler = getattr(app, "_error_pages", {}).get(error.status_code)
        if handler is not None:
            try:
                from ..app.routes import Ctx
                ctx = Ctx(request, app)
                result = handler(ctx)
                if hasattr(result, "__await__"):
                    result = await result
                from ..engine.dom import normalize
                from ..engine.renderer import render_page
                nodes = normalize(result)
                return HTMLResponse(
                    render_page(nodes, title=f"{error.status_code}", lang="en"),
                    status_code=error.status_code,
                )
            except Exception:
                logger.exception("Custom error page handler failed for %d", error.status_code)
    body = _render_error_html(error)
    return HTMLResponse(body, status_code=error.status_code)


def log_error(error: Exception, request: Request) -> None:
    """Log an error with request context."""
    logger.error(
        "Error on %s %s: %s",
        request.method,
        request.url.path,
        str(error),
        exc_info=True,
    )


def _render_error_html(error: MikiUIError) -> str:
    return (
        f"<div class=\"miki-error-page\" role=\"alert\">"
        f"<h1>{error.status_code}</h1>"
        f"<p>{error.message}</p>"
        f"</div>"
    )


__all__ = [
    "MikiUIError",
    "ValidationError",
    "NotFoundError",
    "PermissionError",
    "RateLimitError",
    "ServerError",
    "error_response",
    "log_error",
]
