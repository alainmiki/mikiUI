"""MikiUI - Python-first UI framework.

Render UIs as standalone desktops or websites from Python component trees.
"""

from __future__ import annotations

from . import components
from .app import AppState, ComponentPlugin, Ctx, MikiApp, Plugin, RouteDef, ThemePlugin, WidgetPlugin
from .backend import create_app

# Re-export every public component at the top level so apps can do
# `from mikiui import Div, Button` (see context/plan.md API examples).
from .components import *  # noqa: F401,F403
from .engine import RawHtml, _, render, render_fragment, render_page, set_translator
from .router import Router
from .themes import Theme, get_theme, list_themes, register_theme

__version__ = "0.0.1"

__all__ = [
    "MikiApp",
    "Ctx",
    "AppState",
    "Plugin",
    "ThemePlugin",
    "ComponentPlugin",
    "WidgetPlugin",
    "RouteDef",
    "render",
    "render_page",
    "render_fragment",
    "_",
    "RawHtml",
    "set_translator",
    "create_app",
    "components",
    "Router",
    "Theme",
    "register_theme",
    "get_theme",
    "list_themes",
    "__version__",
]
