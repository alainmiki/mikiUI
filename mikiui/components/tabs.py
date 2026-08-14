"""Tabs component (composite of nav + sections).

Client-side switching is handled by the bundled ``miki_ui.js`` helper
(``window.mikiTabs.show``), so it works with no CDN/Alpine dependency. ARIA
roles and ``aria-selected`` are kept in sync for accessibility.
"""

from __future__ import annotations

import uuid
from typing import Any

from .base import Component
from .html import Nav, Section, Div
from .button import Button


class Tabs(Component):
    """A simple tabbed interface.

    ``tabs`` is a list of ``(label, content)`` pairs. Clicking a tab shows its
    panel and hides the others (pure JS, offline-friendly).
    """

    tag = "div"

    def __init__(self, tabs: list[tuple[str, Any]], **attrs: Any) -> None:
        attrs.setdefault("class", "miki-tabs")
        attrs.setdefault("role", "tablist")
        group = "miki-tabs-" + uuid.uuid4().hex[:8]
        buttons = []
        panels = []
        for i, (label, content) in enumerate(tabs):
            buttons.append(
                Button(
                    label,
                    type="button",
                    role="tab",
                    id=f"{group}-tab-{i}",
                    aria_selected="true" if i == 0 else "false",
                    onclick=f"mikiTabs.show('{group}', {i})",
                    class_="miki-tab" + (" miki-tab-active" if i == 0 else ""),
                )
            )
            panels.append(
                Section(
                    content,
                    role="tabpanel",
                    id=f"{group}-panel-{i}",
                    **({"style": "display:none"} if i > 0 else {}),
                )
            )
        super().__init__(Div(*buttons, class_="miki-tablist", role="tablist"), *panels, **attrs)
