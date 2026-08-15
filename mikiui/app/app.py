"""The user-facing MikiUI application.

`MikiApp` owns routes, shared server-side ``state``, and plugins. Route
handlers return component trees (or strings/lists). They may optionally accept
a :class:`Ctx` (from `mikiui.app.routes`) as their first parameter to access
the request and shared state.
"""

from __future__ import annotations

import html as _html
import logging
from typing import Any, Callable

from ..engine.dom import normalize
from ..themes import Theme, register_theme, get_theme, list_themes
from .routes import Ctx, RouteDef, invoke_route
from .state import AppState
from .plugins import Plugin

logger = logging.getLogger(__name__)


def _esc(value: Any) -> str:
    """Escape a value for safe insertion into an HTML attribute or text node."""
    return _html.escape(str(value), quote=True)


class MikiApp:
    def __init__(
        self,
        title: str = "MikiUI App",
        lang: str = "en",
        favicon: str | None = None,
        desktop_icon: str | None = None,
        splash_screen: str | None = None,
    ) -> None:
        self.title = title
        self.lang = lang
        self.routes: dict[str, RouteDef] = {}
        self.state: AppState = AppState()
        self.plugins: list[Plugin] = []
        self.theme: str = "light"
        self.favicon: str | None = favicon or "/_miki/runtime/mikiui-icon.png"
        self.desktop_icon: str | None = desktop_icon
        self.splash_screen: str | None = splash_screen
        self.palette_color: str = "#0f172a"
        self._head_meta: list[dict[str, str]] = []
        self._head_links: list[dict[str, str]] = []
        self._head_scripts: str = ""

    # -- routing ---------------------------------------------------------------
    def route(
        self,
        path: str,
        methods: tuple[str, ...] = ("GET",),
        name: str | None = None,
        title: str | None = None,
        requires_auth: bool = False,
    ):
        """Register a route handler for *path*.

        Supports FastAPI-style path parameters::

            @app.route("/users/{user_id}")
            def show_user(ctx, user_id):
                return Div(f"User {user_id}")

        Parameters
        ----------
        path:
            URL path.  Use ``{param}`` for path parameters.
        methods:
            Tuple of HTTP methods.
        name:
            Route name (defaults to the handler function name).
        title:
            Per-page ``<title>`` tag content.
        requires_auth:
            If ``True``, require a valid session token when the APIPlugin is
            active.
        """
        def decorator(fn: Callable) -> Callable:
            upper_methods = tuple(m.upper() for m in methods)
            if path in self.routes:
                existing = self.routes[path]
                raise ValueError(
                    f"Route {path!r} is already registered by {existing.name!r}. "
                    "Use a different path or remove the existing route first."
                )
            self.routes[path] = RouteDef(
                path, fn, upper_methods, name, title, requires_auth
            )
            for plugin in self.plugins:
                if hasattr(plugin, "on_route_add"):
                    plugin.on_route_add(path, upper_methods, fn)
            return fn

        return decorator

    def mount(self, router: "Router", *, prefix: str | None = None) -> "MikiApp":
        """Mount a :class:`~mikiui.router.Router` onto this app.

        After mounting, the router's decorator methods (``router.get``,
        ``router.post``, ``router.route``) can be used in their bare form
        (without passing the app explicitly):

            from mikiui.router import Router

            router = Router(prefix="/admin")
            app.mount(router)

            @router.get("/")
            def admin_home():
                return Div("Admin")

        Parameters
        ----------
        router:
            A :class:`~mikiui.router.Router` instance whose ``prefix``
            determines the route grouping.
        prefix:
            Optional override for the router's prefix.  When ``None`` (the
            default) the router's own ``prefix`` attribute is used.
        """
        from ..router.router import Router as _Router

        if not isinstance(router, _Router):
            raise TypeError(
                f"Expected a Router instance, got {type(router).__name__}"
            )
        if prefix is not None:
            router.prefix = prefix.rstrip("/")
        router.mount(self)
        return self

    def get(self, path: str, name: str | None = None, title: str | None = None):
        return self.route(path, ("GET",), name, title)

    def post(self, path: str, name: str | None = None, title: str | None = None):
        return self.route(path, ("POST",), name, title)

    # -- themes ---------------------------------------------------------------
    def set_theme(self, name: str) -> "MikiApp":
        """Activate a registered theme by name."""
        if name not in list_themes():
            raise ValueError(f"Unknown theme: {name!r}. Available: {', '.join(list_themes())}")
        self.theme = name
        return self

    def set_favicon(
        self,
        favicon: str,
        sizes: tuple[int, int] | None = None,
        theme_color: str = "#0f172a",
    ) -> "MikiApp":
        """Set or change the favicon at runtime."""
        self.favicon = favicon
        self.palette_color = theme_color
        return self

    def register_theme(self, theme: Theme) -> "MikiApp":
        """Register a custom or plugin theme and activate it."""
        register_theme(theme)
        self.theme = theme.name
        return self

    def set_head_meta(self, name: str, content: str, **extra: Any) -> "MikiApp":
        """Add a ``<meta>`` tag to the page head.

        Parameters
        ----------
        name : str
            Meta tag name (e.g. "description", "author", "viewport").
        content : str
            Meta tag content value.
        **extra : Additional HTML attributes for the meta tag.

        Example
        -------
        >>> app.set_head_meta("description", "My app description")
        >>> app.set_head_meta("viewport", "width=device-width, initial-scale=1")
        """
        tag = {"name": name, "content": content}
        tag.update(extra)
        self._head_meta.append(tag)
        return self

    def add_head_link(self, href: str, rel: str = "stylesheet", **attrs: Any) -> "MikiApp":
        """Add a ``<link>`` tag to the page head.

        Parameters
        ----------
        href : str
            URL or path to the resource.
        rel : str
            Relationship type (default "stylesheet").
        **attrs : Additional HTML attributes.

        Example
        -------
        >>> app.add_head_link("/static/bootstrap.min.css", rel="stylesheet")
        >>> app.add_head_link("/static/app.js", rel="modulepreload")
        """
        tag = {"href": href, "rel": rel}
        tag.update(attrs)
        self._head_links.append(tag)
        return self

    def add_head_script(self, src: str, **attrs: Any) -> "MikiApp":
        """Add a ``<script>`` tag to the page head.

        Parameters
        ----------
        src :
            URL or path to the JavaScript file.
        **attrs : Additional HTML attributes (e.g., type="module", defer=True).

        Example
        -------
        >>> app.add_head_script("/static/bootstrap.bundle.min.js")
        >>> app.add_head_script("/static/app.js", type="module")
        """
        tag = f'<script src="{_esc(src)}"'
        for k, v in attrs.items():
            tag += f' {_esc(k)}="{_esc(v)}"'
        tag += "></script>\n"
        self._head_scripts += tag
        return self

    def head_extra_html(self) -> str:
        """Build the HTML string for all head extras (internal use)."""
        parts: list[str] = []
        for meta in self._head_meta:
            attrs = " ".join(f'{_esc(k)}="{_esc(v)}"' for k, v in meta.items())
            parts.append(f"<meta {attrs}>")
        for link in self._head_links:
            attrs = " ".join(f'{_esc(k)}="{_esc(v)}"' for k, v in link.items())
            parts.append(f'<link {attrs}>')
        parts.append(self._head_scripts)
        return "\n".join(parts)

    def theme_config(self) -> dict[str, Any]:
        """Return theme configuration for rendering (CSS links, variables, etc.)."""
        t = get_theme(self.theme)
        if t is None:
            return {}
        return {
            "name": t.name,
            "framework": t.framework,
            "cdn_css": t.cdn_url,
            "js_url": t.js_url,
            "variables": dict(t.variables),
            "extra_classes": list(t.extra_classes),
            "tailwind_config": t.tailwind_config or {},
        }

    # -- plugins ---------------------------------------------------------------
    def use(self, plugin: Plugin) -> "MikiApp":
        missing = [d for d in plugin.depends_on if not any(p.name == d for p in self.plugins)]
        if missing:
            raise RuntimeError(
                f"Plugin {plugin.name!r} depends on {missing!r}, "
                "but those plugins are not registered yet. "
                "Register dependencies before registering this plugin."
            )
        self.plugins.append(plugin)
        plugin.register(self)
        return self

    # -- invocation ------------------------------------------------------------
    async def invoke(self, route: RouteDef, request: Any = None, path_params: dict[str, Any] | None = None) -> tuple[list[Any], Any]:
        """Call a route handler and return ``(normalized_nodes, ctx)``.

        The returned ``ctx`` (which may be ``None``) carries ``ctx.meta`` so the
        server can resolve the per-page title via :func:`resolve_title`.

        Parameters
        ----------
        route:
            The :class:`RouteDef` to invoke.
        request:
            The raw ASGI request (may be ``None`` in tests).
        path_params:
            Path parameters extracted from the URL (e.g. ``{"user_id": "42"}``).
        """
        result, ctx = invoke_route(route, self, request, path_params)
        if hasattr(result, "__await__"):
            result = await result
        tree = normalize(result)
        for plugin in self.plugins:
            try:
                tree = plugin.on_render(tree)
            except Exception:
                logger.exception("Plugin %r on_render failed; skipping.", plugin.name)
        return tree, ctx

    def url_for(self, name: str, **path_params: Any) -> str:
        """Reverse-resolve a registered route name to its URL path.

        Parameters
        ----------
        name:
            The route name (defaults to the handler function name).
        **path_params:
            Path parameter values to fill ``{param}`` placeholders.

        Returns
        -------
        str
            The resolved URL path (e.g. ``/users/42``).

        Raises
        ------
        ValueError
            If the route name is not found or required path params are missing.
        """
        route = next((r for r in self.routes.values() if r.name == name), None)
        if route is None:
            raise ValueError(f"No route named {name!r}. Available: {[r.name for r in self.routes.values()]}")
        path = route.path
        for param in route.path_params:
            if param not in path_params:
                raise ValueError(
                    f"Route {name!r} requires path parameter {param!r}. "
                    f"Provided: {list(path_params)}"
                )
            path = path.replace("{" + param + "}", str(path_params[param]))
        return path

    def get_route(self, path: str) -> RouteDef | None:
        return self.routes.get(path)

    # -- convenience ------------------------------------------------------------
    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        *,
        desktop: bool = False,
        browser: bool = False,
        **kwargs: Any,
    ) -> None:
        """Run the app.

        ``python app.py`` (with ``if __name__ == "__main__": app.run()`` at the
        bottom) is the most beginner-friendly way to start a MikiUI app.

        Parameters
        ----------
        host, port:
            Where to bind the server.
        desktop:
            If ``True``, launch in a native pywebview window (``mikiui desktop``).
        browser:
            If ``True`` and ``desktop`` is ``True``, force the system browser
            instead of pywebview.
        reload:
            Enable auto-reload (only for non-desktop mode).
        """
        if desktop:
            from ..build import run_desktop

            run_desktop(
                self,
                host=host,
                port=port,
                native=not browser,
                **kwargs,
            )
        else:
            import uvicorn

            from ..backend import create_app

            reload = kwargs.pop("reload", False)
            fastapi_app = create_app(self)
            uvicorn.run(fastapi_app, host=host, port=port, reload=reload)
