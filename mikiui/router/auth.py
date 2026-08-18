"""Auth primitives for MikiUI.

Provides :class:`AuthRequirement` (declarative per-route auth config) and
the :class:`AuthStrategy` protocol that concrete auth backends implement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


@dataclass
class AuthRequirement:
    """Declarative auth configuration for a route or route group.

    Attributes
    ----------
    strategy:
        Name of the auth strategy to use. Built-in values: ``"session"``,
        ``"jwt"``, ``"token"``, ``"none"``.
    cookie_name:
        Cookie to read for the session token. Defaults to ``"mikiui_session"``
        for the ``"session"`` strategy.
    header_name:
        HTTP header to read for the token. Defaults to ``"Authorization"``.
    query_param:
        Query-string parameter to read as fallback.
    scopes:
        Required scopes/roles. An empty list means "authenticated" only.
    redirect_to:
        Where to send unauthenticated browser clients. Defaults to ``"/login"``.
    """

    strategy: str = "none"
    cookie_name: str | None = None
    header_name: str | None = None
    query_param: str | None = None
    scopes: list[str] = field(default_factory=list)
    redirect_to: str | None = "/login"

    def effective_cookie_name(self) -> str:
        return self.cookie_name or "mikiui_session"

    def effective_header_name(self) -> str:
        return self.header_name or "Authorization"

    def is_public(self) -> bool:
        return self.strategy == "none"


class AuthStrategy(Protocol):
    """Protocol that auth strategies must implement."""

    name: str

    def validate(self, request: Any) -> Any | None:
        """Return the authenticated user/principal, or ``None``."""
        ...


class _BuiltinSessionStrategy:
    """Default session strategy (no-op placeholder).

    The real implementation lives in :class:`mikiui_app_plugins.session.SessionPlugin`
    which registers itself under ``"session"``.
    """

    name = "session"

    def validate(self, request: Any) -> Any | None:
        return None


class _BuiltinTokenStrategy:
    """Simple bearer-token strategy (no validation — opt-in only)."""

    name = "token"

    def validate(self, request: Any) -> Any | None:
        return None


_BUILTIN_STRATEGIES: dict[str, AuthStrategy] = {
    "session": _BuiltinSessionStrategy(),
    "token": _BuiltinTokenStrategy(),
}


def get_builtin_strategies() -> dict[str, AuthStrategy]:
    """Return the built-in auth strategies."""
    return dict(_BUILTIN_STRATEGIES)


__all__ = [
    "AuthRequirement",
    "AuthStrategy",
    "get_builtin_strategies",
]
