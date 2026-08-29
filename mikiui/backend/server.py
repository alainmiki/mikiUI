"""FastAPI backend that serves MikiUI apps.

Creates a FastAPI app from a :class:`MikiApp`: each route is exposed, full HTML
is returned on navigation, and HTMX-driven requests (``HX-Request`` header)
receive a fragment for partial / optimistic updates.

Per-page titles are resolved by :func:`~mikiui.app.routes.resolve_title`,
which checks (in order): ``ctx.meta["title"]``, ``route.title``, then the
app's global ``title``.
"""

from __future__ import annotations

import inspect
import logging
import os
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response

from ..app import MikiApp, RouteDef
from ..app.routes import resolve_title
from ..app.static_assets import (
    CachingStaticFiles,
    discover,
    get_asset_mounts,
    init_defaults,
    register_package_root,
    register_plugin_assets,
)
from ..engine.renderer import render_fragment, render_page
from ..middleware.error_handler import ErrorHandlerMiddleware, register_exception_handlers
from ..middleware.request_id import RequestIDMiddleware
from ..router.auth_middleware import AuthMiddleware, ensure_auth_strategies
from ..router.group import _get_route_group
from ..router.middleware import apply_default_middleware
from ..router.router import add_pwa_manifest
from ..runtime.runtime_loader import runtime_scripts
from .api_routes import add_api_routes
from .websocket import mount_websocket

logger = logging.getLogger(__name__)

_RUNTIME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runtime"))


def _register_app_static_roots(miki_app: MikiApp) -> None:
    """Register additional package roots from app-registered themes, widgets,
    components, and plugins so their ``static/`` directories are discovered."""
    seen: set[str] = set()

    # Scan widget/component registry for module-based static dirs
    registry = getattr(miki_app, "registry", None)
    if registry is not None:
        for name, cls in list(getattr(registry, "_registry", {}).items()):
            mod = getattr(cls, "__module__", None)
            if not mod:
                continue
            mod_path = mod.replace(".", os.sep) + ".py"
            if os.path.isfile(mod_path):
                root = os.path.dirname(os.path.abspath(mod_path))
                if root not in seen:
                    seen.add(root)
                    register_package_root(root)

    # Scan theme registry for theme css_path-based static dirs
    theme_registry = getattr(miki_app, "theme_registry", None)
    if theme_registry is not None:
        for theme_name in theme_registry.list_registered():
            theme = theme_registry.get(theme_name)
            if theme and getattr(theme, "css_path", None):
                css_abs = os.path.abspath(theme.css_path)
                root = os.path.dirname(css_abs)
                if os.path.isdir(root) and root not in seen:
                    seen.add(root)
                    register_package_root(root)


def _wrap_endpoint(endpoint: Any, middleware_classes: list[type]) -> Any:
    """Wrap *endpoint* with per-route-group middleware classes."""

    async def _asgi_endpoint(request: Request) -> Any:
        return await endpoint(request)

    call_next = _asgi_endpoint
    for mw_cls in reversed(middleware_classes):
        try:
            mw = mw_cls(call_next)
            _next = call_next

            async def _wrapped(request: Request, _mw: Any = mw, _next: Any = _next) -> Any:
                return await _mw.dispatch(request, _next)

            call_next = _wrapped
        except Exception:
            logger.exception("Failed to apply middleware %s", mw_cls)
    return call_next


