"""Plugin base class for MikiUI.

Plugins are registered via ``app.use(plugin)``.  A plugin can:

* **Register theme** — override or add a theme via :meth:`ThemePlugin.register_theme`.
* **Register components / widgets** — add custom component or widget classes
  that become importable via ``app.components`` / ``app.widgets``.
* **Add routes** — register new routes on the :class:`~mikiui.app.MikiApp`.
* **Transform output** — :meth:`on_render` post-processes a route's component
  tree before it is sent to the client (e.g. wrapping in a layout, injecting
  scripts, or applying global styles).
* **Extend backend** — return FastAPI route definitions via :meth:`backend_routes`,
  middleware classes via :meth:`middleware_classes`, and static assets via :meth:`assets`.
* **Handle errors** — :meth:`on_error` is called when a route handler raises.

Security-first: plugins run inside the app process, so only trusted, validated
plugins should be installed.  See ``context/PRD.md`` for sandboxing guidance.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ..themes import Theme

if TYPE_CHECKING:
    from ..app.plugin_security import PluginManifest

logger = logging.getLogger(__name__)


class Plugin:
    """Base class for MikiUI plugins.

    Override any of the following hooks:

    * :meth:`register` — called once when ``app.use(plugin)`` is invoked.
    * :meth:`configure` — called with plugin configuration dict before register.
    * :meth:`on_render` — called for every rendered route; can mutate the
      component tree.
    * :meth:`on_request` — called with each incoming request (for analytics,
      auth, etc.).
    * :meth:`on_route_add` — called when a route is registered via
      ``app.route`` / ``app.get`` / ``app.post``.
    * :meth:`on_error` — called when a route handler raises an exception.
    * :meth:`on_shutdown` — called when the app is shutting down.

    Lifecycle hooks are called in insertion order.  Plugins can declare
    ``depends_on`` to control ordering: a plugin's ``depends_on`` list names
    other plugins that must run before it.  Missing dependencies raise
    ``RuntimeError`` at registration time.

    Security attributes:

    * :attr:`capabilities` — list of capability tokens this plugin requires
      (e.g. ``["filesystem:read", "network:outbound"]``).  The framework
      checks these against the app's security policy before registration.
    * :attr:`manifest` — optional :class:`~mikiui.app.plugin_security.PluginManifest`
      describing the plugin.  When absent the framework builds one from
      module attributes.
    """

    name: str = "plugin"
    depends_on: list[str] = []
    _config: dict[str, Any] | None = None
    capabilities: list[str] = []
    manifest: PluginManifest | None = None

    def configure(self, config: dict[str, Any]) -> None:
        """Optional configuration hook.

        Called before :meth:`register` with a dict of configuration values.

        Parameters
        ----------
        config:
            Configuration key-value pairs.
        """
        self._config = config

    def register(self, app: Any) -> None:
        """Called by ``app.use``. Override to extend the app (routes, themes, etc.)."""

    def on_render(self, tree: Any) -> Any:
        """Optional post-processing of a route's returned component tree."""
        return tree

    def on_request(self, request: Any) -> None:
        """Optional hook invoked for every incoming request."""

    def on_route_add(self, path: str, methods: tuple[str, ...], handler: Any) -> None:
        """Optional hook called when a route is registered.

        Parameters
        ----------
        path:
            The full URL path (including any router prefix).
        methods:
            Tuple of HTTP methods for this route.
        handler:
            The raw handler function.
        """

    def on_error(self, error: Exception, request: Any) -> None:
        """Optional hook called when a route handler raises an exception.

        Parameters
        ----------
        error:
            The exception that was raised.
        request:
            The incoming request (may be ``None`` in tests).
        """

    def on_shutdown(self) -> None:
        """Optional hook called when the app is shutting down."""

    def assets(self) -> list[str]:
        """Optional: return list of asset paths to bundle with the app.

        Returns
        -------
        list[str]
            Paths to static assets (CSS, JS, images) that should be
            included in the build.
        """
        return []

    def backend_routes(self) -> list[dict[str, Any]]:
        """Optional: return FastAPI HTTP route definitions to mount.

        Returns
        -------
        list[dict[str, Any]]
            Route definitions with keys: ``path``, ``methods``, ``endpoint``,
            and optional ``include_in_schema``, ``name``, ``tags``.
        """
        return []

    def websocket_routes(self) -> list[dict[str, Any]]:
        """Optional: return WebSocket route definitions to mount.

        Returns
        -------
        list[dict[str, Any]]
            Route definitions with keys: ``path``, ``handler``,
            and optional ``include_in_schema``, ``name``, ``tags``,
            ``manager`` (a ``ConnectionManager`` instance), and
            ``max_message_size``.
        """
        return []

    def middleware_classes(self) -> list[type]:
        """Optional: return list of FastAPI/Starlette middleware classes.

        Returns
        -------
        list[type]
            Middleware classes to add to the app.
        """
        return []


