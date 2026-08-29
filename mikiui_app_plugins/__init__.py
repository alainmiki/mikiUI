"""MikiUI App Plugins package.

Contains plugins for extending MikiUI apps with additional functionality:
- SessionPlugin: Authentication and session management
- APIPlugin: FastAPI endpoint generation from MikiUI routes
- NotificationPlugin: Toast notification system
- Demo: Working example showing plugin usage

Usage:
    from mikiui import MikiApp
    from mikiui_app_plugins import SessionPlugin, NotificationPlugin
    from mikiui_app_plugins.demo import create_demo_app

    app = MikiApp(title="My App")

    # Add session support
    session = SessionPlugin(secret_key="your-secret-key")
    app.use(session)

    # Add notification support
    notifications = NotificationPlugin()
    app.use(notifications)

    # Use the demo's create_demo_app factory
    fastapi_app = create_demo_app(app)

    # Run with uvicorn
    import uvicorn
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
"""

from .api import APIPlugin
from .notifications import NotificationPlugin
from .session import SessionPlugin

__all__ = ["SessionPlugin", "APIPlugin", "NotificationPlugin"]