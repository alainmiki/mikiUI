"""Rate limiting middleware for MikiUI FastAPI apps.

Provides in-memory sliding-window rate limiting with per-key granularity.
No external dependencies required.
"""

from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_DEFAULT_GENERAL_LIMIT = 100
_DEFAULT_GENERAL_WINDOW = 60
_DEFAULT_AUTH_LIMIT = 10
_DEFAULT_AUTH_WINDOW = 60
_DEFAULT_MAX_KEYS = 100_000
_DEFAULT_KEY_TTL = 3600


class _SlidingWindowLimiter:
    """Thread-safe in-memory sliding window rate limiter with eviction."""

    def __init__(
        self,
        max_keys: int = _DEFAULT_MAX_KEYS,
        key_ttl: int = _DEFAULT_KEY_TTL,
    ) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._max_keys = max_keys
        self._key_ttl = key_ttl
        self._first_access: dict[str, float] = {}
        self._evicted_total = 0

    def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        now = time.time()
        self._evict_expired(now)
        self._enforce_max_keys(now)

        window_start = now - window
        timestamps = self._hits[key]
        self._hits[key] = [t for t in timestamps if t > window_start]
        if len(self._hits[key]) >= limit:
            oldest = self._hits[key][0]
            retry_after = int(oldest + window - now) + 1
            return False, retry_after
        self._hits[key].append(now)
        self._first_access.setdefault(key, now)
        return True, 0

    def _evict_expired(self, now: float) -> None:
        cutoff = now - self._key_ttl
        expired = [k for k, first in self._first_access.items() if first < cutoff]
        for key in expired:
            self._hits.pop(key, None)
            self._first_access.pop(key, None)
            self._evicted_total += 1

    def _enforce_max_keys(self, now: float) -> None:
        if len(self._hits) <= self._max_keys:
            return
        overflow = len(self._hits) - int(self._max_keys * 0.8)
        if overflow <= 0:
            return
        sorted_keys = sorted(self._first_access.items(), key=lambda kv: kv[1])
        for key, _ in sorted_keys[:overflow]:
            self._hits.pop(key, None)
            self._first_access.pop(key, None)
            self._evicted_total += 1

    def stats(self) -> dict[str, int]:
        return {
            "active_keys": len(self._hits),
            "evicted_total": self._evicted_total,
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with per-key limits.

    Parameters
    ----------
    general_limit:
        Maximum requests per key per window for general endpoints.
    general_window:
        Window size in seconds for general endpoints.
    auth_limit:
        Maximum requests per key per window for authentication endpoints.
    auth_window:
        Window size in seconds for authentication endpoints.
    auth_path_prefixes:
        Path prefixes that count against the stricter auth limit.
    max_keys:
        Maximum number of tracked keys before oldest keys are evicted.
    key_ttl:
        Time-to-live in seconds for idle keys.
    key_func:
        Optional callable ``(request) -> str`` that returns the rate-limit
        key.  When ``None``, falls back to ``ip:path``.
    """

    def __init__(
        self,
        app: Any,
        general_limit: int = _DEFAULT_GENERAL_LIMIT,
        general_window: int = _DEFAULT_GENERAL_WINDOW,
        auth_limit: int = _DEFAULT_AUTH_LIMIT,
        auth_window: int = _DEFAULT_AUTH_WINDOW,
        auth_path_prefixes: tuple[str, ...] = ("/login", "/auth", "/api/auth"),
        max_keys: int = _DEFAULT_MAX_KEYS,
        key_ttl: int = _DEFAULT_KEY_TTL,
        key_func: Callable[[Request], str] | None = None,
    ) -> None:
        super().__init__(app)
        self._limiter = _SlidingWindowLimiter(max_keys=max_keys, key_ttl=key_ttl)
        self._general_limit = general_limit
        self._general_window = general_window
        self._auth_limit = auth_limit
        self._auth_window = auth_window
        self._auth_path_prefixes = auth_path_prefixes
        self._key_func = key_func

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        path = request.url.path

        limit = self._general_limit
        window = self._general_window
        for prefix in self._auth_path_prefixes:
            if path.startswith(prefix):
                limit = self._auth_limit
                window = self._auth_window
                break

        if self._key_func is not None:
            key = self._key_func(request)
        else:
            ip = request.client.host if request.client else "unknown"
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

    def stats(self) -> dict[str, int]:
        """Return limiter statistics (active keys, total evicted)."""
        return self._limiter.stats()


__all__ = ["RateLimitMiddleware"]
