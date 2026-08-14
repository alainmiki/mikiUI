"""Routing primitives for MikiUI.

Defines :class:`RouteDef` (a registered route) and :class:`Ctx` (the context
object handed to route handlers that declare a ``ctx``/``request`` parameter).
"""

from __future__ import annotations

import inspect
from typing import Any, Callable

from ..engine.dom import normalize


class Ctx:
    """Passed to route handlers that declare a ``ctx`` / ``request`` parameter.

    Provides access to the active request and the app's shared ``state`` dict
    (used for optimistic / server-side interactivity).
    """

    def __init__(self, request: Any, app: "Any") -> None:
        self.request = request
        self.app = app
        self.state = app.state

    async def form(self) -> dict[str, Any]:
        """Parse the incoming request form/query params (best-effort)."""
        if self.request is None:
            return {}
        if hasattr(self.request, "query_params"):
            data = dict(self.request.query_params)
            try:
                form = await self.request.form()
                data.update(dict(form))
            except Exception:
                pass
            return data
        return {}


class RouteDef:
    """A registered route: path, handler, HTTP methods, and call convention."""

    __slots__ = ("path", "handler", "methods", "name", "accepts_ctx")

    def __init__(
        self,
        path: str,
        handler: Callable,
        methods: tuple[str, ...],
        name: str | None,
    ) -> None:
        self.path = path
        self.handler = handler
        self.methods = methods
        self.name = name or getattr(handler, "__name__", "route")
        params = list(inspect.signature(handler).parameters)
        self.accepts_ctx = bool(params) and params[0] in ("ctx", "request")


def invoke_route(route: RouteDef, app: "Any", request: Any = None):
    """Call a route handler and return a normalized list of renderable nodes."""
    ctx = Ctx(request, app) if route.accepts_ctx else None
    result = route.handler(ctx) if ctx is not None else route.handler()
    return result, ctx


__all__ = ["RouteDef", "Ctx", "invoke_route", "normalize"]
