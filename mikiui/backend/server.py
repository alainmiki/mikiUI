"""FastAPI backend that serves MikiUI apps.

Creates a FastAPI app from a :class:`MikiApp`: each route is exposed, full HTML
is returned on navigation, and HTMX-driven requests (``HX-Request`` header or
POST) receive a fragment for partial / optimistic updates.
"""

from __future__ import annotations

import os

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ..app import MikiApp, RouteDef
from ..engine.renderer import render_fragment, render_page
from ..runtime.runtime_loader import runtime_scripts
from .api_routes import add_api_routes

_RUNTIME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runtime"))


def _make_endpoint(miki_app: MikiApp, route: RouteDef):
    async def endpoint(request: Request) -> HTMLResponse:
        nodes = await miki_app.invoke(route, request)
        is_partial = request.headers.get("HX-Request") is not None or request.method == "POST"
        if is_partial:
            return HTMLResponse(render_fragment(nodes))
        scripts = getattr(request.app.state, "runtime_scripts", None)
        return HTMLResponse(
            render_page(
                nodes,
                title=miki_app.title,
                lang=miki_app.lang,
                runtime_scripts=scripts,
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
    for route in miki_app.routes.values():
        app.add_api_route(
            route.path,
            _make_endpoint(miki_app, route),
            methods=list(route.methods),
            name=route.name,
        )
    # Utility endpoints (health / metadata).
    util = APIRouter()
    add_api_routes(util, title=miki_app.title)
    app.include_router(util)
    # Keep a reference so handlers can resolve the underlying app if needed.
    app.state.miki_app = miki_app
    app.state.runtime_scripts = runtime_scripts(runtime)
    return app
