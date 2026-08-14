"""Routing primitives for MikiUI.

Defines :class:`RouteDef` (a registered route) and :class:`Ctx` (the context
object handed to route handlers that declare a ``ctx``/``request`` parameter).

Routes can set a per-page title in two beginner-friendly ways:

1.  Via the ``title`` parameter on the decorator::

        @app.route("/about", title="About Us")
        def about(): ...

2.  Via ``ctx.meta`` inside the handler::

        @app.route("/dashboard")
        def dashboard(ctx):
            ctx.meta["title"] = "Dashboard — My App"
            return Dash()

When neither is set, the app's global ``title`` is used.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable

from ..engine.dom import normalize


class Ctx:
    """Passed to route handlers that declare a ``ctx`` / ``request`` parameter.

    Provides access to:

    * ``ctx.request`` — the raw ASGI request (may be ``None``).
    * ``ctx.app`` — the :class:`~mikiui.app.MikiApp` instance.
    * ``ctx.state`` — the app's shared :class:`~mikiui.app.state.AppState`.
    * ``ctx.meta`` — a per-request dict for metadata (e.g. ``"title"``).
    * ``ctx.form()`` — parse incoming form/query params.
    """

    def __init__(self, request: Any, app: "Any") -> None:
        self.request = request
        self.app = app
        self.state = app.state
        self.meta: dict[str, Any] = {}

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
    """A registered route: path, handler, HTTP methods, and call convention.

    ``title`` is a per-page title used in the ``<title>`` tag.  If ``None``,
    the app's global title is used (overridable at render time via
    ``ctx.meta["title"]``).
    """

    __slots__ = ("path", "handler", "methods", "name", "accepts_ctx", "title")

    def __init__(
        self,
        path: str,
        handler: Callable,
        methods: tuple[str, ...],
        name: str | None,
        title: str | None = None,
    ) -> None:
        self.path = path
        self.handler = handler
        self.methods = methods
        self.name = name or getattr(handler, "__name__", "route")
        self.title = title
        params = list(inspect.signature(handler).parameters)
        self.accepts_ctx = bool(params) and params[0] in ("ctx", "request")


def invoke_route(route: RouteDef, app: "Any", request: Any = None):
    """Call a route handler and return a normalized list of renderable nodes."""
    ctx = Ctx(request, app) if route.accepts_ctx else None
    result = route.handler(ctx) if ctx is not None else route.handler()
    return result, ctx


def resolve_title(route: RouteDef, ctx: Ctx | None, fallback: str) -> str:
    """Determine the page title for a route, in priority order:

    1. ``ctx.meta["title"]`` set by the handler
    2. ``route.title`` set on the decorator
    3. ``fallback`` (the app's global title)
    """
    if ctx is not None:
        custom = ctx.meta.get("title")
        if custom:
            return str(custom)
        if route.title:
            return str(route.title)
    elif route.title:
        return str(route.title)
    return fallback


__all__ = ["RouteDef", "Ctx", "invoke_route", "resolve_title", "normalize"]
