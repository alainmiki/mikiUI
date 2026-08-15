"""MikiUI router package (multi-page, SPA, PWA-ready routing)."""

from __future__ import annotations

from .router import Router, add_pwa_manifest
from .middleware import SecurityHeadersMiddleware, apply_default_middleware
from .csrf import CSRFMiddleware
from .rate_limit import RateLimitMiddleware

__all__ = [
    "Router",
    "add_pwa_manifest",
    "SecurityHeadersMiddleware",
    "apply_default_middleware",
    "CSRFMiddleware",
    "RateLimitMiddleware",
]
