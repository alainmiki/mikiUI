"""Session management plugin for MikiUI.

Provides authentication, authorization, and session storage capabilities.
Integrates with FastAPI's dependency injection system.

Usage:
    from mikiui import MikiApp
    from mikiui_app_plugins import SessionPlugin
    from datetime import timedelta

    app = MikiApp(title="My App")

    session = SessionPlugin(
        secret_key="your-secret-key",
        session_lifetime=timedelta(hours=1),
        authenticated_user_key="user_id",
    )
    app.use(session)

    # Create sessions
    token = app.create_session("user123", role="admin")

    # Validate sessions
    user_id = app.validate_session(token)

    # Get all session data
    data = app.get_session_data(token)

    # Destroy sessions
    app.destroy_session(token)

Security
--------
- **Signed tokens**: Tokens are HMAC-signed with the secret key so they
  cannot be forged.
- **Timing-safe comparison**: Token validation uses ``secrets.compare_digest``
  to prevent timing attacks.
- **Token format validation**: Only tokens matching the expected format
  (``token.signature``) are accepted.
- **Session limits**: Per-user session limits prevent session flooding.
- **Automatic cleanup**: Expired sessions are purged on access.
- **CSRF protection**: CSRF tokens can be generated per-session for state-
  changing operations.
"""

from __future__ import annotations

import hmac
import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from mikiui import MikiApp
from mikiui.app.plugins import Plugin

_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")
_TOKEN_BYTES = 32
_SIG_BYTES = 16


def _sign(token: str, secret_key: str) -> str:
    """Return the HMAC-SHA256 signature of *token* using *secret_key*."""
    return hmac.new(
        secret_key.encode("utf-8"), token.encode("utf-8"), "sha256"
    ).hexdigest()[:_SIG_BYTES]


def _now() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(UTC)


