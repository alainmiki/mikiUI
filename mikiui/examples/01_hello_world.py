"""01_hello_world.py — Greeting card with time-of-day awareness and stats.

Run with: mikiui dev --app mikiui.examples.01_hello_world:app
"""

from __future__ import annotations

from datetime import datetime

from mikiui import (
    Div,
    Footer,
    MikiApp,
    P,
)
from mikiui.components import Button
from mikiui.themes import Theme
from mikiui.widgets import Badge, Card
from mikiui.widgets.layout_widgets import Hero

app = MikiApp(
    title="MikiUI — Hello World",
    lang="en",
)

app.register_theme(Theme(
    name="hello",
    source="custom",
    framework="css",
    variables={
        "--miki-bg": "#f8fafc",
        "--miki-fg": "#0f172a",
        "--miki-accent": "#6366f1",
    },
    extra_classes=["miki-theme-hello"],
))


def _greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


@app.route("/")
def home() -> Div:
    """Return a greeting card with stats and a footer."""
    user = "Miki"
    greeting = _greeting()

    stats = [
        ("Visitors today", "12,482", "+14.2%", "success"),
        ("Active sessions", "384", "+5.1%", "success"),
        ("Bounce rate", "24.3%", "-2.4%", "warning"),
        ("Server uptime", "99.97%", "stable", "success"),
    ]

    stat_cards = []
    for title, value, change, level in stats:
        stat_cards.append(
            Card(
                P(value, class_="text-3xl font-bold text-slate-800"),
                P(title, class_="text-sm text-slate-500 mt-1"),
                Badge(change, variant=level, size="sm"),
                class_="p-5",
                variant="default",
            )
        )

    return Div(
        Hero(
            _greeting() + ", " + user,
            subtitle="Welcome back. Here's what's happening across your projects today.",
            action=Div(
                Button("View Analytics", variant="primary", class_="mr-3"),
                Button("Settings", variant="secondary"),
                class_="flex gap-3 mt-2",
            ),
        ),
        Div(
            Div(
                P("Performance Overview", class_="text-lg font-semibold text-slate-700 mb-4"),
                Div(*stat_cards, class_="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"),
                class_="max-w-6xl mx-auto",
            ),
            class_="py-10",
        ),
        Footer(
            copyright="© 2026 MikiUI Framework",
            social=[
                ("GitHub", "https://github.com/mikiui"),
                ("Docs", "https://mikiui.dev"),
                ("Twitter", "https://twitter.com/mikiui"),
            ],
        ),
        class_="min-h-screen flex flex-col",
    )


if __name__ == "__main__":
    app.run()
