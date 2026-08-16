"""Error handling middleware for MikiUI FastAPI apps.

Catches unhandled exceptions and returns consistent, safe responses.
In production, internal details are hidden. In development, stack traces
are included.
"""

from __future__ import annotations

import logging
import os
import traceback
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from ..errors import (
    MikiUIError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    error_response,
    log_error,
)
from ..errors import (
    PermissionError as MikiPermissionError,
)

logger = logging.getLogger(__name__)

_DEV = os.getenv("MIKIUI_ENV", "development").lower() != "production"


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catches unhandled exceptions and returns formatted responses.

    Parameters
    ----------
    error_page_template:
        Optional callable ``(status_code, message) -> str`` for HTML error pages.
    """

    def __init__(self, app: Any, error_page_template: Callable[[int, str], str] | None = None) -> None:
        super().__init__(app)
        self._error_page_template = error_page_template

    async def dispatch(self, request: Request, call_next: Any) -> JSONResponse | HTMLResponse:
        try:
            return await call_next(request)  # type: ignore[no-any-return]
        except Exception as exc:
            return self._handle(request, exc)

    def _handle(self, request: Request, exc: Exception) -> JSONResponse | HTMLResponse:
        if isinstance(exc, MikiUIError):
            log_error(exc, request)
            return error_response(exc, request)

        status_code = 500
        error_type = "server_error"
        message = "Internal server error"

        if isinstance(exc, ValueError):
            status_code = 422
            error_type = "validation_error"
            message = str(exc)

        if _DEV:
            detail = traceback.format_exc()
            logger.error("Unhandled exception: %s", detail)
            payload: dict[str, Any] = {
                "error": error_type,
                "message": message,
                "detail": detail,
            }
            return JSONResponse(payload, status_code=status_code)

        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.url.path,
            exc,
            exc_info=True,
        )
        error = ServerError(message)
        return error_response(error, request)


def register_exception_handlers(app: Any) -> None:
    """Register FastAPI exception handlers for common HTTP errors.

    Parameters
    ----------
    app:
        A FastAPI application instance.
    """
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    @app.exception_handler(RequestValidationError)
    async def _validation_exc_handler(request: Request, exc: RequestValidationError) -> JSONResponse | HTMLResponse:
        errors: dict[str, str] = {}
        for err in exc.errors():
            loc = ".".join(str(part) for part in err.get("loc", []) if part != "body")
            errors[loc] = err.get("msg", "Invalid value")
        miki_error = ValidationError(errors)
        return error_response(miki_error, request)

    @app.exception_handler(StarletteHTTPException)
    async def _http_exc_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse | HTMLResponse:
        status = exc.status_code
        if status == 404:
            miki_error: MikiUIError = NotFoundError("page")
        elif status == 403:
            miki_error = MikiPermissionError("Access denied")
        elif status == 429:
            miki_error = RateLimitError()
        else:
            miki_error = ServerError(str(exc.detail))
        return error_response(miki_error, request)

    @app.exception_handler(ValidationError)
    async def _miki_validation_handler(request: Request, exc: ValidationError) -> JSONResponse | HTMLResponse:
        return error_response(exc, request)

    @app.exception_handler(MikiUIError)
    async def _miki_error_handler(request: Request, exc: MikiUIError) -> JSONResponse | HTMLResponse:
        return error_response(exc, request)

    @app.exception_handler(Exception)
    async def _catch_all_handler(request: Request, exc: Exception) -> JSONResponse | HTMLResponse:
        if _DEV:
            detail = traceback.format_exc()
            logger.error("Unhandled exception: %s", detail)
            payload = {
                "error": "server_error",
                "message": "Internal server error",
                "detail": detail,
            }
            return JSONResponse(payload, status_code=500)
        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.url.path,
            exc,
            exc_info=True,
        )
        miki_error = ServerError()
        return error_response(miki_error, request)


__all__ = ["ErrorHandlerMiddleware", "register_exception_handlers"]
