"""Tabs component (composite of nav + sections).

Tabs provide accessible tabbed interfaces with:
- Keyboard navigation (Arrow keys, Home/End)
- ARIA roles and selected state
- Smooth transitions
- Icon support
- Vertical orientation
- Scrollable tab lists
- Closeable tabs

Parameters
----------
tabs : list of (label, content) tuples
    Tab definitions. Each label can be a string or tuple of (text, icon).
orientation : str
    "horizontal" (default) or "vertical".
scrollable : bool
    Allow horizontal scrolling when tabs overflow.
closeable : bool
    Show close button on each tab.
**attrs : Additional HTML attributes.

Example
-------
>>> # Basic tabs
>>> Tabs([("Overview", "Content 1"), ("Settings", "Content 2")])

>>> # With icons
>>> Tabs([
...     ("Home", "Overview", "🏠"),
...     ("Settings", "Settings content", "⚙️"),
... ])

>>> # Vertical tabs
>>> Tabs([("A", "A content"), ("B", "B content")], orientation="vertical")
"""

from __future__ import annotations

import uuid
from typing import Any

from .base import Component
from .html import Nav, Section, Div, Span, P
from .button import Button
from .input import Input


class Tabs(Component):
    tag = "div"

    def __init__(
        self,
        tabs: list[tuple[str, Any] | tuple[str, Any, str]],
        orientation: str = "horizontal",
        scrollable: bool = False,
        closeable: bool = False,
        **attrs: Any,
    ) -> None:
        user_class = attrs.pop("class_", "")
        attrs["class_"] = f"miki-tabs miki-tabs-{orientation} {user_class}".strip()
        attrs.setdefault("role", "tablist")

        if orientation not in ("horizontal", "vertical"):
            raise ValueError("orientation must be 'horizontal' or 'vertical'")

        group = "miki-tabs-" + uuid.uuid4().hex[:8]
        buttons = []
        panels = []

        for i, tab in enumerate(tabs):
            label, content = tab[:2]
            icon = tab[2] if len(tab) > 2 else None

            tab_class = "miki-tab" + (" miki-tab-active" if i == 0 else "")
            if scrollable:
                tab_class += " miki-tab-scrollable"

            aria_selected = "true" if i == 0 else "false"

            tab_attrs = {
                "type": "button",
                "role": "tab",
                "id": f"{group}-tab-{i}",
                "aria_selected": aria_selected,
                "aria_controls": f"{group}-panel-{i}",
                "tabindex": "0" if i == 0 else "-1",
                "class_": tab_class,
            }

            if orientation == "vertical":
                tab_attrs["class_"] += " miki-tab-vertical"

            tab_attrs["x_on_click"] = f"mikiTabs.show('{group}', {i})"

            tab_attrs["x_on_keydown.enter"] = f"mikiTabs.show('{group}', {i})"
            tab_attrs["x_on_keydown.space"] = f"mikiTabs.show('{group}', {i}); $event.preventDefault()"

            if i > 0 and orientation == "horizontal":
                tab_attrs["x_on_keydown.arrowleft"] = f"mikiTabs.show('{group}', {max(0, i-1)})"
                tab_attrs["x_on_keydown.arrowright"] = f"mikiTabs.show('{group}', {min(len(tabs)-1, i+1)})"
            elif i > 0 and orientation == "vertical":
                tab_attrs["x_on_keydown.arrowup"] = f"mikiTabs.show('{group}', {max(0, i-1)})"
                tab_attrs["x_on_keydown.arrowdown"] = f"mikiTabs.show('{group}', {min(len(tabs)-1, i+1)})"

            tab_attrs["x_on_keydown.home"] = f"mikiTabs.show('{group}', 0)"
            tab_attrs["x_on_keydown.end"] = f"mikiTabs.show('{group}', {len(tabs)-1})"

            close_btn = None
            if closeable:
                close_btn = Button(
                    "×",
                    type="button",
                    class_="miki-tab-close",
                    role="button",
                    aria_label="Close tab",
                    **{"x_on:click": f"event.stopPropagation(); mikiTabs.close('{group}', {i})"},
                )

            if icon:
                tab_content = (
                    Span(icon, class_="miki-tab-icon"),
                    P(label, class_="miki-tab-label"),
                )
                if closeable:
                    tab_content = tab_content + (close_btn,)
                buttons.append(Div(*tab_content, **tab_attrs))
            else:
                if closeable:
                    buttons.append(Div(label, close_btn, **tab_attrs))
                else:
                    buttons.append(Button(label, **tab_attrs))

            panel_attrs = {
                "role": "tabpanel",
                "id": f"{group}-panel-{i}",
                "aria_labeledby": f"{group}-tab-{i}",
                "class_": "miki-tab-panel miki-tab-panel-content" + (" miki-tab-panel-active" if i == 0 else ""),
            }
            if i > 0:
                panel_attrs["hidden"] = True

            panels.append(Section(content, **panel_attrs))

        tablist_class = "miki-tablist" + (f" miki-tablist-{orientation}" if orientation == "vertical" else "")
        super().__init__(Div(*buttons, class_=tablist_class, role="tablist"), *panels, **attrs)

    @property
    def active_tab(self) -> int:
        return int(self.attrs.get("data-active-tab", 0))