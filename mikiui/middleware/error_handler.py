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


class ErrorHandlerMiddleware:
    """Catches unhandled exceptions and returns formatted responses.

    Parameters
    ----------
    error_page_template:
        Optional callable ``(status_code, message) -> str`` for HTML error pages.
    """

    def __init__(self, app: Any, error_page_template: Callable[[int, str], str] | None = None) -> None:
        self.app = app
        self._error_page_template = error_page_template
        self._dev = os.getenv("MIKIUI_ENV", "development").lower() != "production"

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            request = Request(scope, receive=receive)
            response = await self._handle(request, exc)
            await response(scope, receive, send)

    async def dispatch(self, request: Request, call_next: Any) -> JSONResponse | HTMLResponse:
        try:
            result = call_next(request)
            if hasattr(result, "__await__"):
                result = await result
            return result if result is not None else HTMLResponse("", status_code=200)
        except Exception as exc:
            return await self._handle(request, exc)

    async def _handle(self, request: Request, exc: Exception) -> JSONResponse | HTMLResponse:
        app = getattr(request.app.state, "miki_app", None)
        if isinstance(exc, MikiUIError):
            log_error(exc, request)
            return await error_response(exc, request, app=app)

        status_code = 500
        error_type = "server_error"
        message = "Internal server error"

        if isinstance(exc, ValueError):
            status_code = 422
            error_type = "validation_error"
            message = str(exc)

        if self._dev:
            detail = traceback.format_exc()
            logger.error("Unhandled exception: %s", detail)
            payload: dict[str, Any] = {
                "status": status_code,
                "error": error_type,
                "message": message,
                "detail": detail,
            }
            return JSONResponse(payload, status_code=status_code)

        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.scope.get("path", "?"),
            exc,
            exc_info=True,
        )
        payload = {
            "status": status_code,
            "error": error_type,
            "message": message,
        }
        return JSONResponse(payload, status_code=status_code)


def register_exception_handlers(app: Any) -> None:
    """Register FastAPI exception handlers for common HTTP errors.

    Parameters
    ----------
    app:
        A FastAPI application instance.
    """
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    miki_app = getattr(app.state, "miki_app", None)

    @app.exception_handler(RequestValidationError)  # type: ignore[untyped-decorator]
    async def _validation_exc_handler(request: Request, exc: RequestValidationError) -> JSONResponse | HTMLResponse:
        errors: dict[str, str] = {}
        for err in exc.errors():
            loc = ".".join(str(part) for part in err.get("loc", []) if part != "body")
            errors[loc] = err.get("msg", "Invalid value")
        miki_error = ValidationError(errors)
        return await error_response(miki_error, request, app=miki_app)

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
        return await error_response(miki_error, request, app=miki_app)

    @app.exception_handler(ValidationError)
    async def _miki_validation_handler(request: Request, exc: ValidationError) -> JSONResponse | HTMLResponse:
        return await error_response(exc, request, app=miki_app)

    @app.exception_handler(MikiUIError)
    async def _miki_error_handler(request: Request, exc: MikiUIError) -> JSONResponse | HTMLResponse:
        return await error_response(exc, request, app=miki_app)

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
        return await error_response(miki_error, request, app=miki_app)


__all__ = ["ErrorHandlerMiddleware", "register_exception_handlers"]
