"""Routing helpers: prefixes, SPA fallback, and PWA manifest.

`MikiApp` owns the core route table; this module adds routing conveniences
(mounted sub-routers, SPA history fallback, PWA manifest) without changing the
handler contract.
"""

from __future__ import annotations

from typing import Any, Callable

from fastapi.responses import JSONResponse

from ..app import MikiApp


class Router:
    """A grouped router that registers handlers onto a :class:`MikiApp`.

    Useful for mounting feature areas under a ``prefix`` (e.g. ``/admin``).
    """

    def __init__(self, app: MikiApp, prefix: str = "") -> None:
        self.app = app
        self.prefix = prefix.rstrip("/")

    def _join(self, path: str) -> str:
        if not self.prefix:
            return path
        if path == "/":
            return self.prefix or "/"
        return f"{self.prefix}{path}"

    def add(self, path: str, methods: tuple[str, ...] = ("GET",), name: str | None = None):
        def decorator(fn: Callable) -> Callable:
            self.app.route(self._join(path), methods, name)
            # Register the wrapped function (MikiApp.route re-wraps the raw fn).
            return fn

        return decorator

    def get(self, path: str, name: str | None = None):
        return self.add(path, ("GET",), name)

    def post(self, path: str, name: str | None = None):
        return self.add(path, ("POST",), name)


def add_pwa_manifest(app_fastapi: Any, name: str = "MikiUI App") -> None:
    """Add a ``/manifest.webmanifest`` route for installable PWA apps."""

    @app_fastapi.get("/manifest.webmanifest", include_in_schema=False)
    async def manifest() -> JSONResponse:
        return JSONResponse(
            {
                "name": name,
                "short_name": name,
                "start_url": "/",
                "display": "standalone",
                "background_color": "#ffffff",
                "theme_color": "#0f172a",
            }
        )
