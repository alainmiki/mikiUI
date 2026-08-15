"""Accordion component built from native disclosure elements."""

from __future__ import annotations

from typing import Any

from .base import Component
from .dialog import Details, Summary
from .html import Div, Span
from ..engine import _


class Accordion(Component):
    """Stacked ``<details>`` items in a ``role="list"`` container.

    ``items`` is a list of ``(title, content)`` pairs. Each pair renders as a
    native ``<details><summary>title</summary>content</details>``.
    """

    def __init__(self, items: list[tuple[str, Any]], **attrs: Any) -> None:
        entries = []
        for title, content in items:
            entries.append(
                Details(
                    Summary(_("accordion_summary", title)),
                    content,
                )
            )
        user_class = attrs.pop("class_", "")
        attrs["class_"] = f"miki-accordion {user_class}".strip()
        super().__init__(Div(*entries, role="list"), **attrs)
