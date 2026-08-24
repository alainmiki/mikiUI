"""Central registry for widgets and components.

Provides namespaced registration, lifecycle hooks, and lookup for
widgets and components registered by plugins or the app itself.

Usage:
    from mikiui.app.widget_registry import WidgetRegistry

    registry = WidgetRegistry()
    registry.register("MyWidget", MyWidgetClass)
    registry.register("other_plugin:SpecialWidget", SpecialWidgetClass)

    cls = registry.get("MyWidget")
    widget = registry.create("MyWidget", *args, **kwargs)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class WidgetRegistry:
    """Central registry for components and widgets with namespacing support.

    Supports namespacing via ``plugin_name:widget_name`` to avoid collisions
    between plugins.

    Attributes:
        _registry: Internal dict mapping names to widget/component classes.
        _lifecycle_hooks: Lifecycle hooks registered by name.
        _instances: Weak references to created instances for lifecycle tracking.
    """

    def __init__(self) -> None:
        self._registry: dict[str, type] = {}
        self._lifecycle_hooks: dict[str, dict[str, list[Callable[..., Any]]]] = {}
        self._instances: dict[str, list[Any]] = {}

    def register(self, name: str, cls: type, *, namespace: str | None = None) -> None:
        """Register a widget or component class.

        Parameters
        ----------
        name:
            Widget/component name. Can include namespace prefix
            (e.g. ``"plugin_name:widget_name"``).
        cls:
            The class to register.
        namespace:
            Optional namespace. If provided, the name is stored as
            ``"{namespace}:{name}"``.
        """
        if namespace:
            full_name = f"{namespace}:{name}"
        elif ":" in name:
            full_name = name
        else:
            full_name = name

        if full_name in self._registry:
            logger.warning(
                "Widget/component %r already registered; overwriting.", full_name
            )
        self._registry[full_name] = cls
        logger.debug("Registered widget/component: %s -> %s", full_name, cls.__name__)

    def unregister(self, name: str) -> None:
        """Remove a widget or component from the registry."""
        if name in self._registry:
            del self._registry[name]
            logger.debug("Unregistered widget/component: %s", name)

    def get(self, name: str) -> type | None:
        """Look up a registered class by name.

        Supports both namespaced (``"ns:name"``) and unqualified (``"name"``)
        lookups. Unqualified lookups return the first match.
        """
        if name in self._registry:
            return self._registry[name]
        # Try unqualified match
        matches = [cls for n, cls in self._registry.items() if n.split(":")[-1] == name]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            logger.warning(
                "Ambiguous lookup for %r; found %d matches.", name, len(matches)
            )
        return None

    def create(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Instantiate a registered class.

        Parameters
        ----------
        name:
            The registered name (namespaced or unqualified).
        *args, **kwargs:
            Passed to the class constructor.

        Returns
        -------
        Any
            The instantiated widget/component.
        """
        cls = self.get(name)
        if cls is None:
            raise KeyError(f"No widget/component registered as {name!r}")
        instance = cls(*args, **kwargs)
        self._instances.setdefault(name, []).append(instance)
        self._fire_hook("on_create", name, instance)
        return instance

    def on_create(self, name: str, hook: Callable[..., Any]) -> None:
        """Register a callback invoked when a widget/component is created.

        Parameters
        ----------
        name:
            The widget/component name (namespaced or unqualified).
        hook:
            Callable receiving the created instance.
        """
        self._lifecycle_hooks.setdefault(name, {}).setdefault(
            "on_create", []
        ).append(hook)

    def on_destroy(self, name: str, hook: Callable[..., Any]) -> None:
        """Register a callback invoked when a widget/component is destroyed.

        Parameters
        ----------
        name:
            The widget/component name.
        hook:
            Callable receiving the destroyed instance.
        """
        self._lifecycle_hooks.setdefault(name, {}).setdefault(
            "on_destroy", []
        ).append(hook)

    def on_update(self, name: str, hook: Callable[..., Any]) -> None:
        """Register a callback invoked when a widget/component is updated.

        Parameters
        ----------
        name:
            The widget/component name.
        hook:
            Callable receiving the updated instance and any update data.
        """
        self._lifecycle_hooks.setdefault(name, {}).setdefault(
            "on_update", []
        ).append(hook)

    def destroy(self, name: str, instance: Any) -> None:
        """Explicitly destroy a widget/component instance.

        Fires ``on_destroy`` hooks and removes from tracking.

        Parameters
        ----------
        name:
            The widget/component name.
        instance:
            The instance to destroy.
        """
        self._fire_hook("on_destroy", name, instance)
        tracked = self._instances.get(name, [])
        if instance in tracked:
            tracked.remove(instance)

    def list_registered(self) -> list[str]:
        """Return all registered widget/component names."""
        return list(self._registry.keys())

    def _fire_hook(self, event: str, name: str, instance: Any) -> None:
        """Fire all hooks for a lifecycle event."""
        hooks = self._lifecycle_hooks.get(name, {}).get(event, [])
        for hook in hooks:
            try:
                hook(instance)
            except Exception:
                logger.exception("Lifecycle hook %s on %r failed.", event, name)

    def __contains__(self, name: str) -> bool:
        return self.get(name) is not None

    def __len__(self) -> int:
        return len(self._registry)


__all__ = ["WidgetRegistry"]
