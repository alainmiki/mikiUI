"""Layout widgets: Hero, Footer, and Sidebar.

These composite components provide common page-layout building blocks with
sensible defaults, accessibility attributes, and HTMX-friendly structure.

``Navbar`` is a base :class:`~mikiui.components.Navbar` component, so there is
no separate widget for it.
"""

from __future__ import annotations

from typing import Any

from ..components import H1, A, Div, P, Ul
from ..components.base import Component


class Hero(Component):
    """A full-width hero section with optional background image.

    :param title:    Heading text (rendered as ``<h1>``).
    :param subtitle: Optional sub-heading below the title.
    :param image:    Optional background image URL.
    :param action:   Optional call-to-action content (e.g. a Button).
    :param variant:  ``"primary"`` (default) or ``"secondary"`` color scheme.
    :param align:    Text alignment: ``"left"`` (default), ``"center"``, or ``"right"``.
    :param attrs:    Extra HTML attributes.

    Example::

        Hero("Welcome", subtitle="Build UIs in Python",
             action=Button("Get Started", variant="primary"),
             image="/hero-bg.jpg")
    """

    tag = "section"

    def __init__(
        self,
        title: str,
        *,
        subtitle: str | None = None,
        image: str | None = None,
        action: Any = None,
        variant: str = "primary",
        align: str = "left",
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = f"miki-hero miki-hero-{variant} miki-hero-{align}"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class", classes)

        if image:
            style = attrs.get("style")
            if style is None:
                attrs["style"] = {"background-image": f"url('{image}')"}
            elif isinstance(style, dict):
                style["background-image"] = f"url('{image}')"
            else:
                attrs["style"] = f"{style}; background-image: url('{image}');"

        attrs.setdefault("role", "banner")

        inner_children: list[Any] = [H1(title, class_="miki-hero-title")]

        if subtitle:
            inner_children.append(P(subtitle, class_="miki-hero-subtitle"))

        if action is not None:
            inner_children.append(Div(action, class_="miki-hero-action"))

        inner = Div(*inner_children, role="group")

        super().__init__(inner, **attrs)


class Footer(Component):
    """A sticky footer with optional social links and copyright text.

    :param content:   Footer content (links, copyright text, etc.).
    :param copyright: Optional copyright string (defaults to the app year).
    :param social:    Optional list of (label, href) tuples rendered as links.
    :param attrs:     Extra HTML attributes.
    """

    tag = "footer"

    def __init__(
        self,
        *content: Any,
        copyright: str | None = None,
        social: list[tuple[str, str]] | None = None,
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = "miki-footer"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class", classes)
        attrs.setdefault("role", "contentinfo")

        children: list[Any] = list(content)

        if social:
            links = [A(label, href=href, class_="miki-footer-link") for label, href in social]
            children.append(Div(*links, class_="miki-footer-social"))

        if copyright:
            children.append(P(copyright, class_="miki-footer-copyright"))

        super().__init__(*children, **attrs)


class Sidebar(Component):
    """A collapsible sidebar / drawer for navigation or tools.

    :param items:     List of (label, href) tuples or Component instances.
    :param title:     Optional sidebar header title.
    :param width:     Width CSS value (e.g. ``"250px"`` or ``"20%"``).
    :param mobile:    If ``True``, render as a mobile drawer (hidden by default).
    :param attrs:     Extra HTML attributes.
    """

    tag = "aside"

    def __init__(
        self,
        *items: Any,
        title: str | None = None,
        width: str = "250px",
        mobile: bool = False,
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = "miki-sidebar"
        if class_:
            classes += f" {class_}"
        if mobile:
            classes += " miki-sidebar-mobile"
        attrs.setdefault("class", classes)
        attrs.setdefault("role", "complementary")

        # Set width via style
        style = attrs.get("style")
        if isinstance(style, dict):
            style.setdefault("width", width)
        elif isinstance(style, str):
            attrs["style"] = f"{style.rstrip(';')}; width: {width};"
        else:
            attrs["style"] = {"width": width}

        children: list[Any] = []

        if title:
            children.append(H1(title, class_="miki-sidebar-title"))

        link_items: list[Any] = []
        for item in items:
            if isinstance(item, tuple) and len(item) == 2:
                label, href = item
                link_items.append(
                    A(label, href=href, class_="miki-sidebar-link", role="link")
                )
            else:
                link_items.append(item)

        if link_items:
            children.append(Ul(*link_items, class_="miki-sidebar-list"))

        super().__init__(*children, **attrs)
