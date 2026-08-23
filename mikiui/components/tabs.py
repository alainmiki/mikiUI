"""Tabs component (composite of nav + sections).

Tabs provide accessible tabbed interfaces with:
- Keyboard navigation (Arrow keys, Home/End, Enter/Space)
- ARIA roles and selected state
- Smooth transitions
- Icon support
- Vertical orientation
- Scrollable tab lists
- Closeable tabs

Works **without** Alpine.js — all interactivity is handled by ``miki_ui.js``
via ``data-miki-*`` attributes and inline ``onclick`` handlers.  Alpine
``x_on_*`` directives are omitted entirely so the component works in the
offline desktop runtime.

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
from .button import Button
from .html import Div, P, Section, Span


class Tabs(Component):
    """Accessible tabbed interface — no Alpine.js required.

    Each tab button receives:
    - ``onclick`` calling ``mikiTabs.show('<group>', <index>)``
    - ``data-miki-tab-group`` and ``data-miki-tab-index`` for keyboard routing
    - Standard ARIA attributes (``role="tab"``, ``aria-selected``, ``tabindex``)

    The JS runtime (``miki_ui.js``) handles click + keyboard navigation
    (arrows, Home/End, Enter/Space).  Keyboard navigation is implemented
    in ``mikiTabs.init`` which binds a single ``keydown`` listener to
    the tablist container and focuses/moves between sibling tabs.
    """

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
        attrs.setdefault("data-miki-tabs", "true")

        if orientation not in ("horizontal", "vertical"):
            raise ValueError("orientation must be 'horizontal' or 'vertical'")

        group = "miki-tabs-" + uuid.uuid4().hex[:8]
        attrs["data-miki-tab-group"] = group

        buttons: list[Any] = []
        panels: list[Any] = []

        for i, tab in enumerate(tabs):
            label, content = tab[:2]
            icon = tab[2] if len(tab) > 2 else None

            is_active = i == 0
            tab_class = "miki-tab" + (" miki-tab-active" if is_active else "")
            if scrollable:
                tab_class += " miki-tab-scrollable"

            tab_attrs = {
                "type": "button",
                "role": "tab",
                "id": f"{group}-tab-{i}",
                "aria_selected": str(is_active).lower(),
                "aria_controls": f"{group}-panel-{i}",
                "tabindex": "0" if is_active else "-1",
                "class_": tab_class,
                "data-miki-tab-group": group,
                "data-miki-tab-index": str(i),
                "onclick": f"mikiTabs.show('{group}', {i});",
            }

            if orientation == "vertical":
                tab_attrs["class_"] += " miki-tab-vertical"

            if closeable:
                close_btn = Button(
                    "×",
                    type="button",
                    class_="miki-tab-close",
                    aria_label="Close tab",
                    **{"data-miki-tab-close": "true", "onclick": f"mikiTabs.close('{group}', {i});"},
                )
            else:
                close_btn = None

            if icon:
                tab_content = (
                    Span(icon, class_="miki-tab-icon"),
                    P(label, class_="miki-tab-label"),
                )
                if closeable:
                    tab_content = tab_content + (close_btn,)
                buttons.append(Button(*tab_content, **tab_attrs))
            elif closeable:
                buttons.append(Button(label, close_btn, **tab_attrs))
            else:
                buttons.append(Button(label, **tab_attrs))

            panel_attrs = {
                "role": "tabpanel",
                "id": f"{group}-panel-{i}",
                "aria_labeledby": f"{group}-tab-{i}",
                "class_": "miki-tab-panel miki-tab-panel-content" + (" miki-tab-panel-active" if is_active else ""),
            }
            if not is_active:
                panel_attrs["hidden"] = True

            panels.append(Section(content, **panel_attrs))

        tablist_class = "miki-tablist" + (f" miki-tablist-{orientation}" if orientation == "vertical" else "")
        super().__init__(
            Div(*buttons, class_=tablist_class, role="tablist", **{
                "data-miki-tablist": "true",
                "id": f"{group}-tablist",
            }),
            Div(*panels, **{
                "data-miki-tabpanel-list": "true",
                "id": f"{group}-pages",
            }),
            **attrs,
        )

    @property
    def active_tab(self) -> int:
        return int(self.attrs.get("data-active-tab", 0))

    @active_tab.setter
    def active_tab(self, value: int) -> None:
        self.attrs["data-active-tab"] = str(value)
