"""Route groups for MikiUI.

A :class:`RouteGroup` collects routes that share a prefix, auth requirement,
and middleware stack.  Users build groups via :class:`RouteGroupBuilder`
returned by :meth:`MikiApp.route_group`.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .auth import AuthRequirement

# RouteDef is imported lazily to avoid circular imports
# (routes.py imports from router.auth which imports from router.group)


class RateLimitConfig:
    """Rate-limit settings for a route group."""

    def __init__(
        self,
        limit: int = 100,
        window: int = 60,
        *,
        key_func: Callable[[Any], str] | None = None,
    ) -> None:
        self.limit = limit
        self.window = window
        self.key_func = key_func


class CSRFConfig:
    """CSRF settings for a route group."""

    def __init__(
        self,
        exempt_paths: list[str] | None = None,
        exempt_methods: tuple[str, ...] = ("GET", "HEAD", "OPTIONS"),
    ) -> None:
        self.exempt_paths = tuple(exempt_paths or [])
        self.exempt_methods = exempt_methods


class RouteGroup:
    """A named route group with shared configuration.

    Attributes
    ----------
    prefix:
        URL prefix for all routes in this group.
    auth:
        Auth requirement applied to all routes unless overridden.
    middleware:
        Middleware classes applied to all routes in this group.
    rate_limit:
        Optional rate-limit config.
    csrf:
        Optional CSRF config.
    """

    def __init__(
        self,
        app: Any,
        prefix: str,
        *,
        auth: AuthRequirement | None = None,
    ) -> None:
        self._app = app
        self.prefix = prefix.rstrip("/")
        self._auth = auth
        self.middleware: list[type] = []
        self._rate_limit: RateLimitConfig | None = None
        self._csrf: CSRFConfig | None = None

    def use(self, middleware_cls: type) -> RouteGroup:
        """Add a middleware class to this group."""
        self.middleware.append(middleware_cls)
        return self

    def auth(self, requirement: AuthRequirement) -> RouteGroup:
        """Set the auth requirement for this group."""
        self._auth = requirement
        return self

    def rate_limit(
        self,
        limit: int = 100,
        window: int = 60,
        *,
        key_func: Callable[[Any], str] | None = None,
    ) -> RouteGroup:
        """Enable rate limiting for this group."""
        self._rate_limit = RateLimitConfig(
            limit=limit, window=window, key_func=key_func
        )
        return self

    def csrf(
        self,
        exempt_paths: list[str] | None = None,
        exempt_methods: tuple[str, ...] = ("GET", "HEAD", "OPTIONS"),
    ) -> RouteGroup:
        """Enable CSRF protection for this group."""
        self._csrf = CSRFConfig(
            exempt_paths=exempt_paths, exempt_methods=exempt_methods
        )
        return self

    def _resolve_auth(self, route_auth: Any) -> AuthRequirement | None:
        """Return the effective auth requirement for a route.

        Route-level config overrides group-level config.
        """
        if route_auth is None:
            return self._auth
        if isinstance(route_auth, bool):
            if not route_auth:
                return AuthRequirement(strategy="none")
            return self._auth or AuthRequirement(strategy="session")
        return route_auth  # type: ignore[no-any-return]


class RouteGroupBuilder:
    """Fluent builder for :class:`RouteGroup`.

    Returned by :meth:`MikiApp.route_group`.
    """

    def __init__(self, app: Any, prefix: str) -> None:
        self._app = app
        self._group = RouteGroup(app, prefix)
        # Store the group on the app for later retrieval
        if hasattr(app, "_route_groups"):
            app._route_groups[prefix] = self._group

    def use(self, middleware_cls: type) -> RouteGroupBuilder:
        self._group.use(middleware_cls)
        return self

    def auth(self, requirement: AuthRequirement) -> RouteGroupBuilder:
        self._group.auth(requirement)
        return self

    def rate_limit(
        self,
        limit: int = 100,
        window: int = 60,
        *,
        key_func: Callable[[Any], str] | None = None,
    ) -> RouteGroupBuilder:
        self._group.rate_limit(limit=limit, window=window, key_func=key_func)
        return self

    def csrf(
        self,
        exempt_paths: list[str] | None = None,
        exempt_methods: tuple[str, ...] = ("GET", "HEAD", "OPTIONS"),
    ) -> RouteGroupBuilder:
        self._group.csrf(exempt_paths=exempt_paths, exempt_methods=exempt_methods)
        return self

    def get(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        return self._build_decorator("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        return self._build_decorator("POST", path, **kwargs)

    def route(self, path: str, **kwargs: Any) -> Callable[..., Any]:
        return self._build_decorator(kwargs.pop("methods", ("GET",)), path, **kwargs)

    def _build_decorator(self, methods: str | tuple[str, ...], path: str, **kwargs: Any) -> Callable[..., Any]:
        full_path = f"{self._group.prefix}{path}" if path != "/" else self._group.prefix or "/"
        # Resolve auth: explicit kwargs > group-level > None
        explicit_auth = kwargs.get("auth")
        group_auth = self._group._auth if self._group._auth is not None else None
        effective_auth = explicit_auth if explicit_auth is not None else group_auth

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            # Import here to avoid circular import
            from ..app.routes import RouteDef
            # Register the route directly by calling the inner registration
            # logic, bypassing app.route() decorator pattern.
            upper_methods = tuple(m.upper() for m in (methods if isinstance(methods, tuple) else (methods,)))
            resolved_name = kwargs.get("name") or getattr(fn, "__name__", "route")
            title = kwargs.get("title")
            requires_auth = kwargs.get("requires_auth", False)
            # Check for duplicate route name
            existing = next(
                (r for r in self._app.routes.values() if r.name == resolved_name), None
            )
            if existing is not None:
                raise ValueError(
                    f"Route name {resolved_name!r} is already used by {existing.path!r}. "
                    "Pass a unique `name=` to the decorator."
                )
            # Check for duplicate path with overlapping methods
            auth_req = effective_auth
            if full_path in self._app.routes:
                existing_route = self._app.routes[full_path]
                overlap = set(existing_route.methods) & set(upper_methods)
                if overlap:
                    raise ValueError(
                        f"Route {full_path!r} with method(s) {sorted(overlap)} is already "
                        f"registered by {existing_route.name!r}."
                    )
                merged_methods = tuple(sorted(set(existing_route.methods + upper_methods)))
                self._app.routes[full_path] = RouteDef(
                    full_path, fn, merged_methods, resolved_name, title,
                    requires_auth or existing_route.requires_auth,
                    auth=auth_req if auth_req is not None else existing_route._auth_requirement,
                )
            else:
                self._app.routes[full_path] = RouteDef(
                    full_path, fn, upper_methods, resolved_name, title,
                    requires_auth, auth=auth_req,
                )
            route = self._app.routes[full_path]
            route._route_group = self._group
            # Notify plugins
            for plugin in self._app.plugins:
                if hasattr(plugin, "on_route_add"):
                    plugin.on_route_add(full_path, upper_methods, fn)
            return fn

        return decorator


def _get_route_group(route: Any) -> RouteGroup | None:
    """Return the route group attached to a RouteDef, if any."""
    return getattr(route, "_route_group", None)


__all__ = [
    "RouteGroup",
    "RouteGroupBuilder",
    "RateLimitConfig",
    "CSRFConfig",
    "_get_route_group",
]
