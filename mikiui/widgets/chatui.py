"""ChatUI widget: a scrollable chat log with a message input form."""

from __future__ import annotations

from typing import Any

from ..components import Div, Form, Input, SubmitButton
from ..components.base import Component


class ChatUI(Component):
    """Render a chat interface from a list of messages.

    :param messages: list of ``{"role": "user"|"bot", "text": str}`` dicts.
    """

    tag = "div"

    def __init__(self, messages: list[dict], **attrs: Any) -> None:
        attrs.setdefault("class", "miki-chat")
        attrs.setdefault("role", "log")
        attrs.setdefault("aria_live", "polite")
        attrs.setdefault("data-miki-chat", "true")

        bubbles = []
        for msg in messages:
            role = msg.get("role", "user")
            text = msg.get("text", "")
            cls = (
                "miki-chat-msg miki-chat-user"
                if role == "user"
                else "miki-chat-msg miki-chat-bot"
            )
            bubbles.append(Div(text, class_=cls, role="listitem"))

        log = Div(*bubbles, class_="miki-chat-log", role="list")
        typing = Div(class_="miki-chat-typing", aria_label="Bot is typing")
        form = Form(
            typing,
            Input(name="message", placeholder="Type a message..."),
            SubmitButton("Send"),
            class_="miki-chat-form",
            **{"data-miki-chat-form": "true"}
        )
        super().__init__(log, form, **attrs)
