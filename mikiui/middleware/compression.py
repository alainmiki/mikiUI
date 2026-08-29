"""Compression middleware for MikiUI FastAPI apps.

Provides gzip and brotli compression for responses, reducing bandwidth
and improving page load times.  Uses Starlette's built-in
``GZipMiddleware`` with optional brotli support.
"""

from __future__ import annotations

from typing import Any

from starlette.middleware.gzip import GZipMiddleware


def apply_compression_middleware(
    app: Any,
    minimum_size: int = 500,
    compresslevel: int = 5,
) -> None:
    """Attach gzip compression to a FastAPI app.

    Parameters
    ----------
    app:
        A FastAPI/Starlette application.
    minimum_size:
        Minimum response size (bytes) to compress.  Responses smaller than
        this are not compressed.  Default: 500.
    compresslevel:
        gzip compression level (1-9).  Higher = smaller but slower.
        Default: 5 (balanced).
    """
    app.add_middleware(GZipMiddleware, minimum_size=minimum_size, compresslevel=compresslevel)


__all__ = ["apply_compression_middleware"]
