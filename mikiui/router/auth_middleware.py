"""Auth middleware and helpers for MikiUI.

Provides :func:`resolve_auth_requirement` to compute the effective
:class:`~mikiui.router.auth.AuthRequirement` for a route, and
:class:`AuthMiddleware` for pluggable per-request auth validation.
"""

from __future__ import annotations

import logging
from typing import Any, cast

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from ..router.auth import AuthRequirement
from ..router.group import _get_route_group

logger = logging.getLogger(__name__)


def resolve_auth_requirement(route: Any) -> AuthRequirement:
    """Return the effective auth requirement for *route*.

    Resolution order:
    1. Route-level ``auth`` (from RouteGroupBuilder or explicit ``auth=``).
    2. Route-level ``requires_auth`` (legacy boolean).
    3. Route-group-level ``auth``.
    4. Default ``AuthRequirement(strategy="none")``.
    """
    group = _get_route_group(route)
    if group is not None and group._auth is not None:
        group_req = group._auth
    else:
        group_req = None

    route_req = getattr(route, "_auth_requirement", None)
    if route_req is not None:
        return cast(AuthRequirement, route_req)

    if getattr(route, "requires_auth", False):
        return group_req or AuthRequirement(strategy="session")

    return group_req or AuthRequirement(strategy="none")


class AuthMiddleware:
    """Pluggable auth middleware factory.

    This is not a Starlette middleware class itself.  Instead, it provides
    helpers that ``create_app`` calls per-route to enforce auth using
    strategies registered on the app.
    """

    def __init__(self, app: Any) -> None:
        self._app = app

    def enforce(self, request: Request, route: Any) -> Response | None:
        """Validate the request against *route*'s auth requirement.

        Returns a JSONResponse if auth fails, or ``None`` if auth passes
        or is not required.
        """
        requirement = resolve_auth_requirement(route)
        if requirement.is_public():
            return None

        strategy_name = requirement.strategy
        strategy = self._app.get_auth_strategy(strategy_name)
        if strategy is None:
            logger.error(
                "Auth strategy %r is not registered; failing closed for %s %s.",
                strategy_name,
                getattr(request, "method", "?"),
                getattr(request, "url", "?"),
            )
            return JSONResponse(
                {"error": "ServiceUnavailable", "detail": "Auth infrastructure not configured."},
                status_code=503,
            )

        user = strategy.validate(request)
        if user is None:
            is_hx = request.headers.get("HX-Request") is not None
            redirect_url = requirement.redirect_to or "/login"
            if is_hx:
                # HTMX: return HX-Redirect header for client-side redirect
                return JSONResponse(
                    {"error": "Unauthorized", "detail": "Login required"},
                    status_code=401,
                    headers={"HX-Redirect": redirect_url},
                )
            # Browser navigation: check if it's an API/AJAX request
            accept = request.headers.get("accept", "")
            is_json_request = (
                "application/json" in accept
                or request.headers.get("X-Requested-With") == "XMLHttpRequest"
            )
            if is_json_request:
                return JSONResponse(
                    {"error": "Unauthorized", "detail": "Login required"},
                    status_code=401,
                    headers={"WWW-Authenticate": 'Bearer realm="mikiui"'},
                )
            # Regular browser request: redirect to login
            return RedirectResponse(
                url=f"{redirect_url}?next={str(request.url.path)}",
                status_code=303,
            )

        request.state.mikiui_user = user
        return None


def _get_session_strategy_from_plugins(app: Any) -> Any | None:
    """Attempt to extract a session strategy from SessionPlugin."""
    for plugin in getattr(app, "plugins", []):
        if getattr(plugin, "name", "") == "session":
            plugin_self = plugin

            class _SessionStrategy:
                name = "session"

                def validate(self, request: Any) -> Any | None:
                    token = (
                        request.cookies.get(getattr(plugin_self, "authenticated_user_key", "mikiui_session"))
                        or request.headers.get("Authorization", "").replace("Bearer ", "")
                    )
                    if not token:
                        return None
                    validate = getattr(plugin_self, "validate_session", None)
                    if validate is None:
                        return None
                    user_id = validate(token)
                    return user_id

            return _SessionStrategy()
    return None


def ensure_auth_strategies(app: Any) -> None:
    """Register built-in auth strategies on *app* if not already present."""
    if app.get_auth_strategy("session") is None:
        strategy = _get_session_strategy_from_plugins(app)
        if strategy is not None:
            app.register_auth_strategy("session", strategy)


__all__ = [
    "AuthMiddleware",
    "resolve_auth_requirement",
    "ensure_auth_strategies",
]
