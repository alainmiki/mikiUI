"""FastAPI backend that serves MikiUI apps.

Creates a FastAPI app from a :class:`MikiApp`: each route is exposed, full HTML
is returned on navigation, and HTMX-driven requests (``HX-Request`` header or
POST) receive a fragment for partial / optimistic updates.

Per-page titles are resolved by :func:`~mikiui.app.routes.resolve_title`,
which checks (in order): ``ctx.meta["title"]``, ``route.title``, then the
app's global ``title``.
"""

from __future__ import annotations

import os

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ..app import MikiApp, RouteDef
from ..app.routes import resolve_title
from ..engine.renderer import render_fragment, render_page
from ..runtime.runtime_loader import runtime_scripts
from .api_routes import add_api_routes
from ..router.middleware import apply_default_middleware
from ..router.router import add_pwa_manifest

_RUNTIME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runtime"))


def _make_endpoint(miki_app: MikiApp, route: RouteDef):
    async def endpoint(request: Request) -> HTMLResponse:
        path_params = dict(request.path_params) if hasattr(request, "path_params") else {}
        nodes, ctx = await miki_app.invoke(route, request, path_params)
        is_partial = request.headers.get("HX-Request") is not None or request.method == "POST"
        if is_partial:
            return HTMLResponse(render_fragment(nodes))
        scripts = getattr(request.app.state, "runtime_scripts", None)
        page_title = resolve_title(route, ctx, miki_app.title)
        return HTMLResponse(
            render_page(
                nodes,
                title=page_title,
                lang=miki_app.lang,
                runtime_scripts=scripts,
                theme=miki_app.theme,
                favicon=miki_app.favicon,
            )
        )

    endpoint.__name__ = f"miki_{route.name}"
    return endpoint


def create_app(miki_app: MikiApp, runtime: str = "local") -> FastAPI:
    app = FastAPI(title=miki_app.title)
    if os.path.isdir(_RUNTIME_DIR):
        app.mount(
            "/_miki/runtime",
            StaticFiles(directory=_RUNTIME_DIR),
            name="miki-runtime",
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
        theme_color=miki_app.palette_color if hasattr(miki_app, "palette_color") else "#0f172a",
    )
    apply_default_middleware(app)
    app.state.miki_app = miki_app
    app.state.runtime_scripts = runtime_scripts(runtime)
    return app
