"""Breadcrumbs navigation component."""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import A, Li, Nav, Ol


class Breadcrumbs(Component):
    """Accessible breadcrumb trail.

    ``items`` is a list of ``(href, label)`` pairs. Every item but the last is
    rendered as a link; the final item is plain text (current page).
    """

    def __init__(self, items: list[tuple[str, str]], **attrs: Any) -> None:
        lis = []
        for i, (href, label) in enumerate(items):
            if i < len(items) - 1:
                lis.append(Li(A(label, href=href)))
            else:
                lis.append(Li(label))
        super().__init__(Nav(Ol(*lis), aria_label="breadcrumb"), **attrs)
