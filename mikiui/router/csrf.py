"""CSRF protection middleware for MikiUI FastAPI apps.

Validates CSRF tokens on state-changing requests (POST, PUT, PATCH, DELETE).
GET/HEAD/OPTIONS requests are exempt.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
_CSRF_HEADER = "X-CSRF-Token"
_CSRF_FIELD = "_csrf"


class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware that validates CSRF tokens on unsafe HTTP methods.

    Parameters
    ----------
    get_session_token:
        Callable that extracts a session token from the request.  Should return
        ``None`` if the request is unauthenticated.
    validate_csrf:
        Callable ``(session_token, csrf_token) -> bool`` that validates the
        CSRF token.
    exempt_paths:
        Path prefixes that bypass CSRF validation (e.g. ``["/webhook/"]``).
    """

    def __init__(
        self,
        app: Any,
        get_session_token: Callable[[Request], str | None],
        validate_csrf: Callable[[str, str], bool],
        exempt_paths: list[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._get_session_token = get_session_token
        self._validate_csrf = validate_csrf
        self._exempt_paths = tuple(exempt_paths or [])

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        if request.method in _SAFE_METHODS:
            return await call_next(request)

        path = request.url.path
        for prefix in self._exempt_paths:
            if path.startswith(prefix):
                return await call_next(request)

        session_token = self._get_session_token(request)
        if session_token is None:
            return await call_next(request)

        csrf_token = request.headers.get(_CSRF_HEADER)
        if not csrf_token:
            content_type = request.headers.get("content-type", "")
            if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                form = await request.form()
                csrf_token = form.get(_CSRF_FIELD)

        if not csrf_token or not self._validate_csrf(session_token, csrf_token):
            return JSONResponse(
                {"error": "CSRF validation failed"},
                status_code=403,
            )

        return await call_next(request)


__all__ = ["CSRFMiddleware"]
