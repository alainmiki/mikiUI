"""IDEEditor widget: a lightweight code editor with a line-number gutter."""

from __future__ import annotations

from typing import Any

from ..components import Div, Pre, Textarea
from ..components.base import Component


class IDEEditor(Component):
    """Render a lightweight code editor with a gutter and a textarea.

    :param content: initial editor text.
    :param language: language label (used as a class hint).
    :param tab_size: number of spaces inserted on Tab (default 4).
    :param line_numbers: show the line-number gutter (default True).
    :param readonly: make the editor read-only.
    :param placeholder: placeholder text shown when empty.
    :param editor_id: optional DOM id for the editor container.
    """

    tag = "div"

    def __init__(
        self,
        content: str = "",
        language: str = "python",
        tab_size: int = 4,
        line_numbers: bool = True,
        readonly: bool = False,
        placeholder: str = "",
        editor_id: str | None = None,
        **attrs: Any,
    ) -> None:
        tab_size = max(1, min(tab_size, 16))
        attrs.setdefault("class_", f"miki-ide miki-ide-{language}")
        attrs.setdefault("role", "group")
        attrs.setdefault("aria-label", f"{language} editor")
        attrs.setdefault("data-miki-editor", "true")
        attrs.setdefault("data-tab-size", str(tab_size))
        if editor_id:
            attrs["id"] = editor_id

        lines = content.splitlines() or [""]
        gutter = Pre(
            "\n".join(str(i + 1) for i in range(len(lines))),
            class_="miki-ide-gutter",
            aria_hidden="true",
            **({"style": "display:none"} if not line_numbers else {}),
        )
        textarea_attrs: dict[str, Any] = {
            "class_": "miki-ide-area",
            "spellcheck": "false",
            "aria_label": f"{language} editor",
        }
        if readonly:
            textarea_attrs["readonly"] = True
        if placeholder:
            textarea_attrs["placeholder"] = placeholder
        editor = Textarea(content, **textarea_attrs)
        body = Div(gutter, editor, class_="miki-ide-body")
        super().__init__(body, **attrs)