class RequestLoggingMiddleware:
    """Logs each request with method, path, status, and duration."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        import time

        request = Request(scope, receive)
        start = time.perf_counter()
        status_code = 500

        async def wrapped_send(message: Any) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
            await send(message)

        await self.app(scope, receive, wrapped_send)
        duration = time.perf_counter() - start
        logger.info(
            "%s %s -> %d (%.3fs)",
            request.method,
            request.url.path,
            status_code,
            duration,
        )


def _make_endpoint(miki_app: MikiApp, route: RouteDef):
    auth_middleware = AuthMiddleware(miki_app)

    async def endpoint(request: Request) -> Response:
        auth_result = auth_middleware.enforce(request, route)
        if auth_result is not None:
            return auth_result

        # Notify plugins of every incoming request (analytics, auth, etc.).
        for plugin in miki_app.plugins:
            try:
                plugin.on_request(request)
            except Exception:
                logger.exception("Plugin %r on_request failed; skipping.", getattr(plugin, "name", plugin))

        path_params = dict(request.path_params) if hasattr(request, "path_params") else {}
        nodes, ctx = await miki_app.invoke(route, request, path_params)
        is_partial = request.headers.get("HX-Request") is not None
        if is_partial:
            return HTMLResponse(render_fragment(nodes))
        scripts = getattr(request.app.state, "runtime_scripts", None)
        page_title = resolve_title(route, ctx, miki_app.title)
        head_extra = miki_app.head_extra_html()
        csp_nonce = getattr(request.state, "csp_nonce", None)
        return HTMLResponse(
            render_page(
                nodes,
                title=page_title,
                lang=miki_app.lang,
                runtime_scripts=scripts,
                theme=miki_app.theme,
                framework=miki_app.style_framework,
                style_mode=miki_app.style_mode,
                daisyui=miki_app.style_daisyui,
                favicon=miki_app.favicon,
                head_extra=head_extra,
                csp_nonce=csp_nonce,
            )
        )

    endpoint.__name__ = f"miki_{route.name}"
    return endpoint


def create_app(
    miki_app: MikiApp,
    runtime: str = "local",
    cors_origins: list[str] | None = None,
    runtime_dir: str | None = None,
    enable_csrf: bool = True,
) -> FastAPI:
    """Create a FastAPI ASGI app from a MikiApp.

    Parameters
    ----------
    miki_app:
        The MikiUI application instance.
    runtime:
        JS runtime mode: ``"local"`` (offline) or ``"cdn"``.
    cors_origins:
        Allowed CORS origins.  When ``None``, CORS middleware is not added.
        Pass ``["*"]`` to allow all origins (development only).
    enable_csrf:
        If ``True`` (default), enable CSRF protection with automatic
        token generation.  Set to ``False`` for API-only apps or when
        using a custom CSRF implementation.
    """
    has_api_plugin = any(
        getattr(p, "name", None) == "api" for p in miki_app.plugins
    )
    ensure_auth_strategies(miki_app)

    # Collect WebSocket routes from plugins (before app construction for lifespan)
    ws_routes: list[dict[str, Any]] = getattr(miki_app, "get_websocket_routes", lambda: [])()
    _ws_managers: list[Any] = []

    async def lifespan(app: FastAPI):
        """Manage startup/teardown for real-time connections."""
        yield
        for mgr in _ws_managers:
            close_all = getattr(mgr, "close_all", None)
            if close_all is not None:
                try:
                    if inspect.iscoroutinefunction(close_all):
                        await close_all()
                    else:
                        close_all()
                except Exception:
                    logger.exception("Error closing WebSocket/SSE manager")

    app = FastAPI(title=miki_app.title, lifespan=lifespan)

    # Health-check endpoint for load balancers and monitoring
    async def _health_check(request: Request) -> Response:
        return JSONResponse({"status": "ok", "app": miki_app.title})

    app.add_api_route("/health", _health_check, methods=["GET"], include_in_schema=False)

    # Initialize and discover static assets from components, widgets, and plugins
    init_defaults()

    # Collect plugin static assets
    plugin_asset_paths: list[tuple[str, list[str]]] = []
    for plugin in miki_app.plugins:
        if hasattr(plugin, "assets"):
            try:
                paths = plugin.assets()
                if paths:
                    plugin_asset_paths.append((plugin.name, paths))
            except Exception:
                logger.exception("Plugin %r assets() failed; skipping.", plugin.name)

    # Discover all static directories
    discover()
    for plugin_name, paths in plugin_asset_paths:
        register_plugin_assets(plugin_name, paths)

    # Mount runtime static files with cache headers for production
    if os.path.isdir(_RUNTIME_DIR):
        app.mount(
            "/_miki/runtime",
            CachingStaticFiles(directory=_RUNTIME_DIR, html=False),
            name="miki-runtime",
        )

    # Discover static directories from built-in roots
    discover()

    # Auto-discover static directories from user-registered themes, widgets,
    # components, and plugins so custom packages can ship their own assets.
    _register_app_static_roots(miki_app)

    # Re-discover after registering app-specific roots
    discover()

    # Mount discovered component/widget/plugin/theme static files
    asset_mounts = get_asset_mounts()
    for url_path, abs_path in asset_mounts.items():
        if os.path.isdir(abs_path):
            mount_name = "miki-static-" + url_path.replace("/", "-").strip("-")
            app.mount(
                url_path,
                CachingStaticFiles(directory=abs_path, html=False),
                name=mount_name,
            )

    # Mount the user project's static/ directory if present
    project_static = os.path.join(os.getcwd(), "static")
    if os.path.isdir(project_static):
        app.mount(
            "/static",
            CachingStaticFiles(directory=project_static, html=False),
            name="miki-project-static",
        )

    # Mount any extra static dirs registered via MikiApp.mount_static()
    for url_path, abs_path in getattr(miki_app, "_static_mounts", []):
        if os.path.isdir(abs_path):
            mount_name = "miki-user-static-" + url_path.replace("/", "-").strip("-")
            app.mount(
                url_path,
                CachingStaticFiles(directory=abs_path, html=False),
                name=mount_name,
            )

    if cors_origins:
        from starlette.middleware.cors import CORSMiddleware

        safe_origins = [o for o in cors_origins if o != "*"]
        if not safe_origins and cors_origins == ["*"]:
            safe_origins = ["*"]

        app.add_middleware(
            CORSMiddleware,
            allow_origins=safe_origins,
            allow_credentials=safe_origins != ["*"],
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=[
                "Accept",
                "Accept-Language",
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-CSRF-Token",
            ],
             max_age=600,
         )

    for route in miki_app.routes.values():
        if has_api_plugin and route.path.startswith("/api/"):
            continue
        endpoint = _make_endpoint(miki_app, route)
        group = _get_route_group(route)
        if group is not None and group.middleware:
            endpoint = _wrap_endpoint(endpoint, group.middleware)
        app.add_api_route(
            route.path,
            endpoint,
            methods=list(route.methods),
            name=route.name,
        )
    util = APIRouter()
    add_api_routes(util, title=miki_app.title)
    app.include_router(util)
    add_pwa_manifest(
        app,
        name=miki_app.title,
        icon=miki_app.favicon,
        theme_color=miki_app.palette_color,
    )

    # Add plugin-provided backend routes
    plugin_routes: list[dict[str, Any]] = getattr(miki_app, "get_backend_routes", lambda: [])()
    if plugin_routes:
        plugin_router = APIRouter()
        for route_def in plugin_routes:
            path = route_def.get("path", "/")
            methods = [m.upper() for m in route_def.get("methods", ["GET"])]
            endpoint = route_def.get("endpoint")
            include_in_schema = route_def.get("include_in_schema", True)
            name = route_def.get("name")
            tags = route_def.get("tags", [])
            if endpoint is not None:
                plugin_router.add_api_route(
                    path=path,
                    endpoint=endpoint,
                    methods=methods,
                    include_in_schema=include_in_schema,
                    name=name,
                    tags=tags,
                )
        app.include_router(plugin_router)

    # Custom 404 handler via exception handler (no catch-all route needed;
    # Starlette raises HTTPException(404) when nothing matches).

    # Add plugin-provided WebSocket routes (collected at top for lifespan)
    if ws_routes:
        ws_router = APIRouter()
        for route_def in ws_routes:
            path = route_def.get("path", "/ws")
            handler = route_def.get("handler")
            manager = route_def.get("manager")
            max_message_size = route_def.get("max_message_size")
            if handler is not None:
                mount_websocket(
                    ws_router,
                    path,
                    handler,
                    manager=manager,
                    max_message_size=max_message_size,
                )
                if manager is not None and manager not in _ws_managers:
                    _ws_managers.append(manager)
        app.include_router(ws_router)

    # Add plugin-provided middleware
    middleware_classes: list[Any] = getattr(miki_app, "get_middleware_classes", lambda: [])()
    for middleware_cls in middleware_classes:
        try:
            app.add_middleware(middleware_cls)
        except Exception:
            logger.exception("Failed to add plugin middleware: %s", middleware_cls)

    # Apply rate limiting from route groups (if any are configured)
    rate_limit_configs = miki_app.get_route_group_rate_limits()
    if rate_limit_configs:
        # Use the strictest general limit across all groups
        min_limit = min(cfg[1] for cfg in rate_limit_configs)
        min_window = min(cfg[2] for cfg in rate_limit_configs)
        # Collect all rate-limited path prefixes
        rate_limited_prefixes = tuple(cfg[0] for cfg in rate_limit_configs)
        from ..router.rate_limit import RateLimitMiddleware
        app.add_middleware(
            RateLimitMiddleware,
            general_limit=min_limit,
            general_window=min_window,
            auth_path_prefixes=("/login", "/auth", "/api/auth", *rate_limited_prefixes),
        )
        logger.info(
            "Rate limiting enabled for prefixes: %s (limit=%d/%ds)",
            rate_limited_prefixes, min_limit, min_window,
        )

    apply_default_middleware(app, enable_csrf=enable_csrf)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)
    register_exception_handlers(app)
    app.state.miki_app = miki_app
    app.state.runtime_scripts = runtime_scripts(runtime)
    return app
