"""Routing helpers: mounted sub-routers with prefixes and PWA manifest.

This module provides :class:`Router` — a lightweight helper for grouping routes
under a common prefix.  A ``Router`` can be created in a separate file/module and
then mounted onto a :class:`~mikiui.app.MikiApp` via ``app.mount(router)``.

**Mounted (bare decorator) form** — the recommended pattern::

    # routes/users.py
    from mikiui.router import Router
    from mikiui import Div

    router = Router(prefix="/users")

    @router.get("/")
    def list_users():
        return Div("User list")

    @router.get("/profile")
    def profile():
        return Div("Profile page")

    @router.post("/create")
    def create_user():
        return Div("User Created")

    # app.py
    from mikiui import MikiApp
    from routes.users import router as user_router

    app = MikiApp()
    app.mount(user_router)

**Explicit form** — pass the app to each decorator (no mount needed)::

    router = Router(prefix="/admin")
    app = MikiApp()

    @router.get(app, "/dashboard")
    def admin_dashboard():
        return Div("Admin Dashboard")

The :class:`Router` delegates all registration to ``MikiApp.route``, keeping a
single source of truth (the app's route dict) while letting developers organise
handlers across files.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi.responses import JSONResponse

from ..app import MikiApp


class Router:
    """A grouped router that registers handlers onto a :class:`MikiApp`.

    Useful for mounting feature areas under a ``prefix`` (e.g. ``/admin``).
    Routes are registered directly onto the app so they participate in the
    same route table, HTMX partial-update handling, and title resolution as
    routes declared with ``@app.route(...)``.

    Parameters
    ----------
    prefix:
        URL prefix applied to every route added through this router.
        Trailing slashes are stripped automatically.
    """

    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix.rstrip("/")
        self._app: MikiApp | None = None
        self._parent: Router | None = None

    def _join(self, path: str) -> str:
        """Join the router prefix with a route path."""
        if not self.prefix:
            return path
        if path == "/":
            return self.prefix
        return f"{self.prefix}{path}"

    def _resolve_app(self, app: MikiApp | None = None) -> MikiApp:
        """Return the bound app, preferring an explicitly-passed app."""
        target = app or self._app
        if target is None and self._parent is not None:
            target = self._parent._resolve_app()
        if target is None:
            raise RuntimeError(
                "Router is not bound to a MikiApp. "
                "Either pass app explicitly: @router.get(app, '/path'), "
                "or mount first: app.mount(router)."
            )
        return target

    def add(
        self,
        path_or_app: str | MikiApp,
        path: str = "/",
        methods: tuple[str, ...] = ("GET",),
        name: str | None = None,
        title: str | None = None,
        requires_auth: bool = False,
    ) -> Callable[[Callable], Callable]:
        """Register a handler on the bound app at the prefixed path.

        Supports two calling conventions::

            # Explicit app (no mount needed)
            @router.add(app, "/items")
            def items():
                return Div("items")

            # Bare (requires prior mount())
            @router.add("/items")
            def items():
                return Div("items")

        Set ``requires_auth=True`` to require a valid session token (requires
        :class:`~mikiui_app_plugins.api.APIPlugin` to be active).
        """
        app: MikiApp | None
        if isinstance(path_or_app, str):
            path = path_or_app
            app = None
        else:
            app = path_or_app

        def decorator(fn: Callable) -> Callable:
            target = self._resolve_app(app)
            target.route(
                self._join(path),
                methods,
                name,
                title=title,
                requires_auth=requires_auth,
            )(fn)
            return fn

        return decorator

    def route(
        self,
        path_or_app: str | MikiApp,
        path: str = "/",
        methods: tuple[str, ...] = ("GET",),
        name: str | None = None,
        title: str | None = None,
        requires_auth: bool = False,
    ) -> Callable[[Callable], Callable]:
        """Register a handler at *path* with *methods* (decorator form)."""
        return self.add(path_or_app, path, methods, name, title=title, requires_auth=requires_auth)

    def get(
        self,
        path_or_app: str | MikiApp,
        path: str = "/",
        name: str | None = None,
        title: str | None = None,
        requires_auth: bool = False,
    ) -> Callable[[Callable], Callable]:
        """Register a GET-only handler."""
        return self.add(path_or_app, path, ("GET",), name, title=title, requires_auth=requires_auth)

    def post(
        self,
        path_or_app: str | MikiApp,
        path: str = "/",
        name: str | None = None,
        title: str | None = None,
        requires_auth: bool = False,
    ) -> Callable[[Callable], Callable]:
        """Register a POST-only handler."""
        return self.add(path_or_app, path, ("POST",), name, title=title, requires_auth=requires_auth)

    def mount(self, target: MikiApp | Router) -> Router:
        """Bind this router to *target* for bare-decorator usage.

        *target* may be a :class:`MikiApp` (registers routes directly) or
        another :class:`Router` (propagates the combined prefix and parent chain).

        After mounting, decorator methods can be called without passing
        ``app`` explicitly::

            router = Router(prefix="/admin")
            app.mount(router)

            @router.get("/")
            def admin_home():
                return Div("Admin")

        Nested routers are supported::

            api = Router(prefix="/api")
            v1 = Router(prefix="/v1")
            api.mount(v1)          # v1 inherits /api prefix and parent chain
            app.mount(api)         # v1 routes live under /api/v1/...

            @v1.get("/items")
            def items():
                return Div("items")  # mounted at /api/v1/items
        """
        if isinstance(target, Router):
            combined = (self.prefix or "") + (target.prefix or "")
            target.prefix = combined.rstrip("/")
            target._parent = self
        else:
            self._app = target
        return self



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
    """Add a ``/manifest.webmanifest`` route for installable PWA apps.

    Parameters
    ----------
    app_fastapi:
        A FastAPI instance (typically from :func:`mikiui.backend.create_app`).
    name:
        Full app name shown on the home screen / app switcher.
    icon:
        URL to the app icon (512x512 recommended).
    start_url:
        The URL the app opens at launch.
    display:
        CSS ``display-mode`` value (e.g. ``"standalone"``, ``"fullscreen"``).
    background_color:
        Splash screen background color.
    theme_color:
        Browser UI theme color.
    splash_background_color:
        Android splash background color (overrides ``background_color``
        on Android devices).
    splash_images:
        List of screenshot image URLs for the PWA install dialog.
    """

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
