"""Calendar component (date picker + simple event list)."""

from __future__ import annotations

from typing import Any

from datetime import date

from .base import Component
from .html import Div
from .table import Table, Tr, Thead, Tbody, Th, Td, Caption


class Calendar(Component):
    """A minimal month-grid calendar.

    ``year``/``month`` select the displayed month (1-12). ``events`` maps
    ``day -> label`` to annotate specific days.
    """

    tag = "div"

    def __init__(
        self,
        year: int | None = None,
        month: int | None = None,
        events: dict[int, str] | None = None,
        **attrs: Any,
    ) -> None:
        today = date.today()
        year = year or today.year
        month = month or today.month
        events = events or {}
        attrs.setdefault("role", "grid")
        attrs.setdefault("class", "miki-calendar")
        first = date(year, month, 1)
        # Number of days in the month (handles leap years).
        if month == 12:
            ndays = 31
        else:
            ndays = (date(year, month + 1, 1) - first).days
        start_weekday = first.weekday()
        cells: list[Component] = []
        for _ in range(start_weekday):
            cells.append(Td(""))
        for day in range(1, ndays + 1):
            label = events.get(day, str(day))
            cells.append(Td(label, **({"title": events[day]} if day in events else {})))
        rows = []
        for i in range(0, len(cells), 7):
            rows.append(Tr(*cells[i : i + 7]))
        grid = Table(
            Caption(first.strftime("%B %Y")),
            Thead(Tr(*(Th(d) for d in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")))),
            Tbody(*rows),
        )
        super().__init__(Div(grid), **attrs)
