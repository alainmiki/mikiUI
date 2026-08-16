"""MikiUI application package."""

from __future__ import annotations

from .app import MikiApp
from .plugin_discovery import (
    PluginMetadata,
    auto_load,
    discover_plugins,
    load_plugin,
)
from .plugins import ComponentPlugin, Plugin, ThemePlugin, WidgetPlugin
from .routes import Ctx, RouteDef, invoke_route, resolve_title
from .state import AppState
from .theme_registry import ThemeRegistry
from .widget_registry import WidgetRegistry

__all__ = [
    "MikiApp",
    "Ctx",
    "RouteDef",
    "AppState",
    "Plugin",
    "ThemePlugin",
    "ComponentPlugin",
    "WidgetPlugin",
    "WidgetRegistry",
    "ThemeRegistry",
    "PluginMetadata",
    "discover_plugins",
    "load_plugin",
    "auto_load",
    "resolve_title",
    "invoke_route",
]

