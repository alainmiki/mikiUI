"""The user-facing MikiUI application.

`MikiApp` owns routes, shared server-side ``state``, and plugins. Route
handlers return component trees (or strings/lists). They may optionally accept
a :class:`Ctx` (from `mikiui.app.routes`) as their first parameter to access
the request and shared state.
"""

from __future__ import annotations

from typing import Any, Callable

from ..engine.dom import normalize
from .routes import Ctx, RouteDef, invoke_route
from .state import AppState
from .plugins import Plugin


class MikiApp:
    def __init__(self, title: str = "MikiUI App", lang: str = "en") -> None:
        self.title = title
        self.lang = lang
        self.routes: dict[str, RouteDef] = {}
        self.state: AppState = AppState()
        self.plugins: list[Plugin] = []

    # -- routing ---------------------------------------------------------------
    def route(
        self,
        path: str,
        methods: tuple[str, ...] = ("GET",),
        name: str | None = None,
    ):
        def decorator(fn: Callable) -> Callable:
            self.routes[path] = RouteDef(
                path, fn, tuple(m.upper() for m in methods), name
            )
            return fn

        return decorator

    def get(self, path: str, name: str | None = None):
        return self.route(path, ("GET",), name)

    def post(self, path: str, name: str | None = None):
        return self.route(path, ("POST",), name)

    # -- plugins ---------------------------------------------------------------
    def use(self, plugin: Plugin) -> "MikiApp":
        self.plugins.append(plugin)
        plugin.register(self)
        return self

    # -- invocation ------------------------------------------------------------
    async def invoke(self, route: RouteDef, request: Any = None) -> list[Any]:
        """Call a route handler and return a normalized list of renderable nodes."""
        result, _ = invoke_route(route, self, request)
        if hasattr(result, "__await__"):
            result = await result
        tree = normalize(result)
        for plugin in self.plugins:
            tree = plugin.on_render(tree)
        return tree

    def get_route(self, path: str) -> RouteDef | None:
        return self.routes.get(path)
