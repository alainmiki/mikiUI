"""MenuItem component (menu item button)."""

from __future__ import annotations

from typing import Any

from .base import Component


class MenuItem(Component):
    """A ``<button role="menuitem">`` element for use in menus.

    The deprecated ``<menuitem>`` element is not used; instead a
    ``<button type="button">`` with ``role="menuitem"`` is emitted for
    broad browser compatibility.
    """

    tag = "button"

    def __init__(self, label: str, **attrs: Any) -> None:
        attrs.setdefault("type", "button")
        attrs.setdefault("role", "menuitem")
        super().__init__(label, **attrs)


# Backward-compatible alias — <menuitem> is deprecated in the HTML spec.
LegacyMenuItem = MenuItem
