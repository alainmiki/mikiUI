"""Rate limiting middleware for MikiUI FastAPI apps.

Provides in-memory sliding-window rate limiting with per-IP granularity.
No external dependencies required.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


_DEFAULT_GENERAL_LIMIT = 100
_DEFAULT_GENERAL_WINDOW = 60
_DEFAULT_AUTH_LIMIT = 10
_DEFAULT_AUTH_WINDOW = 60
_AUTH_PATH_PREFIXES = ("/login", "/auth", "/api/auth")


class _SlidingWindowLimiter:
    """Thread-safe in-memory sliding window rate limiter."""

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        now = time.time()
        window_start = now - window
        timestamps = self._hits[key]
        self._hits[key] = [t for t in timestamps if t > window_start]
        if len(self._hits[key]) >= limit:
            oldest = self._hits[key][0]
            retry_after = int(oldest + window - now) + 1
            return False, retry_after
        self._hits[key].append(now)
        return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with per-IP limits.

    Parameters
    ----------
    general_limit:
        Maximum requests per IP per minute for general endpoints.
    general_window:
        Window size in seconds for general endpoints.
    auth_limit:
        Maximum requests per IP per minute for authentication endpoints.
    auth_window:
        Window size in seconds for authentication endpoints.
    auth_path_prefixes:
        Path prefixes that count against the stricter auth limit.
    """

    def __init__(
        self,
        app: Any,
        general_limit: int = _DEFAULT_GENERAL_LIMIT,
        general_window: int = _DEFAULT_GENERAL_WINDOW,
        auth_limit: int = _DEFAULT_AUTH_LIMIT,
        auth_window: int = _DEFAULT_AUTH_WINDOW,
        auth_path_prefixes: tuple[str, ...] = _AUTH_PATH_PREFIXES,
    ) -> None:
        super().__init__(app)
        self._limiter = _SlidingWindowLimiter()
        self._general_limit = general_limit
        self._general_window = general_window
        self._auth_limit = auth_limit
        self._auth_window = auth_window
        self._auth_path_prefixes = auth_path_prefixes

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        ip = request.client.host if request.client else "unknown"
        path = request.url.path

        limit = self._general_limit
        window = self._general_window
        for prefix in self._auth_path_prefixes:
            if path.startswith(prefix):
                limit = self._auth_limit
                window = self._auth_window
                break

        key = f"{ip}:{path}"
        allowed, retry_after = self._limiter.is_allowed(key, limit, window)
        if not allowed:
            response = JSONResponse(
                {"error": "Too many requests", "retry_after": retry_after},
                status_code=429,
            )
            response.headers["Retry-After"] = str(retry_after)
            return response

        return await call_next(request)


__all__ = ["RateLimitMiddleware"]
