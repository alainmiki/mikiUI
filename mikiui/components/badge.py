"""Badge component for status labels and small indicators."""

from __future__ import annotations

from typing import Any

from .base import Component


class Badge(Component):
    """A small status badge / label.

    :param text:  Badge text content.
    :param variant: ``"default"``, ``"primary"``, ``"success"``, ``"warning"``,
                    ``"error"``, or ``"ghost"``.
    :param size:  ``"sm"`` or ``"md"`` (default).
    :param attrs: Extra HTML attributes.
    """

    tag = "span"

    def __init__(
        self,
        text: str,
        *,
        variant: str = "default",
        size: str = "md",
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        classes = f"miki-badge miki-badge-{variant} miki-badge-{size}"
        if class_:
            classes += f" {class_}"
        attrs.setdefault("class_", classes)
        attrs.setdefault("role", "status")

        super().__init__(text, **attrs)
