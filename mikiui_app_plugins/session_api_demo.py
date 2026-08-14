"""Demo of MikiUI Session and API plugins.

This demo shows how to use the SessionPlugin for authentication
and how to create API endpoints from MikiApp routes.

Usage with mikiui dev CLI:
    mikiui dev --app mikiui_app_plugins.session_api_demo:create_app_fastapi
    # or run standalone:
    python -m mikiui_app_plugins.session_api_demo

Then visit:
    http://127.0.0.1:8000/ - Web UI
    http://127.0.0.1:8000/api/users - API endpoint (JSON)
    http://127.0.0.1:8000/api/docs - Swagger UI
    http://127.0.0.1:8000/openapi.json - OpenAPI spec
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, Request, Response, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.testclient import TestClient

from mikiui import MikiApp, Div, A, H1, P
from mikiui.widgets import Card
from mikiui.app.plugins import Plugin


# ============================================================================
# Session Plugin
# ============================================================================

class SessionPlugin(Plugin):
    """Session management and authentication plugin."""

    name = "session"

    def __init__(
        self,
        secret_key: str = None,
        session_lifetime: timedelta = timedelta(hours=24),
        authenticated_user_key: str = "user_id",
    ) -> None:
        self.secret_key = secret_key
        self.session_lifetime = session_lifetime
        self.authenticated_user_key = authenticated_user_key
        self._sessions: dict[str, dict[str, Any]] = {}

    def register(self, app: MikiApp) -> None:
        app.session_plugin = self
        app._sessions = self._sessions
        app._inject_session_methods(self)

    def create_session(self, user_id: str, **data: Any) -> str:
        import secrets
        from datetime import datetime as dt
        token = secrets.token_urlsafe(32)
        self._sessions[token] = {
            "created": dt.utcnow(),
            "expires": dt.utcnow() + self.session_lifetime,
            self.authenticated_user_key: user_id,
            **data,
        }
        return token

    def validate_session(self, token: str) -> str | None:
        from datetime import datetime as dt
        session = self._sessions.get(token)
        if session and dt.utcnow() < session.get("expires"):
            return session.get(self.authenticated_user_key)
        return None

    def destroy_session(self, token: str) -> None:
        self._sessions.pop(token, None)


# ============================================================================
# API Plugin
# ============================================================================

class APIPlugin(Plugin):
    """FastAPI API endpoint generator for MikiApp routes."""

    name = "api"

    def __init__(
        self,
        title: str = "MikiUI API",
        version: str = "1.0.0",
        session_plugin: SessionPlugin | None = None,
    ) -> None:
        self.title = title
        self.version = version
        self.session_plugin = session_plugin
        self._api_router: APIRouter | None = None

    def register(self, app: MikiApp) -> None:
        self._api_router = APIRouter()
        app._api_plugin = self
        self._patch_app_methods(app)

    def _patch_app_methods(self, app: MikiApp) -> None:
        original_route = app.route
        original_get = app.get

        def api_route(path: str, methods: tuple[str, ...] = ("GET",), name: str = None, title: str = None):
            if path.startswith("/api/"):
                def decorator(fn):
                    app.api_routes[path] = (fn, methods)
                    return fn
                return decorator
            return original_route(path, methods, name, title)

        app.route = api_route
        app.get = api_route

    def setup_api_endpoints(self, fastapi_app, miki_app: MikiApp) -> None:
        """Set up API endpoints on a FastAPI app."""
        if not self._api_router:
            return

        router = self._api_router
        api_routes = getattr(miki_app, "api_routes", {})

        bearer = HTTPBearer()
        get_current_user = None

        if self.session_plugin:
            def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer)):
                token = credentials.credentials if credentials else None
                return miki_app.validate_session(token)

        for path, (handler, methods) in api_routes.items():
            async def make_endpoint(handler_fn, route_methods):
                async def endpoint(request: Request):
                    result = handler_fn()
                    return {"data": result, "status": "ok"}
                return endpoint

            router.add_api_route(
                path,
                make_endpoint(handler, methods),
                methods=[m.capitalize() for m in methods],
                name=path.replace("/", "_").strip("_") or "api_route",
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
            return get_redoc_html(openapi_url="/openapi.json", title=f"{self.title} - ReDoc")

        router.api_name = f"{self.title} - API"
        fastapi_app.include_router(router)


# ============================================================================
# Demo App
# ============================================================================

app = MikiApp(title="Session & API Demo")
app.api_routes = {}

session = SessionPlugin(secret_key="demo-secret-key")
app.use(session)

api = APIPlugin(title="Session API Demo", session_plugin=session)


def create_app_fastapi():
    """Factory function for mikiui dev CLI."""
    from mikiui.backend import create_app
    from mikiui.engine.renderer import render_page

    fastapi_app = FastAPI(title=app.title)

    for path, (handler, methods) in app.api_routes.items():
        async def make_endpoint(handler_fn, route_methods):
            async def endpoint(request: Request):
                result = handler_fn()
                return {"data": result, "status": "ok"}
            return endpoint

        fastapi_app.add_api_route(
            path,
            make_endpoint(handler, methods),
            methods=[m.capitalize() for m in methods],
        )

    @fastapi_app.get("/")
    async def home():
        return render_page(
            app._render_fn("/") if hasattr(app, "_render_fn") else Div("Welcome"),
            title=app.title,
            favicon=app.favicon,
            theme=app.theme,
        )

    @fastapi_app.get("/docs")
    async def swagger_ui():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{app.title} - API",
        )

    app._setup_done = True
    return fastapi_app


# Add routes
session.api_routes["/api/users"] = (lambda: [
    {"id": 1, "name": "Alice", "role": "admin"},
    {"id": 2, "name": "Bob", "role": "user"},
    {"id": 3, "name": "Carol", "role": "user"},
], ("GET",))

session.api_routes["/api/items"] = (lambda: {
    "items": [
        {"id": "item-1", "name": "Item One"},
        {"id": "item-2", "name": "Item Two"},
    ],
    "count": 2,
}, ("GET",))

session.api_routes["/api/login"] = (lambda: {"message": "Login endpoint", "status": "success"}, ("POST",))

session.api_routes["/api/logout"] = (lambda: {"message": "Logged out", "status": "success"}, ("POST",))

# Patch route method to support API routes
original_route = app.route

def api_route(path: str, methods: tuple[str, ...] = ("GET",), name: str = None, title: str = None):
    def decorator(fn):
        if path.startswith("/api/"):
            app.api_routes[path] = (fn, methods)
        else:
            app.routes[path] = type('RouteDef', (), {
                'path': path,
                'handler': fn,
                'methods': methods,
                'accepts_ctx': False,
                'name': name,
                'title': title,
            })()
        return fn
    return decorator

app.route = api_route
app.get = api_route

# Add web routes
session.api_routes["/"] = (lambda: Div(
    Card(
        H1("Session & API Plugin Demo"),
        P("This demonstrates authentication and API generation."),
        A("View API Docs →", href="/docs", target="_blank"),
        class_="max-w-2xl mx-auto mt-10 p-6",
        style="border: 1px solid #ccc; border-radius: 8px",
    ),
), ("GET",))


if __name__ == "__main__":
    from mikiui import MikiApp as _ma
    print("Session Plugin Demo")
    print("===================")
    print("Session plugin provides:")
    print("- create_session(user_id): Create a session, returns token")
    print("- validate_session(token): Validate token, get user_id")
    print("- destroy_session(token): Clear session")
    print("")
    print("API Plugin provides:")
    print("- Converts routes starting with /api/ to JSON endpoints")
    print("- Auto-generates OpenAPI spec")
    print("- Provides Swagger UI at /docs")