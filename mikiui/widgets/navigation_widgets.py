"""Drawer, Rail, and ContextWindow layout widgets.

These provide slide-in panels and contextual overlays commonly found in
desktop-style web applications.

Features:
- Drawer: slide-in panel with header, overlay, and smooth animations
- Rail: slim navigation rail with icons and labels
- ContextWindow: floating context menu/popover with positioning
"""

from __future__ import annotations

from typing import Any

from ..components import Div, Span, A, Ul, Button
from ..components.base import Component


class Drawer(Component):
    """A slide-in drawer / side panel that can be toggled open/closed.

    Features:
    - Smooth slide-in/out animations
    - Clickable overlay to close
    - Header with title and close button
    - Responsive size variants (sm, md, lg)
    - ARIA-compliant dialog semantics

    Parameters
    ----------
    *content : Any
        Drawer body content.
    title : str | None
        Optional drawer header title.
    side : str
        Which edge to slide from: "left" (default), "right", "top", "bottom".
    size : str
        Size variant: "sm" (200px), "md" (300px), "lg" (400px).
    closable : bool
        Show a close button in the header.
    open : bool
        Initial open state. External toggles control visibility via Alpine.
    **attrs : Additional HTML attributes.

    Example
    -------
    >>> # Inside an Alpine.js container
    >>> Drawer("Content", title="Quick Panel", side="left", open=True)

    >>> # Nested content
    >>> Drawer(
    ...     Div("Body content"),
    ...     title="Settings",
    ...     side="right",
    ...     size="lg"
    ... )
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
        if side not in ("left", "right", "top", "bottom"):
            raise ValueError(f"side must be 'left', 'right', 'top', or 'bottom', got {side!r}")

        if size not in ("sm", "md", "lg"):
            raise ValueError(f"size must be 'sm', 'md', or 'lg', got {size!r}")

        classes = f"miki-drawer miki-drawer-{side} miki-drawer-{size}"
        attrs.setdefault("class", classes)
        attrs.setdefault("role", "dialog")
        attrs.setdefault("aria-modal", "true")

        if title:
            attrs.setdefault("aria-labelledby", f"{title}-title")

        attrs.setdefault("x_data", f"{{show:{str(open).lower()},side:'{side}',size:'{size}'}}")

        attrs["x_init"] = """
        if (data.show) {
            if (data.side === 'left') $el.style.transform = 'translateX(0)';
            else if (data.side === 'right') $el.style.transform = 'translateX(0)';
            else if (data.side === 'top') $el.style.transform = 'translateY(0)';
            else if (data.side === 'bottom') $el.style.transform = 'translateY(0)';
        }
        """

        children: list[Any] = []

        overlay = Div(
            class_="miki-drawer-overlay",
            x_show="show",
            **{"x_on:click": "show = false"},
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
                    Button(
                        "×",
                        class_="miki-drawer-close",
                        type="button",
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
            x_transition="enter: ease-out duration-200; leave: ease-in duration-150",
        )

        children.append(overlay)
        children.append(panel)

        super().__init__(*children, **attrs)


class Rail(Component):
    """A slim icon-only navigation rail (left or right side of the screen).

    Features:
    - Icon-only items with tooltips
    - Vertical layout
    - Keyboard accessible
    - Active state highlighting

    Parameters
    ----------
    *items : tuple or Component
        List of (label, href, icon_name) tuples or Component instances.
    side : str
        "left" (default) or "right".
    collapsible : bool
        Collapse to icons-only when narrow viewport.
    **attrs : Additional HTML attributes.

    Example
    -------
    >>> Rail(
    ...     ("Dashboard", "/dashboard", "home"),
    ...     ("Settings", "/settings", "settings"),
    ...     side="left"
    ... )
    """

    tag = "nav"

    def __init__(
        self,
        *items: Any,
        side: str = "left",
        collapsible: bool = False,
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        if side not in ("left", "right"):
            raise ValueError(f"side must be 'left' or 'right', got {side!r}")

        classes = f"miki-rail miki-rail-{side}"
        if class_:
            classes += f" {class_}"
        if collapsible:
            classes += " miki-rail-collapsible"

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
                    role="link",
                )
                children.append(link)
            else:
                children.append(item)

        super().__init__(*children, **attrs)


class ContextWindow(Component):
    """A floating context menu / popover window.

    Features:
    - Smart positioning (auto-adjust for viewport)
    - Arrow indicator
    - ARIA-compliant menu semantics
    - Keyboard navigation

    Parameters
    ----------
    *content : Any
        Menu items (tuples or Components).
    trigger : Any
        Optional trigger element (button, icon, etc.).
    position : str
        Position: "auto" (default), "top", "bottom", "left", "right".
    align : str
        Alignment: "start" (default), "center", "end".
    width : str
        Width CSS value, e.g., "auto", "150px", "200px".
    **attrs : Additional HTML attributes.

    Example
    -------
    >>> # With trigger button
    >>> ContextWindow(
    ...     ("Open", "/open"),
    ...     ("Close", "/close"),
    ...     trigger=Button("Menu"),
    ...     position="bottom"
    ... )
    """

    tag = "div"

    def __init__(
        self,
        *content: Any,
        trigger: Any = None,
        position: str = "auto",
        align: str = "start",
        width: str = "auto",
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        if position not in ("auto", "top", "bottom", "left", "right"):
            raise ValueError(f"position must be 'auto', 'top', 'bottom', 'left', or 'right', got {position!r}")
        if align not in ("start", "center", "end"):
            raise ValueError(f"align must be 'start', 'center', or 'end', got {align!r}")

        classes = f"miki-context-window miki-context-{position} miki-context-align-{align}"
        if class_:
            classes += f" {class_}"

        attrs.setdefault("class", classes)
        attrs.setdefault("role", "menu")
        attrs.setdefault("style", f"min-width: {width};")

        children: list[Any] = []

        if trigger is not None:
            children.append(trigger)

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
                        **{"x_on:click": f"{action}();"},
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
            Div(
                Span(class_="miki-context-arrow"),
                Ul(*menu_items, class_="miki-context-menu", role="menu"),
                class_="miki-context-content",
            )
        )

        super().__init__(*children, **attrs)