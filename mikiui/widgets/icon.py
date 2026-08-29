"""Icon system for MikiUI.

Icons are inline SVGs that work in both web and desktop (pywebview) contexts
without any external dependencies. This keeps the framework lightweight and
offline-capable.

Usage::

    from mikiui.widgets import Icon

    Icon("home")          # renders a home icon
    Icon("user", size=24) # 24px icon
    Icon("star", variant="solid")  # solid vs outline

Available icons: see :class:`IconSet` or ``mikiui.widgets.icon.MIKI_ICONS``.
"""

from __future__ import annotations

from typing import Any

from ..components.base import Component

# -- Icon definitions (SVG paths) ---------------------------------------------

# Each icon is a dict with 'outline' and 'solid' path data for a 24x24 viewBox.
MIKI_ICONS: dict[str, dict[str, str]] = {
    "home": {
        "outline": "M3 9.5L12 3l9 6.5V21a1 1 0 01-1 1h-5v-6H9v6H4a1 1 0 01-1-1V9.5z",
        "solid": "M3 9.5L12 3l9 6.5V21a1 1 0 01-1 1h-5v-6H9v6H4a1 1 0 01-1-1V9.5z",
    },
    "user": {
        "outline": "M12 12c2.7 0 4.9-2.2 4.9-4.9S14.7 2.2 12 2.2 7.1 4.4 7.1 7.1 9.3 12 12 12zm0 2.4c-3.2 0-5.9 2.7-5.9 5.9v.4h11.8v-.4c0-3.2-2.7-5.9-5.9-5.9z",
        "solid": "M12 12c2.7 0 4.9-2.2 4.9-4.9S14.7 2.2 12 2.2 7.1 4.4 7.1 7.1 9.3 12 12 12zm0 2.4c-3.2 0-5.9 2.7-5.9 5.4v.5h11.8v-.5c0-3.2-2.7-5.4-5.9-5.4z",
    },
    "search": {
        "outline": "M15.5 14h-.79l-.27-.27C15.41 12.39 16 11.26 16 10 16 6.69 13.31 4 10 4S4 6.69 4 10 6.69 16 10 16c1.26 0 2.39-.59 3.21-1.54l.27.27v.79l5 4.99L20.49 19l-4.99-5zm-5.5 0C7.01 14 4 10.99 4 7s3.01-6 6.5-6 6.5 3.01 6.5 6.5S12.99 14 10 14z",
        "solid": "M15.5 14h-.79l-.27-.27C15.41 12.39 16 11.26 16 10 16 6.69 13.31 4 10 4S4 6.69 4 10 6.69 16 10 16c1.26 0 2.39-.59 3.21-1.54l.27.27v.79l5 4.99L20.49 19l-4.99-5zm-5.5 0C7.01 14 4 10.99 4 7s3.01-6 6.5-6 6.5 3.01 6.5 6.5S12.99 14 10 14z",
    },
    "star": {
        "outline": "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7.91 14.14 4 9.27l6.91-1.01L12 2z",
        "solid": "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7.91 14.14 4 9.27l6.91-1.01L12 2z",
    },
    "menu": {
        "outline": "M3 6h18v2H3zM3 11h18v2H3zM3 16h18v2H3z",
        "solid": "M3 6h18v2H3zM3 11h18v2H3zM3 16h18v2H3z",
    },
    "close": {
        "outline": "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z",
        "solid": "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z",
    },
    "check": {
        "outline": "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z",
        "solid": "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z",
    },
    "plus": {
        "outline": "M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z",
        "solid": "M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z",
    },
    "edit": {
        "outline": "M5 21h14v-2H5v2zm11.5-5.5l-1.4-1.4-6.1 6.1v.5h.5l6.1-6.1zm1.3-1.3l-1.5-1.5L19 7.5V3h-.5L14 7.5l1.5 1.5L19.5 9v4.5l-3.7 3.7z",
        "solid": "M5 21h14v-2H5v2zm11.5-5.5l-1.4-1.4-6.1 6.1v.5h.5l6.1-6.1zm1.3-1.3l-1.5-1.5L19 7.5V3h-.5L14 7.5l1.5 1.5L19.5 9v4.5l-3.7 3.7z",
    },
    "trash": {
        "outline": "M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-3l-1 1H5v2h14V4z",
        "solid": "M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-3l-1 1H5v2h14V4z",
    },
    "settings": {
        "outline": "M19.4 13a7.5 7.5 0 000-2l2-1.6-2-3.3-.04-.4 2.4-1.9v-4l-2.9 1.2c-.5-1-1.2-1.8-2-2.4l-.7-2.8h-4l-.7 2.8c-.8.6-1.5 1.4-2 2.4l-2.9-1.2v4l2.4 1.9c-.1.3-.1.6-.1 1s.1 1.7 2.1 1.7l2-1.6 2 3.3.04.4-2.4 1.9v4l2.9-1.2c.5 1 1.2 1.8 2 2.4l.7 2.8h4l.7-2.8c.8-.6 1.5-1.4 2-2.4l2.9 1.2v-4l-2-1.6c-.1-.2-.1-.5-.1-.8l0-.1z",
        "solid": "M19.4 13a7.5 7.5 0 000-2l2-1.6-2-3.3-.04-.4 2.4-1.9v-4l-2.9 1.2c-.5-1-1.2-1.8-2-2.4l-.7-2.8h-4l-.7 2.8c-.8.6-1.5 1.4-2 2.4l-2.9-1.2v4l2.4 1.9c-.1.3-.1.6-.1 1s.1 1.7 2.1 1.7l2-1.6 2 3.3.04.4-2.4 1.9v4l2.9-1.2c.5 1 1.2 1.8 2 2.4l.7 2.8h4l.7-2.8c.8-.6 1.5-1.4 2-2.4l2.9 1.2v-4l-2-1.6c-.1-.2-.1-.5-.1-.8l0-.1z",
    },
    "download": {
        "outline": "M19 13v8H5v-8H3l7-7 7 7v-7h2zm-2-8h-4V1h-2v4H8l4 4 4-4z",
        "solid": "M19 13v8H5v-8H3l7-7 7 7v-7h2zm-2-8h-4V1h-2v4H8l4 4 4-4z",
    },
    "upload": {
        "outline": "M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-4h-6v4zm8.31-9.31l-1.31-1.31L13 15.17V2h-2v13.17l-2.69-2.69-1.41 1.41 5 5 5-5z",
        "solid": "M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-4h-6v4zm8.31-9.31l-1.31-1.31L13 15.17V2h-2v13.17l-2.69-2.69-1.41 1.41 5 5 5-5z",
    },
    "eye": {
        "outline": "M12 5c-7 0-11 7-11 7s4 7 11 7 11-7 11-7-4-7-11-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z",
        "solid": "M12 5c-7 0-11 7-11 7s4 7 11 7 11-7 11-7-4-7-11-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z",
    },
    "bell": {
        "outline": "M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6h-1V8c0-2.76-2.24-5-5-5S7 5.24 7 8v6H5c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2zm-8-2V8c0-1.66 1.34-3 3-3s3 1.34 3 3v6H9z",
        "solid": "M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6h-1V8c0-2.76-2.24-5-5-5S7 5.24 7 8v6H5c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2zm-8-2V8c0-1.66 1.34-3 3-3s3 1.34 3 3v6H9z",
    },
    "mail": {
        "outline": "M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 2l-8 5-8-5h16zm0 12H4V8l8 5 8-5v10z",
        "solid": "M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 2l-8 5-8-5h16zm0 12H4V8l8 5 8-5v10z",
    },
    "calendar": {
        "outline": "M19 4h-1V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11zm0-13H5V6h14v1z",
        "solid": "M19 4h-1V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11zm0-13H5V6h14v1z",
    },
    "clock": {
        "outline": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z",
        "solid": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z",
    },
    "moon": {
        "outline": "M10 2c-1.34.42-2.48 1.17-3.43 2.14C3.34 7.29 1 10.35 1 14c0 3.87 3.13 7 7 7 3.64 0 6.68-2.35 7.86-5.64-2.69.35-5.43.34-8.12-.02.15.44.27.89.27 1.35 0 2.76-2.24 5-5 5-2.76 0-5-2.24-5-5s2.24-5 5-5c1.34 0 2.55.41 3.53 1.08C15.93 4.64 16 3.85 16 3c0-.83-.17-1.63-.47-2.38-.96.47-1.93 1.14-2.86 1.97C12.25 2.25 11.17 2 10 2z",
        "solid": "M10 2c-1.34.42-2.48 1.17-3.43 2.14C3.34 7.29 1 10.35 1 14c0 3.87 3.13 7 7 7 3.64 0 6.68-2.35 7.86-5.64-2.69.35-5.43.34-8.12-.02.15.44.27.89.27 1.35 0 2.76-2.24 5-5 5-2.76 0-5-2.24-5-5s2.24-5 5-5c1.34 0 2.55.41 3.53 1.08C15.93 4.64 16 3.85 16 3c0-.83-.17-1.63-.47-2.38-.96.47-1.93 1.14-2.86 1.97C12.25 2.25 11.17 2 10 2z",
    },
    "sun": {
        "outline": "M12 4.5V2m0 20v-2.5M5.64 5.64l1.77 1.77M16.59 16.59l1.77 1.77M4.5 12H2m20 0h-2.5M6.34 16.59l1.77-1.77M13.41 7.41l1.77-1.77M12 7a5 5 0 100 10 5 5 0 000-10z",
        "solid": "M12 4.5V2m0 20v-2.5M5.64 5.64l1.77 1.77M16.59 16.59l1.77 1.77M4.5 12H2m20 0h-2.5M6.34 16.59l1.77-1.77M13.41 7.41l1.77-1.77M12 7a5 5 0 100 10 5 5 0 000-10z",
    },
    "info": {
        "outline": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z",
        "solid": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z",
    },
    "alert": {
        "outline": "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z",
        "solid": "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z",
    },
    "chevron-left": {
        "outline": "M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z",
        "solid": "M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z",
    },
    "chevron-right": {
        "outline": "M8.59 16.59L10.17 15 14 10.83 10.17 6.41 8.59 8 12.41 12 8.59 16.59z",
        "solid": "M8.59 16.59L10.17 15 14 10.83 10.17 6.41 8.59 8 12.41 12 8.59 16.59z",
    },
    "arrow-left": {
        "outline": "M20 11H7.83l5.89-5.89-1.42-1.41L4.41 12l7.89 7.89 1.42-1.41L7.83 13z",
        "solid": "M20 11H7.83l5.89-5.89-1.42-1.41L4.41 12l7.89 7.89 1.42-1.41L7.83 13z",
    },
    "arrow-right": {
        "outline": "M4 11h12.17l-5.89-5.89 1.42-1.41L20 12l-7.89 7.89-1.42-1.41L16.17 13z",
        "solid": "M4 11h12.17l-5.89-5.89 1.42-1.41L20 12l-7.89 7.89-1.42-1.41L16.17 13z",
    },
    "external-link": {
        "outline": "M19 19H5V5h7V3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3l-1.41 1.41L19 10.59V13h-2V8.41l-3.3-3.3C13.13 5.99 13 6.71 13 7.41V11h-2V7.41c0-.7.87-1.41 1.59-2.12L19.59 1.41 14 3z",
        "solid": "M19 19H5V5h7V3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3l-1.41 1.41L19 10.59V13h-2V8.41l-3.3-3.3C13.13 5.99 13 6.71 13 7.41V11h-2V7.41c0-.7.87-1.41 1.59-2.12L19.59 1.41 14 3z",
    },
    "copy": {
        "outline": "M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12c1.1 0 2-.9 2-2s-.9-2-2-2zm3 4v14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-4.18C16.82 2.15 16.34 2 15.82 2H8.18C7.66 2 7.18 2.15 6.83 3H4v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-4.05c-.25-1.32-.74-2.5-1.45-3.47L11 3 10.59 2.41C10.22 1.83 9.65 1.5 8.98 1.5H8v14c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-3.05c-.25-1.32-.74-2.5-1.45-3.47L11 3 10.59 2.41C10.22 1.83 9.65 1.5 8.98 1.5H8v14c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z",
        "solid": "M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12c1.1 0 2-.9 2-2s-.9-2-2-2zm3 4v14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-4.18C16.82 2.15 16.34 2 15.82 2H8.18C7.66 2 7.18 2.15 6.83 3H4v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-3.05c-.25-1.32-.74-2.5-1.45-3.47L11 3 10.59 2.41C10.22 1.83 9.65 1.5 8.98 1.5H8v14c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-3.05c-.25-1.32-.74-2.5-1.45-3.47L11 3 10.59 2.41C10.22 1.83 9.65 1.5 8.98 1.5H8v14c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z",
    },
}


