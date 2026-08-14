"""TreeView component (hierarchical list)."""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import Ul, Li, Span
from .dialog import Details, Summary


class TreeView(Component):
    """A hierarchical, expandable tree.

    ``nodes`` is a list of ``(label, children)`` where ``children`` is a
    recursive list or ``None``. Leaves render as plain items; branches use
    ``<details>`` for native disclosure.
    """

    tag = "div"
    role = "tree"

    def __init__(self, nodes: list[tuple[Any, Any]], **attrs: Any) -> None:
        attrs.setdefault("role", "tree")
        super().__init__(self._build(nodes), **attrs)

    def _build(self, nodes: list[tuple[Any, Any]]) -> Ul:
        items = []
        for label, children in nodes:
            if children:
                branch = Details(
                    Summary(label),
                    self._build(children),
                    role="treeitem",
                )
                items.append(Li(branch))
            else:
                items.append(Li(Span(label), role="treeitem"))
        return Ul(*items)
