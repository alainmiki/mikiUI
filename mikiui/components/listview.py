"""ListView component (scrollable selectable list)."""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import Ul, Li


class ListView(Component):
    """A scrollable list with selectable items.

    ``items`` is a list of labels. ``selected`` (index or set of indices)
    marks initial selection. Selection is wired client-side via Alpine.
    """

    tag = "div"

    def __init__(
        self,
        items: list[Any],
        selected: int | set[int] | None = None,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("role", "listbox")
        attrs.setdefault("class", "miki-listview")
        if selected is None:
            selected = set()
        elif isinstance(selected, int):
            selected = {selected}
        rendered = [
            Li(
                item,
                role="option",
                **({"aria-selected": "true"} if i in selected else {}),
            )
            for i, item in enumerate(items)
        ]
        super().__init__(Ul(*rendered), **attrs)
