"""ListView component (scrollable selectable list)."""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import Div, Ul


class ListView(Component):
    """A scrollable list with selectable items.

    ``items`` is a list of labels. ``selected`` (index or set of indices)
    marks initial selection.  Selection can be wired client-side via Alpine
    or server-side via HTMX ``hx_get`` attributes.

    Pass ``class_`` for additional CSS classes.
    """

    tag = "ul"

    def __init__(
        self,
        items: list[Any],
        selected: int | set[int] | None = None,
        **attrs: Any,
    ) -> None:
        user_class = attrs.pop("class_", "")
        attrs["class_"] = f"miki-listview {user_class}".strip()
        attrs.setdefault("role", "list")
        if selected is None:
            selected = set()
        elif isinstance(selected, int):
            selected = {selected}
        rendered = [
            Div(
                item,
                role="listitem",
                **({"aria-selected": "true"} if i in selected else {}),
            )
            for i, item in enumerate(items)
        ]
        super().__init__(*rendered, **attrs)
