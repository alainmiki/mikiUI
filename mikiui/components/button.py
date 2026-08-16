"""Button components with extensive styling options.

Features:
- Multiple variants (primary, secondary, ghost, danger, success, warning)
- Sizes (xs, sm, md, lg, xl)
- Loading states
- Icon support (leading/trailing)
- Outline variant
- Text variant
- Block (full width) variant
- Dark mode compatible
- Full ARIA support
"""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import Span


class Button(Component):
    """A styled ``<button>`` element with modern appearance.

    Parameters
    ----------
    *children : Button content (text, icons, etc.)
    variant : str
        "primary" (default), "secondary", "ghost", "danger", "success", "warning",
        "link", "outline", or "text".
    size : str
        "xs", "sm", "md" (default), "lg", or "xl".
    loading : bool
        Show loading spinner and disable button.
    block : bool
        Make button full width.
    icon : str | None
        Icon name (uses MikiUI icon font or FontAwesome).
    icon_position : str
        "left" (default) or "right".
    **attrs : Additional HTML attributes (including HTMX attributes).

    Example
    -------
    >>> # Primary button
    >>> Button("Submit", variant="primary")

    >>> # Ghost button with icon
    >>> Button("Cancel", variant="ghost", icon="x", icon_position="right")

    >>> # Loading button
    >>> Button("Saving...", loading=True)

    >>> # Outline button
    >>> Button("Delete", variant="outline", variant="danger")
    """

    tag = "button"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "button")
        variant = attrs.pop("variant", "primary")
        size = attrs.pop("size", "md")
        loading = attrs.pop("loading", False)
        block = attrs.pop("block", False)
        icon = attrs.pop("icon", None)
        icon_position = attrs.pop("icon_position", "left")

        classes = self._build_classes(variant, size, loading, block)
        user_classes = attrs.pop("class_", "")
        attrs["class_"] = f"{classes} {user_classes}".strip()

        if loading:
            attrs["aria-busy"] = "true"
            attrs["aria-disabled"] = "true"
            attrs["disabled"] = True

        if icon and not loading:
            icon_element = self._make_icon(icon, icon_position)
            if icon_position == "left":
                children = (icon_element,) + children
            else:
                children = children + (icon_element,)

        super().__init__(*children, **attrs)

    @classmethod
    def _build_classes(cls, variant: str, size: str, loading: bool, block: bool) -> str:
        base = "miki-btn"

        if size == "xs":
            base += " miki-btn-xs"
        elif size == "sm":
            base += " miki-btn-sm"
        elif size == "lg":
            base += " miki-btn-lg"
        elif size == "xl":
            base += " miki-btn-xl"

        if loading:
            base += " miki-btn-loading"
        if block:
            base += " miki-btn-block"

        if variant == "primary":
            base += " miki-btn-primary"
        elif variant == "secondary":
            base += " miki-btn-secondary"
        elif variant == "ghost":
            base += " miki-btn-ghost"
        elif variant == "danger":
            base += " miki-btn-danger"
        elif variant == "success":
            base += " miki-btn-success"
        elif variant == "warning":
            base += " miki-btn-warning"
        elif variant == "link":
            base += " miki-btn-link"
        elif variant == "outline":
            base += " miki-btn-outline"
        elif variant == "text":
            base += " miki-btn-text"

        return base

    @classmethod
    def _make_icon(cls, name: str, position: str) -> Any:
        from ..widgets.icon import Icon
        classes = f"miki-btn-icon miki-btn-icon-{position}"
        return Icon(name, class_=classes)

    @classmethod
    def icon_button(
        cls,
        icon: str,
        aria_label: str,
        **attrs: Any,
    ) -> Any:
        """Create a button with only an icon.

        Parameters
        ----------
        icon : str
            Icon name.
        aria_label : str
            Accessible label.
        **attrs : Additional attributes.

        Returns an icon-only button.
        """
        attrs.setdefault("class", "miki-btn-icon-only")
        attrs.setdefault("aria-label", aria_label)

        return cls(icon, **attrs)

    @classmethod
    def group(
        cls,
        *buttons: Any,
        direction: str = "horizontal",
        **attrs: Any,
    ) -> Any:
        """Create a group of buttons.

        Parameters
        ----------
        *buttons : Button instances
        direction : str
            "horizontal" (default) or "vertical".
        **attrs : Additional attributes for the container.

        Returns a container with grouped buttons.
        """
        from .html import Div

        attrs.setdefault("class", f"miki-btn-group miki-btn-group-{direction}")
        return Div(*buttons, **attrs)

    @classmethod
    def toggle(
        cls,
        icon_on: str,
        icon_off: str,
        aria_label_on: str,
        aria_label_off: str,
        **attrs: Any,
    ) -> Any:
        """Create a toggle button (click to switch between two icon states).

        Works **without** Alpine.js — ``miki_ui.js`` auto-initializes the
        toggle via ``data-miki-toggle`` and handles click events.

        Parameters
        ----------
        icon_on, icon_off : str
            Icon names for each state.
        aria_label_on, aria_label_off : str
            Accessible labels for each state.
        **attrs : Additional attributes.

        Returns a toggle button (wrapped in a ``<span class="miki-toggle-btn">``).
        """
        btn_attrs = {
            "data-miki-toggle": "true",
            "data-miki-icon-on": icon_on,
            "data-miki-icon-off": icon_off,
            "data-miki-aria-label-on": aria_label_on,
            "data-miki-aria-label-off": aria_label_off,
            "aria-pressed": "true",
            "data-miki-state": "on",
        }
        user_classes = attrs.pop("class_", "")
        user_classes = f"miki-toggle-btn {user_classes}".strip()
        btn_attrs["class_"] = user_classes
        btn_attrs.update(attrs)

        return Span(
            cls(icon_on, aria_label=aria_label_on, **btn_attrs),
            class_="miki-toggle-btn-wrapper",
        )


class SubmitButton(Button):
    """A submit button — defaults to ``type="submit"`` and ``variant="primary"``."""

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs["type"] = "submit"
        super().__init__(*children, **attrs)


class IconButton(Button):
    """An icon-only button with proper accessibility."""

    tag = "button"

    def __init__(self, icon: str, aria_label: str, **attrs: Any) -> None:
        attrs.setdefault("aria-label", aria_label)
        attrs.setdefault("type", "button")
        attrs.setdefault("class", "miki-btn-icon-only")

        icon_span = Span(icon, class_="miki-btn-icon-content")
        super().__init__(icon_span, **attrs)