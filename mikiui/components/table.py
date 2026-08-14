"""Table components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Table(Component):
    tag = "table"


class Caption(Component):
    tag = "caption"


class Thead(Component):
    tag = "thead"


class Tbody(Component):
    tag = "tbody"


class Tfoot(Component):
    tag = "tfoot"


class Tr(Component):
    tag = "tr"


class Th(Component):
    tag = "th"


class Td(Component):
    tag = "td"
