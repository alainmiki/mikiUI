"""Middleware for MikiUI FastAPI apps.

Adds security and PWA-friendly defaults. Middleware is applied to the FastAPI
app produced by :func:`mikiui.backend.create_app`.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds baseline security headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        return response


def apply_default_middleware(app) -> None:
    """Attach MikiUI's default middleware stack to a FastAPI app."""
    app.add_middleware(SecurityHeadersMiddleware)
