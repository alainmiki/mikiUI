"""SplitView widget: two panes laid out horizontally or vertically."""

from __future__ import annotations

from typing import Any

from ..components import Div
from ..components.base import Component


class SplitView(Component):
    """Render two child panes in a flex container.

    :param left: content for the first pane.
    :param right: content for the second pane.
    :param orientation: ``"horizontal"`` (side-by-side) or ``"vertical"``.
    """

    tag = "div"

    def __init__(
        self, left: Any, right: Any, orientation: str = "horizontal", **attrs: Any
    ) -> None:
        attrs.setdefault("class", "miki-splitview")
        direction = "row" if orientation == "horizontal" else "column"
        attrs.setdefault(
            "style", {"display": "flex", "flex-direction": direction, "gap": "0.5rem"}
        )
        left_pane = Div(left, class_="miki-split-pane", role="group")
        right_pane = Div(right, class_="miki-split-pane", role="group")
        super().__init__(left_pane, right_pane, **attrs)
