"""Dashboard widget: a responsive grid of cards."""

from __future__ import annotations

from typing import Any

from ..components import Div
from ..components.base import Component


class Dashboard(Component):
    """Render a responsive grid of card ``Div``s.

    :param cards: arbitrary child content, each wrapped in a card.
    :param columns: number of columns in the grid.
    """

    tag = "div"

    def __init__(self, *cards: Any, columns: int = 3, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-dashboard")
        attrs.setdefault("data-miki-dashboard", "true")
        attrs.setdefault("touch-action", "manipulation")
        attrs.setdefault("role", "region")
        attrs.setdefault("aria_label", "Dashboard")
        attrs.setdefault("tabindex", "0")
        attrs.setdefault(
            "style",
            {
                "display": "grid",
                "grid-template-columns": f"repeat({columns}, 1fr)",
                "gap": "1rem",
            },
        )
        card_nodes = [
            Div(card, class_="miki-dashboard-card", role="group") for card in cards
        ]
        super().__init__(*card_nodes, **attrs)
