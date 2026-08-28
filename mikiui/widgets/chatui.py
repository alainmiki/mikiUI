"""ChatUI widget: a scrollable chat log with a message input form."""

from __future__ import annotations

from typing import Any

from ..components import Div, Form, Span, SubmitButton, Textarea
from ..components.base import Component


class ChatUI(Component):
    """Render a chat interface from a list of messages.

    Each message dict may contain:
    - ``role``: ``"user"`` or ``"bot"`` (default ``"user"``).
    - ``text``: message body.
    - ``avatar``: optional avatar text/URL/HTML.
    - ``time``: optional timestamp string.

    :param messages: list of message dicts.
    :param multiline: if True, uses a textarea (Shift+Enter for newline).
    :param placeholder: input placeholder text.
    :param chat_id: optional DOM id for the chat container.
    """

    tag = "div"

    def __init__(
        self,
        messages: list[dict[str, Any]],
        multiline: bool = False,
        placeholder: str = "Type a message...",
        chat_id: str | None = None,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-chat")
        attrs.setdefault("role", "log")
        attrs.setdefault("aria_label", "Chat conversation")
        attrs.setdefault("aria_live", "polite")
        attrs.setdefault("data-miki-chat", "true")
        attrs.setdefault("tabindex", "0")
        if chat_id:
            attrs["id"] = chat_id

        bubbles = []
        for msg in messages:
            role = "user" if msg.get("role") == "user" else "bot"
            text = msg.get("text", "")
            avatar = msg.get("avatar")
            time_str = msg.get("time")

            parts: list[Any] = []
            if avatar is not None:
                if isinstance(avatar, str) and (
                    avatar.startswith(("http", "/", "data:"))
                ):
                    from ..components import Img
                    parts.append(
                        Div(Img(src=avatar, alt=f"{role} avatar", class_="miki-chat-avatar-img"),
                            class_="miki-chat-avatar")
                    )
                else:
                    parts.append(Div(str(avatar), class_="miki-chat-avatar"))

            body_parts: list[Any] = [Div(text, class_="miki-chat-text")]
            if time_str:
                body_parts.append(Div(str(time_str), class_="miki-chat-time"))
            parts.append(Div(*body_parts, class_="miki-chat-bubble-body"))

            bubbles.append(
                Div(*parts, class_=f"miki-chat-msg miki-chat-{role}", role="listitem")
            )

        log = Div(*bubbles, class_="miki-chat-log", role="list")
        typing = Div(
            Span(class_="miki-chat-typing-dot"),
            Span(class_="miki-chat-typing-dot"),
            Span(class_="miki-chat-typing-dot"),
            class_="miki-chat-typing",
            aria_label="Bot is typing",
            style="display:none",
        )
        input_cls = "miki-chat-input"
        if multiline:
            msg_input: Any = Textarea(
                name="message",
                placeholder=placeholder,
                aria_label="Message input",
                class_=input_cls,
                rows=1,
            )
        else:
            from ..components import Input
            msg_input = Input(
                name="message",
                placeholder=placeholder,
                aria_label="Message input",
                class_=input_cls,
            )
        form_attrs: dict[str, Any] = {"class_": "miki-chat-form"}
        form_attrs["data-miki-chat-form"] = "true"
        form = Form(
            typing,
            msg_input,
            SubmitButton("Send", aria_label="Send message"),
            **form_attrs,
        )
        super().__init__(log, form, **attrs)
