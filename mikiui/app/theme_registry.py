"""Central theme registry for MikiUI.

Provides a registry for themes with inheritance, override support, and
runtime theme switching. Plugins register themes through this registry
instead of mutating ``MikiApp`` directly.

Usage:
    from mikiui.app.theme_registry import ThemeRegistry

    registry = ThemeRegistry()
    registry.register(Theme(name="my-theme", ...))
    theme = registry.get("my-theme")
    registry.set_active("my-theme")
"""

from __future__ import annotations

import copy
import logging
from typing import Any

from ..themes import Theme

logger = logging.getLogger(__name__)


class ThemeRegistry:
    """Central theme registry with inheritance and runtime switching.

    Manages theme registration, lookup, and activation. Supports theme
    inheritance: a theme can extend another theme and override specific
    properties.

    Attributes:
        _registry: Map of theme name to Theme dataclass.
        _active: Currently active theme name.
        _parent_registry: Optional parent registry (for chaining).
    """

    def __init__(self, parent_registry: ThemeRegistry | None = None) -> None:
        self._registry: dict[str, Theme] = {}
        self._active: str = "light"
        self._parent: ThemeRegistry | None = parent_registry
        self._inheritance: dict[str, str] = {}

    def register(self, theme: Theme, *, override: bool = False) -> None:
        """Register a theme.

        Parameters
        ----------
        theme:
            The Theme to register.
        override:
            If True, allow overriding an existing theme of the same name.
            If False (default), a warning is logged when overriding.
        """
        existing = self._registry.get(theme.name) or (
            self._parent._registry.get(theme.name) if self._parent else None
        )
        if existing and not override:
            logger.warning(
                "Theme %r already registered by %r; use override=True to replace.",
                theme.name,
                existing.source,
            )
        self._registry[theme.name] = theme
        # Backward compatibility: also register with global theme registry
        try:
            from ..themes import register_theme as _global_register
            _global_register(theme)
        except ImportError:
            pass
        logger.debug("Registered theme: %s (source=%s)", theme.name, theme.source)

    def inherit(self, child_name: str, parent_name: str) -> None:
        """Set up inheritance: child inherits from parent.

        Parameters
        ----------
        child_name:
            Name of the child theme.
        parent_name:
            Name of the parent theme to inherit from.
        """
        self._inheritance[child_name] = parent_name

    def get(self, name: str) -> Theme | None:
        """Return a theme by name, resolving inheritance.

        Parameters
        ----------
        name:
            Theme name to look up.

        Returns
        -------
        Theme | None
            The resolved theme, or None if not found.
        """
        # Check local registry first
        if name in self._registry:
            return self._resolve(name, self._registry[name])
        # Check parent
        if self._parent:
            parent_theme = self._parent.get(name)
            if parent_theme:
                return parent_theme
        return None

    def _resolve(self, name: str, theme: Theme) -> Theme:
        """Resolve inheritance for a theme."""
        parent_name = self._inheritance.get(name)
        if not parent_name:
            return theme
        parent = self.get(parent_name)
        if parent is None:
            return theme
        # Merge: parent properties are base, child overrides
        merged = copy.deepcopy(parent)
        merged.name = theme.name
        merged.source = theme.source
        merged.framework = theme.framework or merged.framework
        merged.css_path = theme.css_path or merged.css_path
        merged.cdn_url = theme.cdn_url or merged.cdn_url
        merged.js_url = theme.js_url or merged.js_url
        merged.tailwind_config = theme.tailwind_config or merged.tailwind_config
        merged.variables = {**merged.variables, **theme.variables}
        merged.extra_classes = list(dict.fromkeys(merged.extra_classes + theme.extra_classes))
        return merged

    def set_active(self, name: str) -> None:
        """Set the active theme by name.

        Parameters
        ----------
        name:
            Theme name to activate.

        Raises
        ------
        ValueError
            If the theme is not registered.
        """
        if name not in self._registry:
            parent = self._parent.get(name) if self._parent else None
            if parent is None:
                raise ValueError(
                    f"Unknown theme: {name!r}. Available: {self.list_all()}"
                )
        self._active = name

    def get_active(self) -> Theme | None:
        """Return the currently active theme."""
        return self.get(self._active)

    def active_name(self) -> str:
        """Return the name of the currently active theme."""
        return self._active

    def list_all(self) -> list[str]:
        """Return all registered theme names (including parent)."""
        names = set(self._registry.keys())
        if self._parent:
            names.update(self._parent.list_all())
        return sorted(names)

    def list_registered(self) -> list[str]:
        """Return theme names registered directly in this registry."""
        return sorted(self._registry.keys())

    def to_dict(self) -> dict[str, Any]:
        """Serialize all themes to a dict."""
        return {
            "active": self._active,
            "themes": {name: theme.to_dict() for name, theme in self._registry.items()},
        }

    def __len__(self) -> int:
        return len(self._registry)

    def __contains__(self, name: str) -> bool:
        return self.get(name) is not None


__all__ = ["ThemeRegistry"]
