"""Tooltip component using native title plus a data attribute hook."""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import Span
from ..engine import _


class Tooltip(Component):
    """Wrap ``text`` in a ``<span>`` with a native ``title`` tooltip.

    The ``tip`` is also exposed via ``data-tooltip`` for custom styling.
    """

    def __init__(self, text: str, tip: str, **attrs: Any) -> None:
        attrs.setdefault("title", tip)
        attrs["data_tooltip"] = tip
        super().__init__(_(text, text), **attrs)
