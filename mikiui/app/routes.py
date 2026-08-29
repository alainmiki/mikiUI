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
using ``{param}`` syntax and the handler will receive them as keyword
arguments::

    @app.route("/users/{user_id}")
    def show_user(user_id):
        return Div(f"User {user_id}")

Path parameters are passed as strings by default.  Use FastAPI-style type
hints in the path to request coercion::

    @app.route("/items/{item_id:int}")
    def show_item(item_id: int):
        return Div(f"Item {item_id + 1}")

Supported types: ``int``, ``float``, ``str`` (default), ``path`` (matches
slashes), ``uuid`` (UUID validation).

When the first parameter is named ``ctx`` or ``request``, it receives the
:class:`Ctx` object (which itself provides ``ctx.path_params``,
``ctx.query_params``, and ``ctx.form()``).
"""

from __future__ import annotations

import inspect
import re
import uuid
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from ..engine.dom import normalize
from ..router.auth import AuthRequirement

_PATH_PARAM_RE = re.compile(r"\{(\w+)(?::(\w+))?\}")

# Supported path parameter type coercions
_PATH_PARAM_TYPES: dict[str, Callable[[str], Any]] = {
    "int": int,
    "float": float,
    "str": str,
    "path": str,
    "uuid": uuid.UUID,
}


class _PathParamSpec:
    """A single path parameter specification."""

    __slots__ = ("name", "type_name", "coerce")

    def __init__(self, name: str, type_name: str = "str") -> None:
        if type_name not in _PATH_PARAM_TYPES:
            raise ValueError(
                f"Unknown path parameter type {type_name!r} for {name!r}. "
                f"Supported: {list(_PATH_PARAM_TYPES)}"
            )
        self.name = name
        self.type_name = type_name
        self.coerce = _PATH_PARAM_TYPES[type_name]

    def convert(self, value: str) -> Any:
        """Convert a string path param to the declared type."""
        try:
            return self.coerce(value)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Cannot convert path parameter {self.name!r} to "
                f"{self.type_name}: {value!r} ({exc})"
            ) from exc


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

    ``path_params`` is the list of :class:`_PathParamSpec` extracted from
    ``{param}`` or ``{param:type}`` placeholders in the route path.
    """

    __slots__ = (
        "path",
        "handler",
        "methods",
        "name",
        "accepts_ctx",
        "title",
        "path_params",
        "requires_auth",
        "_auth_requirement",
        "_route_group",
    )

    def __init__(
        self,
        path: str,
        handler: Callable[..., Any],
        methods: tuple[str, ...],
        name: str | None = None,
        title: str | None = None,
        requires_auth: bool = False,
        auth: AuthRequirement | None = None,
    ) -> None:
        self.path = path
        self.handler = handler
        self.methods = methods
        self.name = name or getattr(handler, "__name__", "route")
        self.title = title
        self.requires_auth = requires_auth
        self._auth_requirement = auth
        self._route_group = None
        # Extract {param} or {param:type} placeholders from the path
        self.path_params: list[_PathParamSpec] = self._extract_path_params(path)
        params = list(inspect.signature(handler).parameters)
        self.accepts_ctx = bool(params) and params[0] in ("ctx", "request")

    def get_auth_requirement(self) -> AuthRequirement | None:
        """Return the effective auth requirement for this route."""
        if self._auth_requirement is not None:
            return self._auth_requirement
        if not self.requires_auth:
            return AuthRequirement(strategy="none")
        return None

    @staticmethod
    def _extract_path_params(path: str) -> list[_PathParamSpec]:
        """Extract parameter specs from ``{param}`` or ``{param:type}`` placeholders."""
        return [_PathParamSpec(name, type_name or "str") for name, type_name in _PATH_PARAM_RE.findall(path)]

    def accepts_path_params(self) -> bool:
        """Return True if the handler declares path parameters."""
        return bool(self.path_params)

    def convert_path_params(self, raw: dict[str, str]) -> dict[str, Any]:
        """Convert raw string path parameters to their declared types."""
        result: dict[str, Any] = {}
        for spec in self.path_params:
            if spec.name in raw:
                result[spec.name] = spec.convert(raw[spec.name])
        return result

    @property
    def param_names(self) -> list[str]:
        """List of path param names that match handler parameters."""
        params = list(inspect.signature(self.handler).parameters)
        all_params = set(params)
        return [p.name for p in self.path_params if p.name in all_params]

    @property
    def path_param_names(self) -> list[str]:
        """List of all path parameter names (for backward compatibility)."""
        return [p.name for p in self.path_params]


def invoke_route(
    route: RouteDef,
    app: Any,
    request: Any = None,
    path_params: dict[str, Any] | None = None,
) -> tuple[Any, Any]:
    """Call a route handler and return a ``(result, ctx)`` tuple.

    The ``result`` may be a sync return value or a coroutine (for async
    handlers).  The caller should ``await`` the result if it is awaitable.

    Path parameters are automatically coerced to their declared types
    (e.g. ``{item_id:int}`` converts the string to an ``int``).

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
        ``{"user_id": "42"}``).  These are coerced to declared types.
    """
    raw_params = path_params or {}
    missing = [p.name for p in route.path_params if p.name not in raw_params]
    if missing:
        raise ValueError(
            f"Missing required path parameters for {route.path!r}: {missing!r}. "
            f"Provided: {list(raw_params)}"
        )
    # Coerce path parameters to their declared types
    coerced_params = route.convert_path_params({k: str(v) for k, v in raw_params.items()})
    ctx = Ctx(request, app, coerced_params) if route.accepts_ctx else None
    if ctx is not None:
        kwargs = {p: coerced_params[p] for p in route.param_names if p in coerced_params}
        result = route.handler(ctx, **kwargs)
    elif route.param_names:
        kwargs = {p: coerced_params[p] for p in route.param_names if p in coerced_params}
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

