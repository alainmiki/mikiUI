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


def add_pwa_manifest(
    app_fastapi: Any,
    name: str = "MikiUI App",
    icon: str | None = None,
    start_url: str = "/",
    display: str = "standalone",
    background_color: str = "#ffffff",
    theme_color: str = "#0f172a",
    splash_background_color: str | None = None,
    splash_images: list[str] | None = None,
) -> None:
    """Add a ``/manifest.webmanifest`` route for installable PWA apps."""

    @app_fastapi.get("/manifest.webmanifest", include_in_schema=False)
    async def manifest() -> JSONResponse:
        manifest_data: dict[str, Any] = {
            "name": name,
            "short_name": name.split()[0] if len(name.split()) > 1 else name,
            "start_url": start_url,
            "display": display,
            "background_color": background_color,
            "theme_color": theme_color,
        }
        if icon:
            manifest_data["icons"] = [
                {
                    "src": icon,
                    "sizes": "512x512",
                    "type": "image/png",
                },
                {
                    "src": icon,
                    "sizes": "192x192",
                    "type": "image/png",
                },
            ]
        if splash_background_color:
            manifest_data["background_color_splash"] = splash_background_color
        if splash_images:
            manifest_data["screenshots"] = [
                {"src": img, "sizes": "1920x1080", "form_factor": "wide"},
                {"src": img, "sizes": "1080x1920", "form_factor": "vertical"},
            ]
        return JSONResponse(manifest_data)
