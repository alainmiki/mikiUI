"""Demo of MikiUI Session and API plugins.

This demo shows how to use the SessionPlugin for authentication
and how to create API endpoints from MikiApp routes.

The SessionPlugin provides:
- create_session(user_id): Create a session, returns token
- validate_session(token): Validate token, returns user_id or None
- destroy_session(token): Clear a session

The APIPlugin converts routes starting with /api/ to JSON endpoints
and generates OpenAPI documentation at /openapi.json and /docs.

Run with:
    mikiui dev --app mikiui_app_plugins.demo:app
"""

from datetime import timedelta

from mikiui import MikiApp, Div, A, H1, P
from mikiui.widgets import Card
from mikiui.backend import create_app

from .session import SessionPlugin
from .notifications import NotificationPlugin


app = MikiApp(title="MikiUI Plugin Demo", lang="en")

# Setup session plugin
session = SessionPlugin(
    secret_key="demo-secret-key-change-in-production",
    session_lifetime=timedelta(hours=24),
)
app.use(session)

# Setup notification plugin
notifications = NotificationPlugin()
app.use(notifications)


@app.route("/")
def home():
    notifications.broadcast("Welcome to MikiUI Plugin Demo!", type="info")
    return Div(
        Card(
            H1("MikiUI Plugin Demo"),
            P("Demonstrates session management, API generation, and notifications."),
            A("API Users →", href="/api/users"),
            class_="max-w-2xl mx-auto mt-10 p-6",
            style="border: 1px solid #ccc; border-radius: 8px",
        ),
    )


@app.route("/api/users")
def api_users():
    return [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
    ]


@app.route("/api/login", methods=["POST"])
def api_login():
    from fastapi import Request
    import json
    body = {"username": "demo-user"}
    token = app.create_session(body["username"])
    return {"token": token, "user_id": body["username"]}


@app.route("/api/logout", methods=["POST"])
def api_logout():
    return {"message": "Logged out successfully"}


def create_demo_app():
    """Create FastAPI app with web pages and API endpoints."""
    from fastapi import FastAPI
    from fastapi.openapi.docs import get_swagger_ui_html
    from mikiui.engine.renderer import render_page

    fastapi_app = FastAPI(title=app.title, version="1.0.0")
    router = fastapi_router = __import__("fastapi").APIRouter()

    @router.get("/")
    async def web_home():
        return render_page(
            home(),
            title=app.title,
            favicon=app.favicon,
            theme=app.theme,
        )

    @router.get("/api/users")
    async def api_users_endpoint():
        result = api_users()
        return {"data": result, "status": "ok"}

    @router.post("/api/login")
    async def api_login_endpoint():
        result = api_login()
        return result

    @router.post("/api/logout")
    async def api_logout_endpoint():
        result = api_logout()
        return result

    @router.get("/docs")
    async def swagger_docs():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{app.title} - API Docs",
        )

    fastapi_app.include_router(router)

    return fastapi_app


if __name__ == "__main__":
    print("MikiUI Session & API Plugin Demo")
    print("=================================")
    print()
    print("To run the demo:")
    print("  mikiui dev --app mikiui_app_plugins.demo:app")
    print()
    print("Or run directly:")
    print("  python -c 'from mikiui_app_plugins.demo import create_demo_app; import uvicorn; uvicorn.run(create_demo_app())'")
    print()
    print("Then visit:")
    print("  http://127.0.0.1:8000/ - Web UI")
    print("  http://127.0.0.1:8000/api/users - API endpoint")
    print("  http://127.0.0.1:8000/docs - Swagger UI")