"""MenuItem component (``<menuitem>``)."""

from __future__ import annotations

from typing import Any

from .base import Component


class MenuItem(Component):
    """A ``<menuitem>`` element with the given ``label`` text."""

    tag = "menuitem"

    def __init__(self, label: str, **attrs: Any) -> None:
        super().__init__(label, **attrs)
