"""MikiUI theme system.

Provides infrastructure for color themes and framework themes (Tailwind, Bootstrap, plain CSS).
Themes can be registered via plugins or directly on the app.

The system distinguishes:
- **Framework themes**: Tailwind, Bootstrap, or plain CSS – these define how styles are processed.
- **Color themes**: light, dark, dracula – these define color variables (`--miki-*`).

A project can use framework + color themes together: the framework provides the CSS pipeline
(Tailwind JIT, Bootstrap, or our base CSS), and the color theme provides the actual color palette.

For Tailwind users wanting JIT builds:
```
mikiui build --target web --theme tailwind
```
This scans the project for MikiUI components/widgets, merges Tailwind config, and outputs static CSS.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

_RUNTIME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runtime"))
THEME_DIR = os.path.join(_RUNTIME_DIR, "themes")

# Color themes (use via theme="dark", theme="light", etc.)
COLOR_THEMES: dict[str, str] = {
    "light": "light.css",
    "dark": "dark.css",
    "dracula": "dracula.css",
    "solarized-dark": "solarized-dark.css",
}

# Framework themes – users can opt into Tailwind, Bootstrap, or plain CSS.
_FRAMEWORK_THEMES: dict[str, dict[str, Any]] = {
    "tailwind": {
        "cdn": "https://unpkg.com/tailwindcss@3.4.1/dist/tailwind.min.css",
        "daisyui": "https://unpkg.com/daisyui@5/dist/daisyui.min.css",
        "entry": "tailwind.css",  # Path relative to runtime dir
    },
    "bootstrap": {
        "cdn": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
        "js": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
    },
}

# Cache of all registered themes
_theme_registry: dict[str, Theme] = {}


def _load_builtin_themes() -> None:
    """Populate the registry with default color themes and framework themes.

    Only loads builtins, preserving any user/plugin-registered themes already
    in the registry.  Safe to call multiple times (idempotent).
    """
    for name, filename in COLOR_THEMES.items():
        _theme_registry[name] = Theme(
            name=name,
            source="builtin-color",
            css_path=os.path.join(THEME_DIR, filename),
        )

    # Framework themes (cdn-based or local tailwind build output)
    for fn, cfg in _FRAMEWORK_THEMES.items():
        _theme_registry[fn] = Theme(
            name=fn,
            source="builtin-framework",
            framework=fn,
            cdn_url=cfg.get("cdn"),
            js_url=cfg.get("js"),
        )


@dataclass
class Theme:
    """A MikiUI theme.

    Attributes
    ----------
    name: str
        Theme identifier (e.g. "dark", "tailwind", "my-theme").
    source: str
        Where the theme came from: "builtin-color", "builtin-framework", "plugin", "custom".
    framework: str | None
        One of "tailwind", "bootstrap", "css", or None.
    css_path: str | None
        Local path to a CSS file (loaded inline or served as asset).
    cdn_url: str | None
        Optional CDN URL for framework CSS.
    js_url: str | None
        Optional CDN URL for framework JS (e.g., Bootstrap bundle).
    tailwind_config: dict
        Optional Tailwind config merging with MikiUI defaults.
    variables: dict
        CSS custom property overrides like ``{"--miki-bg": "#fff"}``.
    extra_classes: list[str]
        CSS classes to add to ``<body>``.
    """

    name: str
    source: str = "custom"
    framework: str | None = None
    css_path: str | None = None
    cdn_url: str | None = None
    js_url: str | None = None
    tailwind_config: dict[str, Any] | None = None
    variables: dict[str, str] = field(default_factory=dict)
    extra_classes: list[str] = field(default_factory=list)

    def css(self) -> str:
        """Return the CSS content (inline if css_path exists, otherwise empty)."""
        if self.css_path and os.path.isfile(self.css_path):
            with open(self.css_path, encoding="utf-8") as fh:
                return fh.read()
        return ""

    def theme_links(self) -> dict[str, str]:
        """Return ``{rel: href}`` for CSS link tags (used when framework=cdn)."""
        result: dict[str, str] = {}
        if self.cdn_url:
            # Different rel for frameworks vs themes
            result[self.framework or "stylesheet"] = self.cdn_url
        return result

    def theme_scripts(self) -> dict[str, str]:
        """Return ``{type/s: href}`` for script tags."""
        result: dict[str, str] = {}
        if self.js_url:
            result["module"] = self.js_url
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "framework": self.framework,
            "variables": dict(self.variables),
            "extra_classes": list(self.extra_classes),
            "tailwind_config": self.tailwind_config or {},
        }


def register_theme(theme: Theme) -> None:
    """Register a user or plugin theme (overrides built-ins of the same name)."""
    _theme_registry[theme.name] = theme


def get_theme(name: str) -> Theme | None:
    """Return a theme by name, or ``None`` if unknown."""
    if not _theme_registry:
        _load_builtin_themes()
    return _theme_registry.get(name)


def list_themes() -> list[str]:
    """Return the names of all registered themes."""
    if not _theme_registry:
        _load_builtin_themes()
    return list(_theme_registry.keys())


def current_theme_name(app: Any) -> str:
    """Return ``app.theme`` or a sensible default."""
    return getattr(app, "theme", None) or "light"


def _init() -> None:
    _load_builtin_themes()


_init()


__all__ = [
    "Theme",
    "register_theme",
    "get_theme",
    "list_themes",
    "current_theme_name",
    "COLOR_THEMES",
    "THEME_DIR",
    "_RUNTIME_DIR",
]