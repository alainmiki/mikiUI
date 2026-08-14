"""Demo MikiUI app used by `mikiui dev` / `mikiui desktop` and the tests.

Demonstrates routing, server-side state, an HTMX partial update (counter),
and a range of components so the desktop window is a real showcase.
"""

from __future__ import annotations

from mikiui import MikiApp, Div, H1, P, A, Button, Span
from mikiui.components import (
    Dialog,
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    Input,
    Form,
    SubmitButton,
    Tabs,
    Ul,
    Li,
)


app = MikiApp(title="MikiUI Demo")


@app.route("/")
def home(ctx):
    count = ctx.app.state.get("count", 0)
    return Div(
        Div(
            H1("MikiUI Demo"),
            P("A Python-first UI framework. Click the button for a live partial update."),
            P(f"Server count: {count}", id="count", style="font-weight:600"),
            Button(
                "Increment",
                hx_post="/increment",
                hx_target="#count",
                hx_swap="outerHTML",
            ),
            " ",
            Button(
                "Open Dialog",
                onclick="document.querySelector('dialog').showModal()",
            ),
            Dialog(
                Div(
                    H1("About"),
                    P("MikiUI renders Python component trees to HTML."),
                    Button("Close", onclick="this.closest('dialog').close()"),
                )
            ),
            A("About page", href="/about"),
            style="display:flex;gap:.5rem;flex-wrap:wrap;align-items:center",
        ),
        Div(
            H1("Components"),
            Table(
                Thead(Tr(Th("Name"), Th("Role"))),
                Tbody(
                    Tr(Td("Button"), Td("Trigger actions / HTMX")),
                    Tr(Td("Table"), Td("Tabular data")),
                    Tr(Td("Tabs"), Td("Switchable panels")),
                    Tr(Td("Dialog"), Td("Modals / popovers")),
                ),
            ),
            Tabs(
                [
                    ("Overview", P("MikiUI maps Python classes to HTML elements.")),
                    ("State", P("Shared server-side state powers interactions.")),
                    ("Runtime", P("HTMX + Alpine.js drive partial updates.")),
                ]
            ),
            class_="miki-container",
        ),
    )


@app.post("/increment")
def increment(ctx):
    ctx.app.state["count"] = ctx.app.state.get("count", 0) + 1
    return P(f"Server count: {ctx.app.state['count']}", id="count", style="font-weight:600")


@app.route("/about")
def about(ctx):
    return Div(
        Div(
            H1("About"),
            P("MikiUI renders Python component trees to HTML and can run as a "
              "website or a standalone desktop window."),
            A("Home", href="/"),
            class_="miki-container",
        )
    )
