"""MikiUI router package (multi-page, SPA, PWA-ready routing)."""

from __future__ import annotations

from .csrf import CSRFMiddleware
from .middleware import SecurityHeadersMiddleware, apply_default_middleware
from .rate_limit import RateLimitMiddleware
from .router import Router, add_pwa_manifest

__all__ = [
    "Router",
    "add_pwa_manifest",
    "SecurityHeadersMiddleware",
    "apply_default_middleware",
    "CSRFMiddleware",
    "RateLimitMiddleware",
]
