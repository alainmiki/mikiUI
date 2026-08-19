"""KanbanBoard widget: columns of item lists."""

from __future__ import annotations

from typing import Any

from ..components import H3, Div
from ..components.base import Component


class KanbanBoard(Component):
    """Render a kanban board from a mapping of column -> items.

    :param columns: dict mapping column title to a list of item labels.
    """

    tag = "div"

    def __init__(self, columns: dict[str, list], **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-kanban")
        attrs.setdefault("role", "list")
        attrs.setdefault("data-miki-kanban", "true")
        column_nodes = []
        for title, items in columns.items():
            item_nodes = []
            for item in items:
                item_nodes.append(
                    Div(
                        item,
                        class_="miki-kanban-item",
                        role="listitem",
                        draggable="true",
                        **{"data-sort-item": "true", "data-miki-kanban-item": "true"}
                    )
                )
            column_nodes.append(
                Div(
                    H3(title, class_="miki-kanban-column-header"),
                    *item_nodes,
                    class_="miki-kanban-column",
                    role="group",
                    aria_label=title,
                    **{"data-miki-kanban-column": "true"}
                )
            )
        super().__init__(*column_nodes, **attrs)
