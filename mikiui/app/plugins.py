"""Plugin base class for MikiUI.

Plugins are registered via ``app.use(plugin)``.  A plugin can:

* **Register theme** — override or add a theme via :meth:`ThemePlugin.register_theme`.
* **Register components / widgets** — add custom component or widget classes
  that become importable via ``app.components`` / ``app.widgets``.
* **Add routes** — register new routes on the :class:`~mikiui.app.MikiApp`.
* **Transform output** — :meth:`on_render` post-processes a route's component
  tree before it is sent to the client (e.g. wrapping in a layout, injecting
  scripts, or applying global styles).

Security-first: plugins run inside the app process, so only trusted, validated
plugins should be installed.  See ``context/PRD.md`` for sandboxing guidance.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from ..themes import Theme

logger = logging.getLogger(__name__)


class Plugin:
    """Base class for MikiUI plugins.

    Override any of the following hooks:

    * :meth:`register` — called once when ``app.use(plugin)`` is invoked.
    * :meth:`on_render` — called for every rendered route; can mutate the
      component tree.
    * :meth:`on_request` — called with each incoming request (for analytics,
      auth, etc.).
    * :meth:`on_route_add` — called when a route is registered via
      ``app.route`` / ``app.get`` / ``app.post``.  Receives the path, method,
      and handler.  Used by :class:`~mikiui_app_plugins.api.APIPlugin` to
      collect ``/api/`` routes.

    Lifecycle hooks are called in insertion order.  Plugins can declare
    ``depends_on`` to control ordering: a plugin's ``depends_on`` list names
    other plugins that must run before it.  Missing dependencies raise
    ``RuntimeError`` at registration time.
    """

    name: str = "plugin"
    depends_on: list[str] = []

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
        from ..themes import register_theme as _register, get_theme

        existing = get_theme(t.name)
        if existing and existing.source != "builtin-color":
            raise ValueError(
                f"Theme {t.name!r} is already registered by {existing.source!r}. "
                "Use a different theme name."
            )
        _register(t)
        app.theme = t.name


class ComponentPlugin(Plugin):
    """Plugin that registers custom component or widget classes.

    Override :meth:`components` to return a dict mapping names to classes.
    They become accessible as ``app.components["MyWidget"]``.
    """

    name: str = "component"

    def components(self) -> dict[str, type]:
        """Return ``{name: ComponentClass}``. Override me."""
        return {}

    def register(self, app: Any) -> None:
        comps = self.components()
        if not hasattr(app, "_component_registry"):
            app._component_registry = {}
        for name, cls in comps.items():
            if name in app._component_registry:
                logger.warning("Component %r already registered; overwriting.", name)
            app._component_registry[name] = cls


class WidgetPlugin(Plugin):
    """Plugin that registers custom widget classes.

    Override :meth:`widgets` to return a dict mapping names to classes.
    They become accessible as ``app.widgets["MyCustomWidget"]``.
    """

    name: str = "widget"

    def widgets(self) -> dict[str, type]:
        """Return ``{name: WidgetClass}``. Override me."""
        return {}

    def register(self, app: Any) -> None:
        widgets = self.widgets()
        if not hasattr(app, "_widget_registry"):
            app._widget_registry = {}
        for name, cls in widgets.items():
            if name in app._widget_registry:
                logger.warning("Widget %r already registered; overwriting.", name)
            app._widget_registry[name] = cls


__all__ = ["Plugin", "ThemePlugin", "ComponentPlugin", "WidgetPlugin"]
