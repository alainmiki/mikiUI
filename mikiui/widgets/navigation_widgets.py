"""Drawer, Rail, and ContextWindow layout widgets.

These provide slide-in panels and contextual overlays commonly found in
desktop-style web applications.
"""

from __future__ import annotations

from typing import Any

from ..components import Div, Span, A, Ul
from ..components.base import Component


class Drawer(Component):
    """A slide-in drawer / side panel that can be toggled open/closed.

    Uses Alpine.js for interactive toggle behavior. The drawer starts hidden
    unless ``open=True`` is set. Toggle it externally by setting the `show`
    Alpine.js variable on this drawer's scope.

    :param content:   Drawer body content.
    :param title:     Optional drawer header title.
    :param side:      Which edge to slide from: ``"left"`` (default),
                    ``"right"``, ``"top"``, ``"bottom"``.
    :param size:      ``"sm"``, ``"md"`` (default), or ``"lg"``.
    :param closable:  If ``True`` (default), show a close button in the header.
    :param open:      If ``True``, drawer starts open. Set ``False`` for a hidden drawer.
    :param attrs:     Extra HTML attributes.

    Example::

        # Include in an Alpine.js scoped container
        # <div x-data="{ navOpen: false }">
        #   <button @click="navOpen = true">Menu</button>
        #   <div x-data="{ show: navOpen }">
        #     <Drawer>...</Drawer>
        #   </div>
        # </div>

        # Or for immediate visibility:
        Drawer(Div("Content"), title="Quick Panel", open=True)
    """

    tag = "div"

    def __init__(
        self,
        *content: Any,
        title: str | None = None,
        side: str = "left",
        size: str = "md",
        closable: bool = True,
        open: bool = False,
        **attrs: Any,
    ) -> None:
        classes = f"miki-drawer miki-drawer-{side} miki-drawer-{size}"
        attrs.setdefault("class", classes)
        attrs.setdefault("role", "dialog")
        attrs.setdefault("aria-modal", "true")
        attrs.setdefault("aria-labelledby", f"{title or 'drawer'}-title")
        attrs.setdefault("x-data", "{show: false}" if not open else "{show: true}")
        attrs.setdefault(":class", "{'miki-drawer-open': show}")

        children: list[Any] = []

        children.append(
            Div(
                class_="miki-drawer-overlay",
                x_show="show",
                x_on_click="show = false",
            )
        )

        panel_children: list[Any] = []

        if title or closable:
            header_children: list[Any] = []
            if title:
                header_children.append(
                    Span(title, class_="miki-drawer-title", id=f"{title}-title")
                )
            if closable:
                header_children.append(
                    Span(
                        "×",
                        class_="miki-drawer-close",
                        role="button",
                        aria_label="Close drawer",
                        x_on_click="show = false",
                    )
                )
            panel_children.append(
                Div(*header_children, class_="miki-drawer-header")
            )

        if content:
            panel_children.append(
                Div(*content, class_="miki-drawer-body")
            )

        panel = Div(
            *panel_children,
            class_="miki-drawer-panel",
            x_show="show",
        )

        children.append(panel)

        super().__init__(*children, **attrs)


class Rail(Component):
    """A slim icon-only navigation rail (left or right side of the screen).

    :param items:     List of (label, href, icon_name) tuples or Component instances.
    :param side:      ``"left"`` (default) or ``"right"``.
    :param attrs:     Extra HTML attributes.

    Example::

        Rail(
            ("Dashboard", "/dashboard", "home"),
            ("Settings", "/settings", "settings"),
            ("Profile", "/profile", "user"),
            side="left",
        )
    """

    tag = "nav"

    def __init__(
        self,
        *items: Any,
        side: str = "left",
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = f"miki-rail miki-rail-{side}"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class", classes)
        attrs.setdefault("role", "navigation")
        attrs.setdefault("aria_label", "Navigation rail")

        children: list[Any] = []

        for item in items:
            if isinstance(item, tuple) and len(item) == 3:
                label, href, icon_name = item
                from .icon import Icon
                icon = Icon(icon_name, size=20)
                link = A(
                    Div(icon, Span(label, class_="miki-rail-label")),
                    href=href,
                    class_="miki-rail-item",
                )
                children.append(link)
            else:
                children.append(item)

        super().__init__(*children, **attrs)


class ContextWindow(Component):
    """A floating context menu / popover window.

    :param content:   Menu items or content.
    :param trigger:   Optional trigger element (button, icon, etc.).
    :param position:  Preferred position: ``"auto"`` (default), ``"top"``,
                      ``"bottom"``, ``"left"``, ``"right"``.
    :param align:     Alignment: ``"start"`` (default), ``"center"``, ``"end"``.
    :param attrs:     Extra HTML attributes.
    """

    tag = "div"

    def __init__(
        self,
        *content: Any,
        trigger: Any = None,
        position: str = "auto",
        align: str = "start",
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = f"miki-context-window miki-context-{position} miki-context-align-{align}"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class", classes)
        attrs.setdefault("role", "menu")
        attrs.setdefault("aria_hidden", "true")

        children: list[Any] = []

        if trigger is not None:
            children.append(trigger)

        # Menu content
        menu_items: list[Any] = []
        for item in content:
            if isinstance(item, tuple) and len(item) == 2 and callable(item[1]):
                label, action = item
                menu_items.append(
                    A(
                        label,
                        href="#",
                        role="menuitem",
                        class_="miki-context-item",
                        onclick=f"{action}(); return false;",
                    )
                )
            elif isinstance(item, tuple) and len(item) == 2:
                label, href = item
                menu_items.append(
                    A(label, href=href, role="menuitem", class_="miki-context-item")
                )
            else:
                menu_items.append(item)

        children.append(
            Ul(*menu_items, class_="miki-context-menu", role="menu")
        )

        super().__init__(*children, **attrs)
