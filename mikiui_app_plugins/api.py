"""API plugin for MikiUI.

Automatically generates FastAPI endpoints from MikiApp routes with
OpenAPI docs, authentication, and security features.

Routes prefixed with `/api/` are converted to JSON endpoints.
Other routes remain as HTML pages served by the MikiApp's route handlers.

Usage:
    from mikiui import MikiApp, Div, H1
    from mikiui_app_plugins import APIPlugin, SessionPlugin
    from mikiui.backend import create_app

    app = MikiApp(title="My API")

    # Setup session plugin
    session = SessionPlugin(secret_key="your-secret-key")
    app.use(session)

    # Define API routes (prefixed with /api/)
    @app.route("/api/users")
    def users():
        return [{"id": 1, "name": "Alice"}]

    @app.route("/api/login", methods=["POST"])
    def login():
        return {"token": "session-token"}

    # Define web routes (no /api/ prefix)
    @app.route("/")
    def home():
        return H1("Welcome")

    # Create FastAPI app - APIPlugin backend routes are auto-mounted
    fastapi_app = create_app(app)
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import JSONResponse, Response

from mikiui import MikiApp
from mikiui.app.plugins import Plugin
from mikiui.app.routes import RouteDef
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
        openapi_path: str = "/openapi.json",
        docs_path: str = "/docs",
    ) -> None:
        self.title = title
        self.version = version
        self.session_plugin = session_plugin
        self.openapi_path = openapi_path
        self.docs_path = docs_path
        self._routes: dict[str, dict[str, Any]] = {}

    def register(self, app: MikiApp) -> None:
        """Store reference to the MikiApp."""
        app._api_plugin = self
        self._app = app

    def collect_route(
        self,
        path: str,
        handler: Any,
        methods: tuple[str, ...],
        requires_auth: bool = False,
    ) -> None:
        """Collect an API route for later registration.

        Call this from route decorators that need to be exposed as API endpoints.

        Args:
            path: Route path (should start with /api/)
            handler: Route handler function
            methods: HTTP methods for the route
            requires_auth: If True, require a valid session token
        """
        if not path.startswith("/api/"):
            return

        self._routes[path] = {
            "handler": handler,
            "methods": methods,
            "requires_auth": requires_auth,
        }

    def backend_routes(self) -> list[dict[str, Any]]:
        """Return FastAPI route definitions for API endpoints.

        Scans ``app.routes`` for ``/api/`` paths and returns route definitions
        that the backend server will mount automatically.
        """
        route_defs = []
        router = APIRouter()

        if hasattr(self, "_app") and hasattr(self._app, "routes"):
            for path, route_def in self._app.routes.items():
                if path.startswith("/api/"):
                    route_defs.append(self._make_route_def(router, path, route_def))

        for path, route_data in self._routes.items():
            existing_paths = {r.get("path") for r in route_defs}
            if path not in existing_paths:
                route_defs.append(self._make_route_def(router, path, route_data))

        # Add docs routes
        docs_route = {
            "path": self.openapi_path,
            "methods": ["GET"],
            "endpoint": self._make_openapi_endpoint(router),
            "include_in_schema": False,
            "tags": ["docs"],
        }
        route_defs.append(docs_route)

        docs_route2 = {
            "path": self.docs_path,
            "methods": ["GET"],
            "endpoint": self._make_swagger_endpoint(router),
            "include_in_schema": False,
            "tags": ["docs"],
        }
        route_defs.append(docs_route2)

        docs_route3 = {
            "path": "/redoc",
            "methods": ["GET"],
            "endpoint": self._make_redoc_endpoint(router),
            "include_in_schema": False,
            "tags": ["docs"],
        }
        route_defs.append(docs_route3)

        return route_defs

    def _make_route_def(
        self, router: APIRouter, path: str, route_info: dict[str, Any] | RouteDef
    ) -> dict[str, Any]:
        """Create a route definition dict for a single API route."""
        if isinstance(route_info, RouteDef):
            handler = route_info.handler
            methods = route_info.methods
            requires_auth = route_info.requires_auth
        else:
            handler = route_info["handler"]
            methods = route_info["methods"]
            requires_auth = route_info.get("requires_auth", False)

        async def endpoint(request: Request) -> Any:
            if requires_auth and self.session_plugin:
                auth_header = request.headers.get("Authorization", "")
                token = (
                    request.cookies.get("mikiui_session")
                    or auth_header.replace("Bearer ", "")
                )
                app = self._app
                if (
                    not token
                    or not hasattr(app, "validate_session")
                    or not app.validate_session(token)
                ):
                    return JSONResponse(
                        {"error": "Unauthorized", "code": 401},
                        status_code=401,
                    )

            result = handler()
            if isinstance(result, tuple):
                data, status_code = result
            else:
                data = result
                status_code = 200

            if isinstance(data, Response):
                return data

            if isinstance(data, dict) and "data" in data and "status" in data:
                return data

            return {"data": data, "status": "ok", "code": status_code}

        endpoint.__name__ = path.replace("/", "_").strip("_") or "api_root"

        router.add_api_route(
            path=path,
            endpoint=endpoint,
            methods=[m.capitalize() for m in methods],
            include_in_schema=True,
        )

        return {
            "path": path,
            "methods": [m.capitalize() for m in methods],
            "endpoint": endpoint,
            "include_in_schema": True,
            "name": endpoint.__name__,
            "tags": ["api"],
        }

    def _make_openapi_endpoint(self, router: APIRouter):
        async def openapi_json():
            from fastapi.openapi.utils import get_openapi

            return get_openapi(
                title=self.title,
                version=self.version,
                routes=router.routes,
            )

        openapi_json.__name__ = "openapi_json"
        return openapi_json

    def _make_swagger_endpoint(self, router: APIRouter):
        async def swagger_ui():
            return get_swagger_ui_html(
                openapi_url=self.openapi_path,
                title=f"{self.title} - Swagger UI",
            )

        swagger_ui.__name__ = "swagger_ui"
        return swagger_ui

    def _make_redoc_endpoint(self, router: APIRouter):
        async def redoc_html():
            return get_redoc_html(
                openapi_url=self.openapi_path,
                title=f"{self.title} - ReDoc",
            )

        redoc_html.__name__ = "redoc_html"
        return redoc_html

    def register_endpoints(self, fastapi_app: Any) -> None:
        """Backward-compatible: register API endpoints on a FastAPI app.

        .. deprecated::
            Use :meth:`backend_routes` instead. The backend server
            auto-mounts routes returned by this method.
        """
        routes = self.backend_routes()
        for route_def in routes:
            path = route_def.get("path", "/")
            methods = route_def.get("methods", ["GET"])
            endpoint = route_def.get("endpoint")
            include_in_schema = route_def.get("include_in_schema", True)
            name = route_def.get("name")
            tags = route_def.get("tags", [])
            if endpoint is not None:
                fastapi_app.add_api_route(
                    path=path,
                    endpoint=endpoint,
                    methods=methods,
                    include_in_schema=include_in_schema,
                    name=name,
                    tags=tags,
                )


__all__ = ["APIPlugin", "SessionPlugin"]
