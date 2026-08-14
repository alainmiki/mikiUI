"""MikiUI - Python-first UI framework.

Render UIs as standalone desktops or websites from Python component trees.
"""

from __future__ import annotations

from .app import MikiApp, Ctx, AppState, Plugin, ThemePlugin, ComponentPlugin, WidgetPlugin, RouteDef
from .engine import render, render_page, render_fragment, _, set_translator
from .backend import create_app
from . import components
from .router import Router
from .themes import Theme, register_theme, get_theme, list_themes

# Re-export every public component at the top level so apps can do
# `from mikiui import Div, Button` (see context/plan.md API examples).
from .components import *  # noqa: F401,F403

__version__ = "0.1.0"

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
