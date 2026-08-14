"""Routing helpers: mounted sub-routers with prefixes and PWA manifest.

This module provides :class:`Router` — a lightweight helper for grouping routes
under a common prefix.  A ``Router`` can be created in a separate file/module and
then mounted onto a :class:`~mikiui.app.MikiApp` via ``app.mount(router)``:

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

    # app.py
    from mikiui import MikiApp
    from routes.users import router as user_router

    app = MikiApp()
    app.mount(user_router)


Two usage patterns are supported:

1. **Explicit (no mount needed)** — pass ``app`` to each decorator:

       @router.get(app, "/items")
       def items():
           ...

2. **Mounted (bare decorators)** — mount first, then decorators drop ``app``:

       app.mount(router)

       @router.get("/")
       def items():
           ...

The :class:`Router` delegates all registration to ``MikiApp.route``, keeping
a single source of truth (the app's route dict) while letting developers
organise handlers across files.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Union

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
    app:
        Optional :class:`MikiApp` to register routes on immediately.
        If provided, the **mounted (bare decorator)** form can be used without
        calling ``app.mount(router)`` first.
    """

    def __init__(self, prefix: str = "", app: Optional[MikiApp] = None) -> None:
        self.prefix = prefix.rstrip("/")
        self._app: Optional[MikiApp] = app

    def _join(self, path: str) -> str:
        """Join the router prefix with a route path."""
        if not self.prefix:
            return path
        if path == "/":
            return self.prefix
        return f"{self.prefix}{path}"

    def _resolve_app(self, app: Optional[MikiApp]) -> MikiApp:
        """Determine which MikiApp to register on.

        Resolution order:
        1. Explicit ``app`` argument (if provided)
        2. ``self._app`` bound via mount() or constructor
        """
        target = app or self._app
        if target is None:
            raise RuntimeError(
                "Router is not bound to a MikiApp. "
                "Either pass app explicitly: @router.get(app, '/path'), "
                "or mount first: app.mount(router)."
            )
        return target

    def add(
        self,
        path_or_app: Union[str, MikiApp],
        path: str = "/",
        methods: tuple[str, ...] = ("GET",),
        name: str | None = None,
        title: str | None = None,
    ):
        """Register a handler on the bound app at the prefixed path.

        Works as a decorator in two forms::

            # Explicit app (no mount needed)
            @router.add(app, "/items")
            def items():
                return Div("items")

            # Bare (requires prior mount())
            @router.add("/items")
            def items():
                return Div("items")
        """
        app: Optional[MikiApp]
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
            )(fn)
            return fn

        return decorator

    def route(
        self,
        path_or_app: Union[str, MikiApp],
        path: str = "/",
        methods: tuple[str, ...] = ("GET",),
        name: str | None = None,
        title: str | None = None,
    ):
        """Register a handler at *path* with *methods* (decorator form)."""
        return self.add(path_or_app, path, methods, name, title=title)

    def get(
        self,
        path_or_app: Union[str, MikiApp],
        path: str = "/",
        name: str | None = None,
        title: str | None = None,
    ):
        """Register a GET-only handler."""
        return self.add(path_or_app, path, ("GET",), name, title=title)

    def post(
        self,
        path_or_app: Union[str, MikiApp],
        path: str = "/",
        name: str | None = None,
        title: str | None = None,
    ):
        """Register a POST-only handler."""
        return self.add(path_or_app, path, ("POST",), name, title=title)

    def mount(self, app: MikiApp) -> "Router":
        """Bind this router to *app* for bare-decorator usage.

        After mounting, decorator methods can be called without passing
        ``app`` explicitly::

            router = Router(prefix="/admin")
            app.mount(router)

            @router.get("/")
            def admin_home():
                return Div("Admin")
        """
        self._app = app
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
        The URL the app opens on launch.
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
