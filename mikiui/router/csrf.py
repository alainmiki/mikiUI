"""CSRF protection middleware for MikiUI FastAPI apps.

Validates CSRF tokens on state-changing requests (POST, PUT, PATCH, DELETE).
GET/HEAD/OPTIONS requests are exempt.

Provides :func:`generate_csrf_token` for token creation and
:func:`default_get_session_token` / :func:`default_validate_csrf` for
out-of-the-box CSRF protection using signed cookies.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
_CSRF_HEADER = "X-CSRF-Token"
_CSRF_FIELD = "_csrf"
_DEFAULT_COOKIE_NAME = "mikiui_csrf"
_DEFAULT_TOKEN_TTL = 3600  # 1 hour

logger = logging.getLogger(__name__)


def generate_csrf_token(secret: str, session_id: str = "") -> str:
    """Generate a CSRF token bound to an optional session ID.

    The token is a base64-encoded string with a timestamp and HMAC signature.
    Tokens are time-limited to :data:`_DEFAULT_TTL` seconds.
    """
    timestamp = str(int(time.time()))
    nonce = secrets.token_hex(8)
    data = f"{session_id}:{timestamp}:{nonce}"
    sig = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{timestamp}:{nonce}:{sig}"


def _verify_csrf_token(token: str, secret: str, session_id: str = "") -> bool:
    """Verify a CSRF token's signature and expiry."""
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return False
        timestamp_str, nonce, sig = parts
        # Check expiry
        token_time = int(timestamp_str)
        if abs(time.time() - token_time) > _DEFAULT_TOKEN_TTL:
            return False
        # Verify signature
        data = f"{session_id}:{timestamp_str}:{nonce}"
        expected_sig = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()[:32]
        return hmac.compare_digest(sig, expected_sig)
    except (ValueError, TypeError):
        return False


def default_get_session_token(
    request: Request,
    cookie_name: str = _DEFAULT_COOKIE_NAME,
    secret: str = "",
) -> str | None:
    """Default session token extractor.

    Returns the existing CSRF cookie value, or ``None`` if no cookie exists.
    This means CSRF validation is only active for requests that have already
    received a CSRF cookie (i.e., after a prior GET request).
    """
    return request.cookies.get(cookie_name)


def default_validate_csrf(
    session_token: str,
    csrf_token: str,
    secret: str = "",
) -> bool:
    """Default CSRF validator using double-submit cookie pattern.

    The CSRF token submitted by the client must match the session cookie value.
    This is the double-submit cookie pattern: the cookie is set on the server,
    and the client must echo it back in the header or form field.
    """
    if not session_token or not csrf_token:
        return False
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(session_token, csrf_token)


class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware that validates CSRF tokens on unsafe HTTP methods.

    Parameters
    ----------
    get_session_token:
        Callable that extracts a session token from the request.  Should return
        ``None`` if the request is unauthenticated.  Defaults to
        :func:`default_get_session_token`.
    validate_csrf:
        Callable ``(session_token, csrf_token) -> bool`` that validates the
        CSRF token.  Defaults to :func:`default_validate_csrf`.
    exempt_paths:
        Path prefixes that bypass CSRF validation (e.g. ``["/webhook/"]``).
    cookie_name:
        Name of the CSRF cookie (default: ``mikiui_csrf``).
    secret:
        Secret key for token generation.  If empty, a random key is used
        (tokens will not persist across restarts).
    """

    def __init__(
        self,
        app: Any,
        get_session_token: Callable[[Request], str | None] | None = None,
        validate_csrf: Callable[[str, str], bool] | None = None,
        exempt_paths: list[str] | None = None,
        cookie_name: str = _DEFAULT_COOKIE_NAME,
        secret: str = "",
    ) -> None:
        super().__init__(app)
        self._get_session_token = get_session_token or default_get_session_token
        self._validate_csrf = validate_csrf or default_validate_csrf
        self._exempt_paths = tuple(exempt_paths or [])
        self._cookie_name = cookie_name
        self._secret = secret

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Any:
        if request.method in _SAFE_METHODS:
            response = await call_next(request)
            # Ensure CSRF cookie is set on safe responses
            self._ensure_csrf_cookie(request, response)
            return response

        path = request.url.path
        for prefix in self._exempt_paths:
            if path.startswith(prefix):
                return await call_next(request)

        session_token = self._get_session_token(request)
        if session_token is None:
            # Unauthenticated request — skip CSRF but ensure cookie is set
            response = await call_next(request)
            self._ensure_csrf_cookie(request, response)
            return response

        csrf_token = request.headers.get(_CSRF_HEADER)
        if not csrf_token:
            content_type = request.headers.get("content-type", "")
            if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                form = await request.form()
                raw = form.get(_CSRF_FIELD)
                if isinstance(raw, str):
                    csrf_token = raw

        if not csrf_token or not self._validate_csrf(session_token, csrf_token):
            logger.warning(
                "CSRF validation failed for %s %s from %s",
                request.method,
                path,
                request.client.host if request.client else "?",
            )
            return JSONResponse(
                {"error": "CSRF validation failed", "detail": "Invalid or missing CSRF token"},
                status_code=403,
            )

        response = await call_next(request)
        self._ensure_csrf_cookie(request, response)
        return response

    def _ensure_csrf_cookie(self, request: Request, response: Any) -> None:
        """Ensure the CSRF cookie is present on the response."""
        if self._cookie_name not in request.cookies:
            token = generate_csrf_token(self._secret or secrets.token_hex(16))
            response.set_cookie(
                self._cookie_name,
                token,
                httponly=False,  # Must be readable by JS
                samesite="lax",
                max_age=_DEFAULT_TOKEN_TTL,
                path="/",
            )


def apply_csrf_middleware(
    app: Any,
    secret: str = "",
    exempt_paths: list[str] | None = None,
) -> None:
    """Attach CSRF protection to a FastAPI app with sensible defaults.

    This is the recommended way to enable CSRF protection::

        from mikiui.router.csrf import apply_csrf_middleware
        apply_csrf_middleware(app, secret="your-secret-key")

    Parameters
    ----------
    app:
        A FastAPI/Starlette application.
    secret:
        Secret key for token signing.  Should be consistent across workers.
    exempt_paths:
        Path prefixes to exempt from CSRF (e.g. webhooks).
    """
    app.add_middleware(
        CSRFMiddleware,
        secret=secret,
        exempt_paths=exempt_paths,
    )


__all__ = [
    "CSRFMiddleware",
    "generate_csrf_token",
    "default_get_session_token",
    "default_validate_csrf",
    "apply_csrf_middleware",
]