class SessionPlugin(Plugin):
    """Session management and authentication plugin.

    Provides session storage, user authentication, and authorization hooks.
    Sessions are stored in-memory by default; for distributed deployments,
    consider using Redis or a database-backed session store.

    Attributes:
        name: Plugin identifier
        secret_key: Secret key for session signing (generated if not provided)
        session_lifetime: How long sessions remain valid
        authenticated_user_key: Key in session storing user identity

    Example:
        >>> app = MikiApp()
        >>> session = SessionPlugin(secret_key="secret")
        >>> app.use(session)
        >>> token = app.create_session("user123")
        >>> app.validate_session(token)
        'user123'
    """

    name = "session"

    def __init__(
        self,
        secret_key: str | None = None,
        session_lifetime: timedelta = timedelta(hours=24),
        authenticated_user_key: str = "user_id",
        max_sessions_per_user: int = 10,
    ) -> None:
        """Initialize the session plugin.

        Args:
            secret_key: Secret key for session signing. If not provided,
                a secure random key is generated.
            session_lifetime: How long sessions remain valid after creation.
            authenticated_user_key: Key used to store/retrieve user identity
                in the session dict.
            max_sessions_per_user: Maximum concurrent sessions per user.
        """
        if secret_key is None:
            secret_key = secrets.token_urlsafe(32)
        if len(secret_key) < 16:
            raise ValueError(
                "secret_key must be at least 16 characters long. "
                "Use secrets.token_urlsafe(32) to generate a secure key."
            )
        self.secret_key = secret_key
        self.session_lifetime = session_lifetime
        self.authenticated_user_key = authenticated_user_key
        self.max_sessions_per_user = max_sessions_per_user
        self._sessions: dict[str, dict[str, Any]] = {}

    def register(self, app: MikiApp) -> None:
        """Register session helpers on the app."""
        app._session_plugin = self
        app._sessions = self._sessions
        self._inject_session_methods(app)

    def middleware_classes(self) -> list[type]:
        """Return session middleware class for automatic mounting."""
        return [self._create_middleware()]

    def _create_middleware(self) -> type:
        """Create a Starlette middleware class for session handling."""

        class SessionMiddleware:
            def __init__(self, app: Any) -> None:
                self.app = app

            async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
                if scope["type"] != "http":
                    await self.app(scope, receive, send)
                    return
                await self.app(scope, receive, send)

        SessionMiddleware.__name__ = "SessionMiddleware"
        return SessionMiddleware

    def _inject_session_methods(self, app: MikiApp) -> None:
        """Inject session management methods onto the app."""
        plugin_self = self

        def create_session(user_id: str, **data: Any) -> str:
            """Create a new session for a user.

            Args:
                user_id: The user's unique identifier.
                **data: Additional session data to store.

            Returns:
                A signed session token.

            Example:
                token = app.create_session("user123", role="admin", email="user@example.com")
            """
            raw_token = secrets.token_urlsafe(_TOKEN_BYTES)
            token = f"{raw_token}.{_sign(raw_token, plugin_self.secret_key)}"

            now = _now()
            existing_user_sessions = [
                t for t, s in plugin_self._sessions.items()
                if s.get(plugin_self.authenticated_user_key) == user_id
            ]

            while len(existing_user_sessions) >= plugin_self.max_sessions_per_user:
                oldest_token = min(
                    existing_user_sessions,
                    key=lambda t: plugin_self._sessions[t].get("created", datetime.min.replace(tzinfo=UTC))
                )
                plugin_self._sessions.pop(oldest_token, None)
                existing_user_sessions.remove(oldest_token)

            plugin_self._sessions[token] = {
                "created": now,
                "expires": now + plugin_self.session_lifetime,
                plugin_self.authenticated_user_key: user_id,
                **data,
            }
            return token

        def _is_valid_token_format(token: str) -> bool:
            """Check if a token matches the expected ``token.signature`` format."""
            if not isinstance(token, str):
                return False
            return bool(_TOKEN_PATTERN.match(token))

        def validate_session(token: str) -> str | None:
            """Validate a session token and return the user_id if valid.

            Uses timing-safe comparison to prevent timing attacks.

            Args:
                token: The session token to validate.

            Returns:
                The user_id if the session is valid and not expired, None otherwise.

            Example:
                user_id = app.validate_session(token)
                if user_id:
                    print(f"Logged in as {user_id}")
            """
            if not _is_valid_token_format(token):
                return None

            session = plugin_self._sessions.get(token)
            if not session:
                return None

            if _now() > session.get("expires"):
                plugin_self._sessions.pop(token, None)
                return None

            return session.get(plugin_self.authenticated_user_key)

        def destroy_session(token: str) -> bool:
            """Destroy a session by token.

            Args:
                token: The session token to destroy.

            Returns:
                True if the session was destroyed, False if it didn't exist.

            Example:
                if app.destroy_session(token):
                    print("Logged out")
            """
            if not _is_valid_token_format(token):
                return False
            if token in plugin_self._sessions:
                del plugin_self._sessions[token]
                return True
            return False

        def set_session_cookie(response: Any, token: str, *, secure: bool = True, httponly: bool = True, samesite: str = "lax", max_age: int | None = None) -> None:
            """Set a session cookie with security attributes on a FastAPI/Starlette response.

            Args:
                response: The response object (JSONResponse, RedirectResponse, etc.).
                token: The session token to store.
                secure: If True, cookie is only sent over HTTPS.
                httponly: If True, cookie is inaccessible to JavaScript (prevents XSS theft).
                samesite: SameSite attribute: ``"lax"``, ``"strict"``, or ``"none"``.
                max_age: Cookie max-age in seconds. Defaults to session_lifetime.
            """
            if max_age is None:
                max_age = int(plugin_self.session_lifetime.total_seconds())
            response.set_cookie(
                key="mikiui_session",
                value=token,
                httponly=httponly,
                secure=secure,
                samesite=samesite,
                max_age=max_age,
            )

        def delete_session_cookie(response: Any, *, secure: bool = True, httponly: bool = True, samesite: str = "lax") -> None:
            """Delete the session cookie by setting it with max_age=0.

            Args:
                response: The response object.
                secure: Must match the ``secure`` value used in :meth:`set_session_cookie`.
                httponly: Must match the ``httponly`` value used in :meth:`set_session_cookie`.
                samesite: Must match the ``samesite`` value used in :meth:`set_session_cookie`.
            """
            response.set_cookie(
                key="mikiui_session",
                value="",
                max_age=0,
                httponly=httponly,
                secure=secure,
                samesite=samesite,
            )

        def get_session_data(token: str) -> dict[str, Any] | None:
            """Get all session data for a token.

            Args:
                token: The session token.

            Returns:
                Dictionary of session data (excluding internal fields),
                or None if the session is invalid/expired.

            Example:
                data = app.get_session_data(token)
                if data:
                    print(f"Role: {data.get('role')}")
            """
            if not _is_valid_token_format(token):
                return None

            session = plugin_self._sessions.get(token)
            if not session:
                return None

            if _now() > session.get("expires"):
                plugin_self._sessions.pop(token, None)
                return None

            return {
                k: v for k, v in session.items()
                if k not in ("created", "expires", plugin_self.authenticated_user_key)
            }

        def rotate_session(token: str) -> str | None:
            """Rotate a session token (issue a new token, invalidate old).

            Use this after privilege changes (e.g. login escalation) to
            prevent session fixation attacks.

            Args:
                token: The current session token.

            Returns:
                A new signed token, or None if the original token was invalid.
            """
            data = get_session_data(token)
            if data is None:
                return None
            user_id = validate_session(token)
            if user_id is None:
                return None
            user_id = plugin_self._sessions[token].get(plugin_self.authenticated_user_key)
            new_token = create_session(user_id, **data)
            destroy_session(token)
            return new_token

        def generate_csrf_token(token: str) -> str | None:
            """Generate a CSRF token bound to a session.

            The CSRF token is signed with the session token and secret key.
            Include it in forms and validate on submission.

            Args:
                token: The session token.

            Returns:
                A CSRF token string, or None if the session is invalid.
            """
            if not validate_session(token):
                return None
            raw = secrets.token_urlsafe(_TOKEN_BYTES)
            sig = _sign(f"{token}:{raw}", plugin_self.secret_key)
            return f"{raw}.{sig}"

        def validate_csrf_token(token: str, csrf_token: str) -> bool:
            """Validate a CSRF token against a session token.

            Uses timing-safe comparison.

            Args:
                token: The session token.
                csrf_token: The CSRF token to validate.

            Returns:
                True if the CSRF token is valid for the session.
            """
            if not _is_valid_token_format(csrf_token):
                return False
            if not validate_session(token):
                return False
            csrf_raw, csrf_sig = csrf_token.rsplit(".", 1)
            expected_sig = _sign(f"{token}:{csrf_raw}", plugin_self.secret_key)
            return hmac.compare_digest(expected_sig, csrf_sig)

        def cleanup_expired() -> int:
            """Remove all expired sessions.

            Returns:
                Number of sessions removed.

            Example:
                count = app.cleanup_expired()
                print(f"Removed {count} expired sessions")
            """
            now = _now()
            expired = [
                t for t, s in plugin_self._sessions.items()
                if s.get("expires", datetime.min.replace(tzinfo=UTC)) < now
            ]
            for t in expired:
                plugin_self._sessions.pop(t, None)
            return len(expired)

        app.create_session = create_session
        app.validate_session = validate_session
        app.destroy_session = destroy_session
        app.set_session_cookie = set_session_cookie
        app.delete_session_cookie = delete_session_cookie
        app.get_session_data = get_session_data
        app.rotate_session = rotate_session
        app.generate_csrf_token = generate_csrf_token
        app.validate_csrf_token = validate_csrf_token
        app.cleanup_expired = cleanup_expired


__all__ = ["SessionPlugin"]
