"""IDEEditor widget: a simple code editor with a line-number gutter."""

from __future__ import annotations

from typing import Any

from ..components import Div, Pre, Textarea
from ..components.base import Component


class IDEEditor(Component):
    """Render a lightweight code editor with a gutter and a textarea.

    :param content: initial editor text.
    :param language: language label (used as a class hint).
    """

    tag = "div"

    def __init__(
        self, content: str = "", language: str = "python", **attrs: Any
    ) -> None:
        attrs.setdefault("class", f"miki-ide miki-ide-{language}")
        attrs.setdefault("role", "group")
        attrs.setdefault("aria_label", f"{language} editor")

        lines = content.splitlines() or [""]
        gutter = Pre(
            "\n".join(str(i + 1) for i in range(len(lines))),
            class_="miki-ide-gutter",
            aria_hidden="true",
        )
        editor = Textarea(content, class_="miki-ide-area", spellcheck="false")
        body = Div(gutter, editor, class_="miki-ide-body")
        super().__init__(body, **attrs)
