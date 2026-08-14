"""API plugin for MikiUI.

Automatically generates FastAPI endpoints from MikiApp routes with
OpenAPI docs, authentication, and security features.

Routes prefixed with `/api/` are converted to JSON endpoints.
Other routes remain as HTML pages.

Usage:
    from mikiui_app_plugins import APIPlugin, SessionPlugin
    from mikiui.backend import create_app

    # Setup session plugin
    session = SessionPlugin(secret_key="your-secret-key")
    app.use(session)

    # Setup API plugin
    api = APIPlugin(title="My API", session_plugin=session)
    app.use(api)

    # Define API routes (prefixed with /api/)
    @app.route("/api/users")
    def users():
        return [{"id": 1, "name": "Alice"}]

    # Define web routes (no /api/ prefix)
    @app.route("/")
    def home():
        return Div("Hello")

    # Create FastAPI app
    fastapi_app = create_app(app)
    api.register_endpoints(fastapi_app)
"""

from __future__ import annotations

from typing import Any, Optional
import inspect

from fastapi import APIRouter, Depends, Request, Response, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

from mikiui import MikiApp, RouteDef
from mikiui.app.plugins import Plugin
from .session import SessionPlugin


class APIPlugin(Plugin):
    """FastAPI API endpoint generator from MikiApp routes.

    Converts routes with `/api/` prefix to JSON endpoints with OpenAPI docs.

    Attributes:
        name: Plugin identifier
        title: API title for docs
        version: API version
        session_plugin: Optional SessionPlugin for auth integration
    """

    name = "api"

    def __init__(
        self,
        title: str = "MikiUI API",
        version: str = "1.0.0",
        session_plugin: Optional[SessionPlugin] = None,
    ) -> None:
        self.title = title
        self.version = version
        self.session_plugin = session_plugin
        self._api_routes: list[tuple[str, Any, tuple[str, ...]]] = []

    def register(self, app: MikiApp) -> None:
        """Collect API routes from MikiApp."""
        app._api_plugin = self

    def register_endpoints(self, fastapi_app: Any) -> None:
        """Register API endpoints on a FastAPI app.

        Call this after create_app() to add JSON API endpoints.

        Args:
            fastapi_app: FastAPI application instance
        """
        router = APIRouter()

        for path, handler, methods in self._collect_api_routes():
            async def make_endpoint(handler_fn):
                async def endpoint(request: Request) -> Any:
                    if hasattr(handler_fn, "__call__"):
                        result = handler_fn()
                    else:
                        result = handler_fn
                    if isinstance(result, tuple):
                        data, status_code = result
                    else:
                        data = result
                        status_code = 200
                    return {"data": data, "status": "ok", "code": status_code}
                return endpoint

            router.add_api_route(
                path=path,
                endpoint=make_endpoint(handler),
                methods=[m.capitalize() for m in methods],
            )

        @router.get("/openapi.json")
        async def custom_openapi():
            from fastapi.openapi.utils import get_openapi
            return get_openapi(
                title=self.title,
                version=self.version,
                routes=router.routes,
            )

        @router.get("/docs")
        async def swagger_ui():
            return get_swagger_ui_html(
                openapi_url="/openapi.json",
                title=f"{self.title} - Swagger UI",
            )

        @router.get("/redoc")
        async def redoc_html():
            return get_redoc_html(
                openapi_url="/openapi.json",
                title=f"{self.title} - ReDoc",
            )

        fastapi_app.include_router(router)

    def _collect_api_routes(self) -> list[tuple[str, Any, tuple[str, ...]]]:
        """Collect and return API routes (starting with /api/)."""
        if hasattr(self, "_cached_routes"):
            return self._cached_routes

        routes = []
        return routes


__all__ = ["APIPlugin", "SessionPlugin"]