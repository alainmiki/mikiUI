"""MikiUI Navbar component for responsive navigation.

A responsive navbar with hamburger menu for mobile and dropdown menus.

Example usage:
    from mikiui.components import Navbar

    navbar = Navbar(
        brand="MyApp",
        links=[("Home", "/"), ("About", "/about"), ("Contact", "/contact")],
    )

Advanced usage with dark theme and sticky positioning:
    navbar = Navbar(
        brand="MyApp",
        links=[("Home", "/"), ("Docs", "/docs")],
        sticky=True,
        dark=True,
        right=Button("Login"),
    )
"""

from __future__ import annotations

from typing import Any

from ..components.base import Component
from ..components.button import Button
from ..components.html import A, Div, Li, Ul
from ..engine.bridge import bridge_attr


class Navbar(Component):
    """A responsive navigation bar with brand, links, and mobile toggle.

    :param brand:     Brand / logo text or element (left side).
    :param links:     List of (label, href) tuples for navigation links.
    :param items:     Additional positional items (Component instances) to
                      render between links and right-side content.
    :param right:     Optional right-side content (buttons, profile, etc.).
    :param sticky:    If ``True``, the navbar stays fixed at the top.
    :param dark:      If ``True``, use dark color scheme (white text).
    :param class_:    Additional CSS classes.
    :param attrs:     Extra HTML attributes (aria-*, data-*, etc.).

    Accessibility:
    - ``role="navigation"``, ``aria-label="Main navigation"``
    - Mobile hamburger button with ``aria-label="Toggle navigation menu"``
    - Links rendered as ``<a>`` elements for proper keyboard navigation
    """

    tag = "nav"

    def __init__(
        self,
        brand: str | Any = "MikiUI",
        links: list[tuple[str, str]] | None = None,
        *items: Any,
        right: Any = None,
        sticky: bool = False,
        dark: bool = False,
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        links = links or []

        # Build CSS classes
        classes = "miki-navbar"
        if class_:
            classes += f" {class_}"
        if sticky:
            classes += " miki-navbar-sticky"
        if dark:
            classes += " miki-navbar-dark"
        attrs.setdefault("class_", classes)
        attrs.setdefault("role", "navigation")
        attrs.setdefault("aria-label", "Main navigation")
        attrs.setdefault("data-miki-navbar", "true")
        attrs.setdefault("touch-action", "manipulation")

        # Build nav links
        nav_items: list[Any] = []
        for label, href in links:
            nav_items.append(
                Li(A(label, href=href, class_="miki-navbar-link"))
            )
        # Additional positional items
        for item in items:
            nav_items.append(Li(item))

        # Hamburger button for mobile (accessible)
        hamburger = Button(
            "☰",
            type="button",
            class_="miki-navbar-toggle",
            aria_label="Toggle navigation menu",
            aria_expanded="false",
            **bridge_attr(
                "click",
                "var nav=this.closest('.miki-navbar'); var links=nav.querySelector('.miki-navbar-links'); var open=links.classList.toggle('open'); this.setAttribute('aria-expanded', String(open));",
            ),
        )

        # Container with flex layout
        container_children: list[Any] = [
            Div(
                (A(brand, href="/") if isinstance(brand, str) else brand),
                class_="miki-navbar-brand",
            ),
            Ul(*nav_items, class_="miki-navbar-links"),
        ]
        if right is not None:
            container_children.append(Div(right, class_="miki-navbar-right"))

        container = Div(*container_children, class_="miki-navbar-container")

        super().__init__(container, hamburger, **attrs)

