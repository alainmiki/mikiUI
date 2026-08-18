"""MikiUI router package (multi-page, SPA, PWA-ready routing)."""

from __future__ import annotations

from .auth import AuthRequirement, get_builtin_strategies
from .auth_middleware import AuthMiddleware, ensure_auth_strategies, resolve_auth_requirement
from .csrf import CSRFMiddleware
from .group import CSRFConfig, RateLimitConfig, RouteGroup, RouteGroupBuilder, _get_route_group
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
    "AuthRequirement",
    "get_builtin_strategies",
    "AuthMiddleware",
    "ensure_auth_strategies",
    "resolve_auth_requirement",
    "RouteGroup",
    "RouteGroupBuilder",
    "RateLimitConfig",
    "CSRFConfig",
    "_get_route_group",
]
