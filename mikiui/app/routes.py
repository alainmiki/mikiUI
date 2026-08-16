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

Path Parameters
---------------
Route handlers can accept path parameters.  Declare them in the path string
using FastAPI-style ``{param}`` syntax and the handler will receive them
as keyword arguments::

    @app.route("/users/{user_id}")
    def show_user(user_id: int):
        return Div(f"User {user_id}")

When the first parameter is named ``ctx`` or ``request``, it receives the
:class:`Ctx` object (which itself provides ``ctx.path_params``,
``ctx.query_params``, and ``ctx.form()``).
"""

from __future__ import annotations

import inspect
import re
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from ..engine.dom import normalize

_PATH_PARAM_RE = re.compile(r"\{(\w+)\}")


class Ctx:
    """Passed to route handlers that declare a ``ctx`` / ``request`` parameter.

    Provides access to:

    * ``ctx.request`` — the raw ASGI request (may be ``None``).
    * ``ctx.app`` — the :class:`~mikiui.app.MikiApp` instance.
    * ``ctx.state`` — the app's shared :class:`~mikiui.app.state.AppState`.
    * ``ctx.meta`` — a per-request dict for metadata (e.g. ``"title"``).
    * ``ctx.path_params`` — dict of path parameters extracted from the URL.
    * ``ctx.query_params`` — dict of query string parameters (multi-values preserved).
    * ``ctx.cookies`` — dict of request cookies.
    * ``ctx.url`` — the request URL string.
    * ``ctx.form()`` — async method to parse form / query / path params.
    """

    def __init__(self, request: Any, app: Any, path_params: dict[str, Any] | None = None) -> None:
        self.request = request
        self.app = app
        self.state = app.state
        self.meta: dict[str, Any] = {}
        self.path_params: dict[str, Any] = path_params or {}

    @property
    def query_params(self) -> dict[str, list[str]]:
        """Return the request's query-string parameters as a dict of lists.

        Multi-value parameters (e.g. ``?tag=a&tag=b``) are preserved.
        """
        if self.request is None or not hasattr(self.request, "query_params"):
            return {}
        result: dict[str, list[str]] = defaultdict(list)
        for k, v in self.request.query_params.multi_items():
            result[k].append(v)
        return dict(result)

    @property
    def cookies(self) -> dict[str, str]:
        """Return the request's cookies as a plain dict."""
        if self.request is None or not hasattr(self.request, "cookies"):
            return {}
        return dict(self.request.cookies)

    @property
    def url(self) -> str | None:
        """Return the request URL as a string, or ``None`` if no request."""
        if self.request is None or not hasattr(self.request, "url"):
            return None
        return str(self.request.url)

    async def form(self) -> dict[str, Any]:
        """Parse the incoming request form / query / path params (best-effort).

        Result priority: form body > query string > path params.
        """
        if self.request is None:
            return dict(self.path_params)
        data: dict[str, Any] = dict(self.path_params)
        if hasattr(self.request, "query_params"):
            for k, v in self.request.query_params.multi_items():
                data.setdefault(k, []).append(v) if k in data else data.update({k: v})
            try:
                form = await self.request.form()
                data.update(dict(form))
            except Exception:
                pass
        return data


class RouteDef:
    """A registered route: path, handler, HTTP methods, and call convention.

    ``title`` is a per-page title used in the ``<title>`` tag.  If ``None``,
    the app's global title is used (overridable at render time via
    ``ctx.meta["title"]``).

    ``path_params`` is the list of parameter names extracted from ``{param}``
    placeholders in the route path.
    """

    __slots__ = (
        "path",
        "handler",
        "methods",
        "name",
        "accepts_ctx",
        "title",
        "path_params",
        "param_names",
        "requires_auth",
    )

    def __init__(
        self,
        path: str,
        handler: Callable,
        methods: tuple[str, ...],
        name: str | None,
        title: str | None = None,
        requires_auth: bool = False,
    ) -> None:
        self.path = path
        self.handler = handler
        self.methods = methods
        self.name = name or getattr(handler, "__name__", "route")
        self.title = title
        self.requires_auth = requires_auth
        # Extract {param} placeholders from the path
        self.path_params: list[str] = self._extract_path_params(path)
        params = list(inspect.signature(handler).parameters)
        self.accepts_ctx = bool(params) and params[0] in ("ctx", "request")
        # Handler param names excluding ctx/request — these receive path params
        all_params = set(params)
        self.param_names = [p for p in self.path_params if p in all_params]

    @staticmethod
    def _extract_path_params(path: str) -> list[str]:
        """Extract parameter names from ``{param}`` placeholders in a path.

        Supports FastAPI-style syntax: ``/users/{user_id}``.
        """
        return _PATH_PARAM_RE.findall(path)

    def accepts_path_params(self) -> bool:
        """Return True if the handler declares path parameters."""
        return bool(self.path_params)


def invoke_route(route: RouteDef, app: Any, request: Any = None, path_params: dict[str, Any] | None = None):
    """Call a route handler and return a ``(result, ctx)`` tuple.

    The ``result`` may be a sync return value or a coroutine (for async
    handlers).  The caller should ``await`` the result if it is awaitable.

    Parameters
    ----------
    route:
        The :class:`RouteDef` to invoke.
    app:
        The :class:`MikiApp` instance (passed to ``Ctx``).
    request:
        The raw ASGI request (passed to ``Ctx``).
    path_params:
        Dict of path parameters extracted by FastAPI (e.g.
        ``{"user_id": "42"}``).
    """
    path_params = path_params or {}
    missing = [p for p in route.path_params if p not in path_params]
    if missing:
        raise ValueError(
            f"Missing required path parameters for {route.path!r}: {missing!r}. "
            f"Provided: {list(path_params)}"
        )
    ctx = Ctx(request, app, path_params) if route.accepts_ctx else None
    if ctx is not None:
        kwargs = {p: path_params[p] for p in route.param_names if p in path_params}
        result = route.handler(ctx, **kwargs)
    elif route.param_names:
        kwargs = {p: path_params[p] for p in route.param_names if p in path_params}
        result = route.handler(**kwargs)
    else:
        result = route.handler()
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

