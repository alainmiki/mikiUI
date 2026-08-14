"""TerminalWidget: a monospace terminal-style output block."""

from __future__ import annotations

from typing import Any

from ..components import Pre
from ..components.base import Component


class TerminalWidget(Component):
    """Render terminal output lines in a monospace block.

    :param lines: a list of lines, or a single string with newlines.
    """

    tag = "pre"

    def __init__(self, lines: list[str] | str = "", **attrs: Any) -> None:
        attrs.setdefault("class", "miki-terminal")
        attrs.setdefault("role", "log")
        attrs.setdefault("aria_live", "polite")
        if isinstance(lines, str):
            text = lines
        else:
            text = "\n".join(lines)
        super().__init__(text, **attrs)
