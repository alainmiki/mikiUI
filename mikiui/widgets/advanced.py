"""Advanced interactive widgets: wizards, search, streaming, notifications."""

from __future__ import annotations

import uuid
from typing import Any

from ..components import (
    Button,
    Div,
    Form,
    Input,
    Li,
    Ol,
    Span,
    SubmitButton,
)
from ..components.base import Component
from ..engine import _


class FormWizard(Component):
    """A multi-step form wizard.

    Renders a step indicator (ordered list of step titles), the content of the
    current step, and Back/Next buttons. Switching steps is handled with plain
    inline JavaScript so it works fully offline.

    :param steps: a list of ``(title, content)`` pairs.
    :param current: the zero-based index of the step shown initially.
    """

    tag = "div"

    def __init__(
        self, steps: list[tuple[str, Any]], current: int = 0, **attrs: Any
    ) -> None:
        attrs.setdefault("class", "miki-wizard")
        group = "miki-wizard-" + uuid.uuid4().hex[:8]

        indicator_items = []
        step_panels = []
        for i, (title, content) in enumerate(steps):
            indicator_items.append(
                Li(
                    title,
                    class_="miki-wizard-step" + (" active" if i == current else ""),
                    **({"aria_current": "step"} if i == current else {}),
                )
            )
            step_panels.append(
                Div(
                    content,
                    id=f"{group}-step-{i}",
                    role="tabpanel",
                    **({"style": "display:none"} if i != current else {}),
                )
            )

        indicator = Ol(
            *indicator_items,
            id=f"{group}-indicator",
            class_="miki-wizard-indicator",
        )

        def js_show(idx: int) -> str:
            return (
                "var ps=document.getElementById('" + group + "-steps').children;"
                "for(var i=0;i<ps.length;i++){ps[i].style.display=(i===" + str(idx)
                + ")?'block':'none';}"
                "var ind=document.getElementById('" + group
                + "-indicator').children;"
                "for(var i=0;i<ind.length;i++){"
                "ind[i].classList.toggle('active',i===" + str(idx) + ");}"
            )

        nav = Div(
            Button(
                _("wizard_back", "Back"),
                type="button",
                class_="miki-wizard-back",
                disabled=(current == 0),
                onclick=js_show(max(0, current - 1)),
            ),
            Button(
                _("wizard_next", "Next"),
                type="button",
                class_="miki-wizard-next",
                disabled=(current >= len(steps) - 1),
                onclick=js_show(min(len(steps) - 1, current + 1)),
            ),
            class_="miki-wizard-nav",
        )

        steps_wrap = Div(*step_panels, id=f"{group}-steps", class_="miki-wizard-steps")
        super().__init__(indicator, steps_wrap, nav, **attrs)


class SearchPanel(Component):
    """A search box with a results region.

    Renders a :class:`Form` containing a text ``Input(name="q")`` and a
    ``SubmitButton``. A results ``Div`` (``id="search-results"``) is included so
    the backend can target it via HTMX swaps.

    :param placeholder: placeholder text for the search input.
    :param on_search: optional HTMX route (``hx-post``) to receive the query.
    """

    tag = "div"

    def __init__(
        self, placeholder: str = "Search...", on_search: str | None = None, **attrs: Any
    ) -> None:
        attrs.setdefault("class", "miki-searchpanel")
        form_attrs: dict[str, Any] = {"role": "search", "class_": "miki-search-form"}
        if on_search:
            form_attrs["hx_post"] = on_search
            form_attrs["hx_target"] = "#search-results"
        form = Form(
            Input(
                type="text",
                name="q",
                placeholder=placeholder,
                aria_label=_("search_label", "Search"),
            ),
            SubmitButton(_("search_button", "Search")),
            **form_attrs,
        )
        results = Div(id="search-results", class_="miki-search-results", role="region")
        super().__init__(form, results, **attrs)


class StreamingPanel(Component):
    """A live/streaming log panel.

    Renders a :class:`Section` with a scrollable log area (``id`` provided for
    streaming updates) and a status indicator ``Span``.

    :param title: panel heading.
    """

    tag = "section"

    def __init__(self, title: str = "Live", **attrs: Any) -> None:
        attrs.setdefault("class", "miki-streamingpanel")
        attrs.setdefault("aria_label", title)
        heading = Div(title, class_="miki-streaming-title")
        log = Div(
            id="streaming-log",
            class_="miki-streaming-log",
            role="log",
            aria_live="polite",
        )
        status = Span(
            _("streaming_idle", "Idle"),
            class_="miki-streaming-status",
            role="status",
        )
        super().__init__(heading, log, status, **attrs)


class NotificationPanel(Component):
    """A container for transient toast notifications.

    The container has ``role="log"`` and ``aria-live="polite"`` so screen
    readers announce new toasts. Use :meth:`toast` to build individual toasts.
    """

    tag = "div"

    def __init__(self, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-notificationpanel")
        attrs.setdefault("role", "log")
        attrs.setdefault("aria_live", "polite")
        super().__init__(**attrs)

    def toast(self, text: str, level: str = "info") -> Component:
        """Build a toast ``Div`` for the given ``text`` and severity ``level``."""
        return Div(
            text,
            class_="miki-toast miki-toast-" + level,
            role="status",
        )
