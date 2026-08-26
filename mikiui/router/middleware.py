"""Middleware for MikiUI FastAPI apps.

Adds security and PWA-friendly defaults.  Middleware is applied to the FastAPI
app produced by :func:`mikiui.backend.create_app`.

Security headers added:
- ``X-Content-Type-Options: nosniff`` — prevents MIME-type sniffing
- ``X-Frame-Options: DENY`` — prevents clickjacking
- ``Referrer-Policy: no-referrer`` — limits referrer leakage
- ``Content-Security-Policy`` — restricts resource loading sources
- ``Strict-Transport-Security`` — enables HSTS on HTTPS connections
- ``Permissions-Policy`` — restricts browser APIs (camera, mic, location, etc.)
- ``Cross-Origin-Opener-Policy: same-origin`` — prevents cross-origin opener attacks
- ``Cross-Origin-Embedder-Policy: require-corp`` — prevents cross-origin embedder attacks
- ``X-Permitted-Cross-Domain-Policies: none`` — blocks cross-domain policy files
"""

from __future__ import annotations

import secrets
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_CSP_DEFAULT = (
    "default-src 'self'; "
    "script-src-elem 'self' 'unsafe-inline'; "
    "script-src-attr 'unsafe-inline'; "
    "style-src-elem 'self' 'unsafe-inline'; "
    "style-src-attr 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds baseline security headers to every response.

    Parameters
    ----------
    content_security_policy:
        Custom CSP directive string.  When ``None`` (the default) a safe
        baseline policy is applied.
    strict_transport_security:
        HSTS ``max-age`` in seconds.  ``None`` disables HSTS.
    """

    def __init__(
        self,
        app: Any,
        content_security_policy: str | None = _CSP_DEFAULT,
        strict_transport_security: int | None = 31536000,
    ) -> None:
        super().__init__(app)
        self._csp = content_security_policy
        self._hsts = strict_transport_security

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Any:
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
        csp = self._csp or ""
        if nonce:
            csp = csp.replace(
                "script-src-elem 'self' 'unsafe-inline'",
                f"script-src-elem 'self' 'nonce-{nonce}'",
            )
            csp = csp.replace(
                "style-src-elem 'self' 'unsafe-inline'",
                f"style-src-elem 'self' 'nonce-{nonce}'",
            )
        response.headers.setdefault("Content-Security-Policy", csp)
        if self._hsts:
            is_https = (
                request.url.scheme == "https"
                or request.headers.get("X-Forwarded-Proto") == "https"
            )
            if is_https:
                response.headers.setdefault(
                    "Strict-Transport-Security",
                    f"max-age={self._hsts}; includeSubDomains",
                )
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Embedder-Policy", "require-corp")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=(), payment=(), "
            "usb=(), magnetometer=(), gyroscope=(), accelerometer=()",
        )
        return response


def apply_default_middleware(
    app: Any,
    content_security_policy: str | None = _CSP_DEFAULT,
    strict_transport_security: int | None = 31536000,
) -> None:
    """Attach MikiUI's default middleware stack to a FastAPI app.

    Parameters
    ----------
    app:
        A FastAPI/Starlette application instance.
    content_security_policy:
        Custom CSP string, or ``None`` to disable CSP.
    strict_transport_security:
        HSTS max-age in seconds, or ``None`` to disable HSTS.
    """
    app.add_middleware(
        SecurityHeadersMiddleware,
        content_security_policy=content_security_policy,
        strict_transport_security=strict_transport_security,
    )