class IconSet:
    """Registry of available icons.

    Usage::

        from mikiui.widgets import IconSet

        IconSet.has_icon("home")       # True
        IconSet.icon_names()           # ['home', 'user', ...]
    """

    @staticmethod
    def has_icon(name: str) -> bool:
        return name in MIKI_ICONS

    @staticmethod
    def icon_names() -> list[str]:
        return sorted(MIKI_ICONS.keys())


class Icon(Component):
    """An inline SVG icon.

    Icons work in both web and desktop contexts — no external font or CDN
    dependency required. The SVG is rendered inline, so it inherits the
    current text color and scales with font-size.

    :param name:    Icon name (e.g. ``"home"``, ``"user"``). Must be in
                    :data:`MIKI_ICONS`.
    :param size:    Pixel size (default 16). Sets ``width``/``height``/``viewBox``.
    :param variant: ``"outline"`` (default) or ``"solid"``.
    :param class_:  Additional CSS classes.
    :param attrs:   Extra HTML attributes (e.g. ``aria_label``).

    Example::

        Icon("home", size=24)
        Icon("star", variant="solid", class_="text-yellow-400")

    Raises
    ------
    ValueError
        If ``name`` is not a known icon.
    """

    tag = "svg"

    def __init__(
        self,
        name: str,
        *,
        size: int = 16,
        variant: str = "outline",
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        if name not in MIKI_ICONS:
            raise ValueError(
                f"Unknown icon '{name}'. "
                f"Available: {', '.join(IconSet.icon_names())}"
            )

        icon_data = MIKI_ICONS[name]
        path_data = icon_data.get(variant, icon_data.get("outline", ""))

        classes = "miki-icon"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class_", classes)

        attrs.setdefault("xmlns", "http://www.w3.org/2000/svg")
        attrs.setdefault("width", str(size))
        attrs.setdefault("height", str(size))
        attrs.setdefault("viewBox", "0 0 24 24")
        attrs.setdefault("fill", "none")
        attrs.setdefault("stroke", "currentColor")
        attrs.setdefault("stroke-width", "2")
        attrs.setdefault("stroke-linecap", "round")
        attrs.setdefault("stroke-linejoin", "round")

        if variant == "solid":
            attrs.pop("fill", None)
            attrs["fill"] = "currentColor"

        attrs.setdefault("aria_hidden", "true")

        from ..components.base import component
        PathEl = component("path")
        path = PathEl(d=path_data)

        super().__init__(path, **attrs)