class ThemePlugin(Plugin):
    """Plugin that registers a theme with the app.

    Usage::

        from mikiui import register_theme, Theme

        class MyTheme(ThemePlugin):
            def theme(self) -> Theme:
                return Theme(
                    name="my-theme",
                    css_path="/path/to/my.css",
                    extra_classes=["data-theme-my"],
                )

        app.use(MyTheme())
    """

    name: str = "theme"

    def theme(self) -> Theme:
        """Return the :class:`~mikiui.themes.Theme` to register. Override me."""
        raise NotImplementedError

    def register(self, app: Any) -> None:
        t = self.theme()
        registry = getattr(app, "theme_registry", None)
        if registry is not None:
            # Prefer propagating to the global registry so get_theme() can find it.
            try:
                registry.register(t, propagate_global=True)
            except TypeError:
                # Older ThemeRegistry may not accept propagate_global.
                registry.register(t)
        else:
            from ..themes import get_theme
            from ..themes import register_theme as _register

            existing = get_theme(t.name)
            if existing and existing.source != "builtin-color":
                raise ValueError(
                    f"Theme {t.name!r} is already registered by {existing.source!r}. "
                    "Use a different theme name."
                )
            _register(t)
        if hasattr(app, "set_theme"):
            try:
                app.set_theme(t.name)
            except ValueError:
                pass


class ComponentPlugin(Plugin):
    """Plugin that registers custom component or widget classes.

    Override :meth:`components` to return a dict mapping names to classes.
    They become accessible via ``app.registry``.
    """

    name: str = "component"

    def components(self) -> dict[str, type]:
        """Return ``{name: ComponentClass}``. Override me."""
        return {}

    def register(self, app: Any) -> None:
        comps = self.components()
        registry = getattr(app, "registry", None)
        if registry is not None:
            for name, cls in comps.items():
                registry.register(name, cls, namespace=self.name)
        # Backward compatibility: maintain _component_registry
        if not hasattr(app, "_component_registry"):
            app._component_registry = {}
        for name, cls in comps.items():
            if name in app._component_registry:
                logger.warning("Component %r already registered; overwriting.", name)
            app._component_registry[name] = cls


class WidgetPlugin(Plugin):
    """Plugin that registers custom widget classes.

    Override :meth:`widgets` to return a dict mapping names to classes.
    They become accessible via ``app.registry``.
    """

    name: str = "widget"

    def widgets(self) -> dict[str, type]:
        """Return ``{name: WidgetClass}``. Override me."""
        return {}

    def register(self, app: Any) -> None:
        widgets = self.widgets()
        registry = getattr(app, "registry", None)
        if registry is not None:
            for name, cls in widgets.items():
                registry.register(name, cls, namespace=self.name)
        # Backward compatibility: maintain _widget_registry
        if not hasattr(app, "_widget_registry"):
            app._widget_registry = {}
        for name, cls in widgets.items():
            if name in app._widget_registry:
                logger.warning("Widget %r already registered; overwriting.", name)
            app._widget_registry[name] = cls


__all__ = ["Plugin", "ThemePlugin", "ComponentPlugin", "WidgetPlugin"]
