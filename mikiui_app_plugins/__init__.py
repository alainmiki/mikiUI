"""MikiUI App Plugins package.

Contains plugins for extending MikiUI apps with additional functionality:
- Session: Authentication and session management
- API: FastAPI endpoint generation from MikiUI routes
- (future plugins: Database, Cache, Logging, etc.)

Usage:
    from mikiui_app_plugins import SessionPlugin, APIPlugin

    # Session plugin for authentication
    session = SessionPlugin(secret_key="your-secret-key")
    app.use(session)

    # API plugin for FastAPI endpoints
    api = APIPlugin(session_plugin=session)
    app.use(api)
"""

from .session import SessionPlugin
from .api import APIPlugin

__all__ = ["SessionPlugin", "APIPlugin"]