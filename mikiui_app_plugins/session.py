"""Session management plugin for MikiUI.

Provides authentication, authorization, and session storage capabilities.
Integrates with FastAPI's dependency injection system.

Usage:
    from mikiui_app_plugins import SessionPlugin

    session = SessionPlugin(
        secret_key="your-secret-key",
        session_lifetime=timedelta(hours=1),
    )
    app.use(session)

    # Create sessions
    token = app.create_session("user123")

    # Validate sessions  
    user_id = app.validate_session(token)

    # Destroy sessions
    app.destroy_session(token)
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Any

from mikiui import MikiApp
from mikiui.app.plugins import Plugin


class SessionPlugin(Plugin):
    """Session management and authentication plugin.

    Provides session storage, user authentication, and authorization hooks.

    Attributes:
        name: Plugin identifier
        secret_key: Secret key for session signing
        session_lifetime: How long sessions remain valid
        authenticated_user_key: Key in session storing user identity
    """

    name = "session"

    def __init__(
        self,
        secret_key: str | None = None,
        session_lifetime: timedelta = timedelta(hours=24),
        authenticated_user_key: str = "user_id",
    ) -> None:
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.session_lifetime = session_lifetime
        self.authenticated_user_key = authenticated_user_key
        self._sessions: dict[str, dict[str, Any]] = {}

    def register(self, app: MikiApp) -> None:
        """Register session helpers on the app."""
        app._session_plugin = self
        app._sessions = self._sessions

        self._inject_session_methods(app)

    def _inject_session_methods(self, app: MikiApp) -> None:
        """Inject session management methods onto the app."""

        def create_session(user_id: str, **data: Any) -> str:
            """Create a new session for a user. Returns session token."""
            token = secrets.token_urlsafe(32)
            self._sessions[token] = {
                "created": datetime.utcnow(),
                "expires": datetime.utcnow() + self.session_lifetime,
                self.authenticated_user_key: user_id,
                **data,
            }
            return token

        def validate_session(token: str) -> str | None:
            """Validate session token and return user_id if valid."""
            if not token:
                return None
            session = self._sessions.get(token)
            if not session:
                return None
            if datetime.utcnow() > session.get("expires"):
                self._sessions.pop(token, None)
                return None
            return session.get(self.authenticated_user_key)

        def destroy_session(token: str) -> None:
            """Destroy a session by token."""
            self._sessions.pop(token, None)

        def get_session_data(token: str) -> dict[str, Any] | None:
            """Get all session data for a token."""
            session = self._sessions.get(token)
            if session and datetime.utcnow() < session.get("expires"):
                return {k: v for k, v in session.items() if k not in ("created", "expires")}
            return None

        app.create_session = create_session
        app.validate_session = validate_session
        app.destroy_session = destroy_session
        app.get_session_data = get_session_data


__all__ = ["SessionPlugin"]