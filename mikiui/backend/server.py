"""FastAPI backend that serves MikiUI apps.

Creates a FastAPI app from a :class:`MikiApp`: each route is exposed, full HTML
is returned on navigation, and HTMX-driven requests (``HX-Request`` header)
receive a fragment for partial / optimistic updates.

Per-page titles are resolved by :func:`~mikiui.app.routes.resolve_title`,
which checks (in order): ``ctx.meta["title"]``, ``route.title``, then the
app's global ``title``.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ..app import MikiApp, RouteDef
from ..app.routes import resolve_title
from ..engine.renderer import render_fragment, render_page
from ..middleware.error_handler import ErrorHandlerMiddleware, register_exception_handlers
from ..router.middleware import apply_default_middleware
from ..router.router import add_pwa_manifest
from ..runtime.runtime_loader import runtime_scripts
from .api_routes import add_api_routes

logger = logging.getLogger(__name__)

_RUNTIME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runtime"))


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
    async def endpoint(request: Request) -> HTMLResponse:
        if route.requires_auth:
            session_cookie = request.cookies.get("mikiui_session")
            if not session_cookie:
                return JSONResponse(
                    {"error": "Unauthorized", "detail": "Login required"},
                    status_code=401,
                    headers={"HX-Redirect": "/login"} if request.headers.get("HX-Request") else {},
                )

        path_params = dict(request.path_params) if hasattr(request, "path_params") else {}
        nodes, ctx = await miki_app.invoke(route, request, path_params)
        is_partial = request.headers.get("HX-Request") is not None
        if is_partial:
            return HTMLResponse(render_fragment(nodes))
        scripts = getattr(request.app.state, "runtime_scripts", None)
        page_title = resolve_title(route, ctx, miki_app.title)
        head_extra = miki_app.head_extra_html()
        return HTMLResponse(
            render_page(
                nodes,
                title=page_title,
                lang=miki_app.lang,
                runtime_scripts=scripts,
                theme=miki_app.theme,
                favicon=miki_app.favicon,
                head_extra=head_extra,
            )
        )

    endpoint.__name__ = f"miki_{route.name}"
    return endpoint


def create_app(
    miki_app: MikiApp,
    runtime: str = "local",
    cors_origins: list[str] | None = None,
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
    """
    app = FastAPI(title=miki_app.title)

    if os.path.isdir(_RUNTIME_DIR):
        app.mount(
            "/_miki/runtime",
            StaticFiles(directory=_RUNTIME_DIR),
            name="miki-runtime",
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

    has_api_plugin = any(
        getattr(p, "name", None) == "api" for p in miki_app.plugins
    )
    for route in miki_app.routes.values():
        if has_api_plugin and route.path.startswith("/api/"):
            continue
        app.add_api_route(
            route.path,
            _make_endpoint(miki_app, route),
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
    plugin_routes = getattr(miki_app, "get_backend_routes", lambda: [])()
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

    # Add plugin-provided middleware
    middleware_classes = getattr(miki_app, "get_middleware_classes", lambda: [])()
    for middleware_cls in middleware_classes:
        try:
            app.add_middleware(middleware_cls)
        except Exception:
            logger.exception("Failed to add plugin middleware: %s", middleware_cls)

    apply_default_middleware(app)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)
    register_exception_handlers(app)
    app.state.miki_app = miki_app
    app.state.runtime_scripts = runtime_scripts(runtime)
    return app
