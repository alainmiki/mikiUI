"""The user-facing MikiUI application.

`MikiApp` owns routes, shared server-side ``state``, and plugins. Route
handlers return component trees (or strings/lists). They may optionally accept
a :class:`Ctx` (from `mikiui.app.routes`) as their first parameter to access
the request and shared state.
"""

from __future__ import annotations

import html as _html
import logging
import os
import re as _re
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ..app.plugin_security import PluginSecurityConfig, PluginValidator
from ..app.static_assets import register_plugin_assets
from ..engine.dom import normalize
from ..router.group import RouteGroup, RouteGroupBuilder

if TYPE_CHECKING:
    from ..router.router import Router
from ..themes import Theme
from .plugins import Plugin
from .routes import RouteDef, invoke_route, match_route
from .state import AppState
from .theme_registry import ThemeRegistry
from .widget_registry import WidgetRegistry

logger = logging.getLogger(__name__)


def _esc(value: Any) -> str:
    """Escape a value for safe insertion into an HTML attribute or text node."""
    return _html.escape(str(value), quote=True)


def _resolve_app_spec(miki_app: Any) -> str:
    """Best-effort reverse lookup of ``module:attr`` for a live ``MikiApp``.

    uvicorn's ``reload`` mode requires the application to be passed as an
    import string, so when ``app.run(reload=True)`` is used we have to figure
    out the user's ``module:attr`` to hand to uvicorn.

    Falls back to ``__main__:app`` which is what ``python app.py`` runs.
    """
    import sys

    target_id = id(miki_app)
    for mod_name, mod in list(sys.modules.items()):
        if mod is None or not hasattr(mod, "__dict__"):
            continue
        for attr_name, attr in list(vars(mod).items()):
            if attr is miki_app or (id(attr) == target_id and attr is miki_app):
                if mod_name == "__main__":
                    return f"__main__:{attr_name}"
                if mod_name.startswith("__"):
                    continue
                return f"{mod_name}:{attr_name}"
    return "__main__:app"


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
        self.style_framework: str = "plain"
        self.style_mode: str = "cdn"
        self.style_daisyui: bool = False
        self.favicon: str | None = favicon or "/_miki/runtime/mikiui-icon.png"
        self.desktop_icon: str | None = desktop_icon
        self.splash_screen: str | None = splash_screen
        self.palette_color: str = "#0f172a"
        self._head_meta: list[dict[str, str]] = []
        self._head_links: list[dict[str, str]] = []
        self._head_scripts: str = ""
        self._not_found_handler: Callable | None = None
        self._error_pages: dict[int, Callable] = {}
        self._static_mounts: list[tuple[str, str]] = []

        # New registries
        self.registry: WidgetRegistry = WidgetRegistry()
        # ThemeRegistry should consult the global theme registry as a parent
        from ..themes import get_theme, list_themes

        class _GlobalThemeProxy:
            def get(self, name: str) -> Theme | None:
                return get_theme(name)

            def list_all(self) -> list[str]:
                return list_themes()

        self.theme_registry: ThemeRegistry = ThemeRegistry(parent_registry=_GlobalThemeProxy())  # type: ignore[arg-type]
        self._backend_routes: list[dict[str, Any]] = []
        self._websocket_routes: list[dict[str, Any]] = []
        self._middleware_classes: list[type] = []
        self._route_groups: dict[str, RouteGroup] = {}
        self._auth_strategies: dict[str, Any] = {}

        # Plugin security policy
        self._plugin_security_config: PluginSecurityConfig = PluginSecurityConfig()
        self._plugin_validator: PluginValidator = PluginValidator(self._plugin_security_config)

        # Initialize theme registry with builtin themes
        from ..themes import get_theme as _get_theme
        from ..themes import list_themes as _list_themes

        for theme_name in _list_themes():
            theme = _get_theme(theme_name)
            if theme:
                self.theme_registry.register(theme, override=True)

    # -- routing ---------------------------------------------------------------
    def _normalize_path(self, path: str) -> str:
        """Normalize a route path by stripping trailing slashes (except root)."""
        if path != "/" and path.endswith("/"):
            return path.rstrip("/")
        return path

    def route(
        self,
        path: str,
        methods: tuple[str, ...] = ("GET",),
        name: str | None = None,
        title: str | None = None,
        requires_auth: bool = False,
        auth: Any | None = None,
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
            Route name (defaults to the handler function name). Must be unique.
        title:
            Per-page ``<title>`` tag content.
        requires_auth:
            If ``True``, require a valid session token when the APIPlugin is
            active.
        """
        path = self._normalize_path(path)
        def decorator(fn: Callable) -> Callable:
            upper_methods = tuple(m.upper() for m in methods)
            resolved_name = name or getattr(fn, "__name__", "route")
            existing = next(
                (r for r in self.routes.values() if r.name == resolved_name), None
            )
            if existing is not None:
                raise ValueError(
                    f"Route name {resolved_name!r} is already used by {existing.path!r}. "
                    "Pass a unique `name=` to the decorator."
                )
            if path in self.routes:
                existing_route = self.routes[path]
                # Check for overlapping methods (same path + same method = error)
                overlap = set(existing_route.methods) & set(upper_methods)
                if overlap:
                    raise ValueError(
                        f"Route {path!r} with method(s) {sorted(overlap)} is already "
                        f"registered by {existing_route.name!r}. Use a different path "
                        "or remove the existing route first."
                    )
                # Merge methods for the same path (e.g., GET /users/{id} + POST /users/{id})
                merged_methods = tuple(sorted(set(existing_route.methods + upper_methods)))
                self.routes[path] = RouteDef(
                    path, fn, merged_methods, resolved_name, title,
                    requires_auth or existing_route.requires_auth,
                    auth=auth if auth is not None else existing_route._auth_requirement,
                )
                # Preserve route group from existing registration
                if existing_route._route_group is not None:
                    self.routes[path]._route_group = existing_route._route_group
            else:
                self.routes[path] = RouteDef(
                    path, fn, upper_methods, resolved_name, title, requires_auth, auth=auth
                )
            for plugin in self.plugins:
                if hasattr(plugin, "on_route_add"):
                    plugin.on_route_add(path, upper_methods, fn)
            return fn

        return decorator

    def not_found(self, handler: Callable) -> Callable:
        """Register a custom 404 handler.

        The handler may accept ``ctx`` as its first parameter and should
        return a component tree. If not set, MikiUI returns a standard
        ``NotFoundError`` response.

        Example::

            @app.not_found
            def not_found(ctx):
                return Div("This page does not exist.")
        """
        self._not_found_handler = handler
        return handler

    def set_error_page(self, status_code: int, handler: Callable) -> MikiApp:
        """Register a custom error page for *status_code*.

        Example::

            app.set_error_page(403, lambda ctx: Div("Access denied"))
        """
        self._error_pages[status_code] = handler
        return self

    def mount(self, router: Router, *, prefix: str | None = None) -> MikiApp:
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

    def mount_static(self, url_path: str, directory: str, *, name: str | None = None) -> MikiApp:
        """Mount an arbitrary directory for static file serving.

        The directory is served under *url_path* when the app is built or run.
        This is the beginner-friendly alternative to dropping down to raw
        FastAPI ``app.mount()`` after ``create_app()``.

        Parameters
        ----------
        url_path:
            URL prefix (e.g. ``"/static"`` or ``"/media"``).
        directory:
            Absolute or relative path to the directory to serve.
        name:
            Optional mount name.  Auto-generated from *url_path* if omitted.

        Example
        -------
        >>> app.mount_static("/uploads", "./uploads")
        >>> app.add_head_link("/uploads/logo.png", rel="icon")
        """
        abs_path = os.path.abspath(directory)
        if not os.path.isdir(abs_path):
            raise NotADirectoryError(
                f"Cannot mount static directory: {abs_path!r} does not exist or is not a directory."
            )
        self._static_mounts.append((url_path.rstrip("/"), abs_path))
        return self

    def asset_url(
        self,
        package_type: str,
        package_name: str,
        filename: str,
    ) -> str:
        """Build the URL for a static asset served by the framework.

        Parameters
        ----------
        package_type:
            One of ``"components"``, ``"widgets"``, ``"plugins"``, or ``"themes"``.
        package_name:
            The package or plugin name (e.g. ``"splitview"``).
        filename:
            The asset filename (e.g. ``"splitview.css"``).

        Returns
        -------
        str
            URL path to the asset, e.g.
            ``/_miki/components/splitview/static/splitview.css``.

        Example
        -------
        >>> app.asset_url("components", "splitview", "splitview.css")
        '/_miki/components/splitview/static/splitview.css'
        """
        from ..app.static_assets import get_asset_url

        return get_asset_url(package_type, package_name, filename)

    def route_group(self, prefix: str) -> RouteGroupBuilder:
        """Create a route group with shared prefix, auth, and middleware.

        Example::

            api = app.route_group("/api")
            api.rate_limit(limit=200, window=60)
            api.auth(AuthRequirement(strategy="jwt", scopes=["admin"]))

            @api.get("/users")
            def list_users(ctx):
                return Div("users")
        """
        return RouteGroupBuilder(self, prefix)

    def register_auth_strategy(self, name: str, strategy: Any) -> MikiApp:
        """Register an auth strategy callable.

        The strategy must implement ``validate(request) -> user | None``.
        Built-in strategies: ``"session"`` (from SessionPlugin), ``"jwt"``.
        """
        self._auth_strategies[name] = strategy
        return self

    def get_auth_strategy(self, name: str) -> Any | None:
        """Return a registered auth strategy by name."""
        return self._auth_strategies.get(name)

    def get(self, path: str, name: str | None = None, title: str | None = None, auth: Any | None = None):
        return self.route(path, ("GET",), name, title, auth=auth)

    def post(self, path: str, name: str | None = None, title: str | None = None, auth: Any | None = None):
        return self.route(path, ("POST",), name, title, auth=auth)

    def put(self, path: str, name: str | None = None, title: str | None = None, auth: Any | None = None):
        return self.route(path, ("PUT",), name, title, auth=auth)

    def patch(self, path: str, name: str | None = None, title: str | None = None, auth: Any | None = None):
        return self.route(path, ("PATCH",), name, title, auth=auth)

    def delete(self, path: str, name: str | None = None, title: str | None = None, auth: Any | None = None):
        return self.route(path, ("DELETE",), name, title, auth=auth)

    def head(self, path: str, name: str | None = None, title: str | None = None, auth: Any | None = None):
        return self.route(path, ("HEAD",), name, title, auth=auth)

    def options(self, path: str, name: str | None = None, title: str | None = None, auth: Any | None = None):
        return self.route(path, ("OPTIONS",), name, title, auth=auth)

    # -- themes ---------------------------------------------------------------
    def set_theme(self, name: str) -> MikiApp:
        """Activate a registered theme by name."""
        if name not in self.theme_registry.list_all():
            available = ", ".join(self.theme_registry.list_all())
            raise ValueError(f"Unknown theme: {name!r}. Available: {available}")
        self.theme = name
        self.theme_registry.set_active(name)
        return self

    def set_style_framework(
        self,
        framework: str,
        mode: str = "cdn",
        daisyui: bool = False,
    ) -> MikiApp:
        """Set the CSS styling framework.

        Parameters
        ----------
        framework:
            One of ``"plain"`` or ``"tailwind"``.
        mode:
            Tailwind only. One of ``"cdn"`` (use public CDN) or ``"local"``
            (serve a locally built CSS file from ``_miki/runtime/themes/``).
        daisyui:
            Tailwind only. Enable DaisyUI component classes.
        """
        framework = framework.lower().strip()
        if framework not in ("plain", "tailwind"):
            raise ValueError(
                f"Unknown style framework {framework!r}. Choose from: plain, tailwind"
            )
        if framework == "plain":
            self.style_framework = "plain"
            self.style_mode = "cdn"
            self.style_daisyui = False
            return self

        self.style_framework = "tailwind"
        self.style_mode = "cdn" if mode == "cdn" else "local"
        self.style_daisyui = bool(daisyui)
        return self

    def set_favicon(
        self,
        favicon: str,
        sizes: tuple[int, int] | None = None,
        theme_color: str = "#0f172a",
    ) -> MikiApp:
        """Set or change the favicon at runtime."""
        self.favicon = favicon
        self.palette_color = theme_color
        return self

    def register_theme(self, theme: Theme) -> MikiApp:
        """Register a custom or plugin theme and activate it."""
        # Register locally and propagate to the global registry so renderer
        # and other tooling can discover the theme.
        try:
            self.theme_registry.register(theme, propagate_global=True)
        except TypeError:
            # Older register API: fall back to simple register and call global helper
            self.theme_registry.register(theme)
            try:
                from ..themes import register_theme as _global_register

                _global_register(theme)
            except Exception:
                pass
        self.theme = theme.name
        return self

    def set_head_meta(self, name: str, content: str, **extra: Any) -> MikiApp:
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

    def add_head_link(self, href: str, rel: str = "stylesheet", **attrs: Any) -> MikiApp:
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
        >>> app.add_head_link("/static/custom.css", rel="stylesheet")
        >>> app.add_head_link("/static/app.js", rel="modulepreload")
        """
        tag = {"href": href, "rel": rel}
        tag.update(attrs)
        self._head_links.append(tag)
        return self

    def add_head_script(self, src: str, **attrs: Any) -> MikiApp:
        """Add a ``<script>`` tag to the page head.

        Parameters
        ----------
        src :
            URL or path to the JavaScript file.
        **attrs : Additional HTML attributes (e.g. type="module", defer=True).

        Example
        -------
        >>> app.add_head_script("/static/app.js")
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
        t = self.theme_registry.get_active()
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
    def use(self, plugin: Plugin, config: dict[str, Any] | None = None) -> MikiApp:
        """Register a plugin.

        Parameters
        ----------
        plugin:
            The plugin instance to register.
        config:
            Optional configuration dict passed to ``plugin.configure()``.
        """
        missing = [
            d
            for d in getattr(plugin, "depends_on", [])
            if not any(p.name == d for p in self.plugins)
        ]
        if missing:
            raise RuntimeError(
                f"Plugin {plugin.name!r} depends on {missing!r}, "
                "but those plugins are not registered yet. "
                "Register dependencies before registering this plugin."
            )
        # Security-first: validate the plugin before it touches the app.
        self._plugin_validator.validate_plugin(
            plugin,
            manifest=getattr(plugin, "manifest", None),
            source_code=self._resolve_plugin_source(plugin),
        )
        if config:
            plugin.configure(config)
        self.plugins.append(plugin)
        if hasattr(plugin, "register"):
            plugin.register(self)
        # Collect backend routes and middleware from plugins
        if hasattr(plugin, "backend_routes"):
            self._backend_routes.extend(plugin.backend_routes())
        if hasattr(plugin, "websocket_routes"):
            self._websocket_routes.extend(plugin.websocket_routes())
        if hasattr(plugin, "middleware_classes"):
            self._middleware_classes.extend(plugin.middleware_classes())
        # Register plugin static assets for server mounting
        if hasattr(plugin, "assets"):
            try:
                paths = plugin.assets()
                if paths:
                    register_plugin_assets(plugin.name, paths)
            except Exception:
                logger.exception("Plugin %r assets() failed; skipping.", plugin.name)
        return self

    def _resolve_plugin_source(self, plugin: Plugin) -> str | None:
        """Try to read the plugin's source code for AST vetting."""
        module = getattr(plugin, "__module__", None)
        if not module:
            return None
        module_path = module.replace(".", os.sep) + ".py"
        candidates = [
            module_path,
            os.path.join("mikiui_app_plugins", module_path),
        ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                try:
                    with open(candidate, encoding="utf-8") as fh:
                        return fh.read()
                except OSError:
                    continue
        return None

    def set_plugin_security_config(self, config: PluginSecurityConfig) -> MikiApp:
        """Replace the app's plugin security policy.

        Example::

            app.set_plugin_security_config(
                PluginSecurityConfig(
                    allow_untrusted=False,
                    vet_ast=True,
                    blocked_capabilities=["filesystem:write"],
                )
            )
        """
        self._plugin_security_config = config
        self._plugin_validator = PluginValidator(config)
        return self

    def get_plugin_security_config(self) -> PluginSecurityConfig:
        """Return the current plugin security policy."""
        return self._plugin_security_config

    # -- backend integration ---------------------------------------------------
    def get_backend_routes(self) -> list[dict[str, Any]]:
        """Return all backend route definitions from plugins.

        Routes are collected once at :meth:`use` time and cached in
        ``self._backend_routes``.  Plugins that need to add routes after
        registration should append to that list directly rather than
        returning them from :meth:`Plugin.backend_routes`.
        """
        return list(self._backend_routes)

    def get_websocket_routes(self) -> list[dict[str, Any]]:
        """Return all WebSocket route definitions from plugins.

        Routes are collected once at :meth:`use` time and cached in
        ``self._websocket_routes``.  Plugins that need to add WebSocket
        routes after registration should append to that list directly rather
        than returning them from :meth:`Plugin.websocket_routes`.
        """
        return list(self._websocket_routes)

    def get_middleware_classes(self) -> list[type]:
        """Return all middleware classes from plugins.

        Middleware classes are cached at :meth:`use` time (see
        ``self._middleware_classes``).  Plugins that register middleware
        after being loaded should append to that list directly.
        """
        return list(self._middleware_classes)

    def get_route_group_rate_limits(self) -> list[tuple[str, int, int]]:
        """Return rate-limit configs from all route groups.

        Returns a list of ``(path_prefix, limit, window)`` tuples.
        """
        configs: list[tuple[str, int, int]] = []
        for group in self._route_groups.values():
            if group._rate_limit is not None:
                configs.append((
                    group.prefix,
                    group._rate_limit.limit,
                    group._rate_limit.window,
                ))
        return configs

    def get_plugin_assets(self) -> list[str]:
        """Return all static assets from plugins.

        Assets are collected once at :meth:`use` time via
        :func:`register_plugin_assets`.  This method returns the deduplicated
        mount list from the static-assets registry for backward compatibility.
        """
        from ..app.static_assets import get_asset_mounts

        return list(get_asset_mounts().values())

    # -- invocation ------------------------------------------------------------
    async def invoke(
        self,
        route: RouteDef,
        request: Any = None,
        path_params: dict[str, Any] | None = None,
    ) -> tuple[list[Any], Any]:
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
        try:
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
        except Exception as error:
            for plugin in self.plugins:
                try:
                    plugin.on_error(error, request)
                except Exception:
                    logger.exception("Plugin %r on_error failed.", plugin.name)
            raise

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
        for param in route.path_param_names:
            if param not in path_params:
                raise ValueError(
                    f"Route {name!r} requires path parameter {param!r}. "
                    f"Provided: {list(path_params)}"
                )
            # Replace both {param} and {param:type} forms
            path = _re.sub(r"\{" + _re.escape(param) + r"(?::\w+)?\}", str(path_params[param]), path)
        return path

    def get_route(self, path: str) -> RouteDef | None:
        """Look up a route by exact path or by pattern match.

        First tries an exact match, then falls back to matching against
        registered route patterns (e.g. ``/users/42`` matches
        ``/users/{user_id}``).
        """
        path = self._normalize_path(path)
        # Exact match first
        if path in self.routes:
            return self.routes[path]
        # Pattern match against parameterized routes
        return match_route(path, list(self.routes.values()))

    # -- testing ---------------------------------------------------------------
    def test_client(self, **kwargs: Any) -> Any:
        """Return a Starlette ``TestClient`` for this app.

        Convenience wrapper around ``create_app`` + ``TestClient``::

            client = app.test_client()
            resp = client.get("/")
            assert resp.status_code == 200

        Parameters
        ----------
        **kwargs:
            Forwarded to :func:`mikiui.backend.create_app`.
        """
        from starlette.testclient import TestClient

        from ..backend import create_app
        return TestClient(create_app(self, **kwargs))

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
            return

        import uvicorn

        from ..backend import create_app

        reload = kwargs.pop("reload", False)
        if reload:
            import os

            spec = _resolve_app_spec(self)
            os.environ["MIKIUI_APP_SPEC"] = spec
            uvicorn.run(
                "mikiui.cli._dev_support:app_factory",
                host=host,
                port=port,
                reload=True,
                factory=True,
            )
            return

        fastapi_app = create_app(self)
        uvicorn.run(fastapi_app, host=host, port=port)

    def shutdown(self) -> None:
        """Shut down the app, calling plugin shutdown hooks."""
        for plugin in reversed(self.plugins):
            try:
                plugin.on_shutdown()
            except Exception:
                logger.exception("Plugin %r on_shutdown failed.", plugin.name)


__all__ = ["MikiApp"]
