"""07_themes.py — Theme studio with live switcher and custom creator.

Demonstrates built-in theme switching, custom theme registration,
preview cards, and a simulated export/import flow.

Run with: mikiui dev --app mikiui.examples.07_themes:app
"""

from __future__ import annotations

import json

from mikiui import Div, H1, H2, H3, MikiApp, P, register_theme
from mikiui.components import Button, Input, Label, Navbar, Select
from mikiui.components.form import Option
from mikiui.themes import Theme

app = MikiApp(title="Theme Studio", lang="en")

BUILTIN_THEMES = ["light", "dark", "dracula", "solarized-dark", "nord", "monokai"]


def _preview_card(title: str, description: str) -> Div:
    return Div(
        Div(
            H3(title, class_="font-semibold text-slate-800 mb-1"),
            P(description, class_="text-sm text-slate-500"),
            class_="p-4",
        ),
        class_="rounded-lg border border-slate-200 bg-white shadow-sm",
    )


@app.route("/")
def home() -> Div:
    theme_options = []
    for name in BUILTIN_THEMES:
        theme_options.append(Option(name.replace("-", " ").title(), value=name))

    return Div(
        Navbar(brand="Theme Studio", links=[("Home", "/"), ("Create", "/create"), ("Export", "/export")], dark=True),
        Div(
            Div(
                H1("Theme Studio", class_="text-4xl font-extrabold text-slate-900 mb-2"),
                P("Explore built-in themes and preview components in real time.", class_="text-lg text-slate-600 mb-8"),
                Div(
                    Label("Active Theme", for_="theme-select", class_="block text-sm font-medium text-slate-700 mb-2"),
                    Select(
                        *theme_options,
                        id="theme-select",
                        name="theme",
                        class_="rounded border-slate-300",
                    ),
                    Div(
                        Button("Apply", variant="primary", hx_post="/api/theme/apply", hx_target="#preview-grid", hx_swap="innerHTML"),
                        class_="mt-4",
                    ),
                    class_="max-w-xs",
                ),
                class_="mb-12",
            ),
            Div(
                H2("Preview Cards", class_="text-2xl font-bold text-slate-800 mb-6"),
                Div(
                    _preview_card("Typography", "Headings, paragraphs, and inline text render with theme-aware colors."),
                    _preview_card("Forms", "Inputs, selects, and buttons reflect the active palette."),
                    _preview_card("Data", "Tables, badges, and progress bars inherit semantic colors."),
                    _preview_card("Navigation", "Navbar, breadcrumbs, and tabs use the primary accent."),
                    id="preview-grid",
                    class_="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",
                ),
                class_="mb-12",
            ),
            Div(
                H2("Theme JSON", class_="text-2xl font-bold text-slate-800 mb-4"),
                P("Inspect the active theme variables and CSS classes below.", class_="text-slate-600 mb-4"),
                Div(
                    P("Theme variables render here after applying a theme.", class_="text-sm text-slate-500"),
                    id="theme-json",
                    class_="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-sm overflow-x-auto",
                ),
                class_="max-w-2xl",
            ),
            class_="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12",
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/api/theme/apply", methods=["POST"])
async def apply_theme(ctx) -> Div:
    data = await ctx.form()
    theme_name = data.get("theme", "light")
    try:
        app.set_theme(theme_name)
        theme = app.theme_registry.get_active()
        variables = dict(theme.variables) if theme else {}
        json_str = json.dumps(variables, indent=2)
        return Div(
            _preview_card("Typography", "Headings, paragraphs, and inline text render with theme-aware colors."),
            _preview_card("Forms", "Inputs, selects, and buttons reflect the active palette."),
            _preview_card("Data", "Tables, badges, and progress bars inherit semantic colors."),
            _preview_card("Navigation", "Navbar, breadcrumbs, and tabs use the primary accent."),
            class_="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4",
        ), Div(
            P(f'<pre class="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-sm overflow-x-auto">{json_str}</pre>', class_=""),
            id="theme-json",
            class_="max-w-2xl",
        )
    except Exception as exc:
        return Div(P(f"Error: {exc}", class_="text-red-600"), class_="text-red-600")


@app.route("/create")
def create() -> Div:
    return Div(
        Navbar(brand="Theme Studio", links=[("Home", "/"), ("Create", "/create"), ("Export", "/export")]),
        Div(
            H1("Create Custom Theme", class_="text-3xl font-bold text-slate-900 mb-2"),
            P("Pick colors and preview a live theme.", class_="text-slate-600 mb-8"),
            Div(
                Div(
                    Label("Theme Name", for_="custom-name", class_="block text-sm font-medium text-slate-700 mb-1"),
                    Input(type="text", id="custom-name", name="name", placeholder="Midnight Ocean", class_="w-full rounded border-slate-300 mb-4"),
                    Label("Background", for_="custom-bg", class_="block text-sm font-medium text-slate-700 mb-1"),
                    Input(type="color", id="custom-bg", name="bg", value="#0f172a", class_="w-full h-10 rounded border-slate-300 mb-4"),
                    Label("Foreground", for_="custom-fg", class_="block text-sm font-medium text-slate-700 mb-1"),
                    Input(type="color", id="custom-fg", name="fg", value="#e2e8f0", class_="w-full h-10 rounded border-slate-300 mb-4"),
                    Label("Accent", for_="custom-accent", class_="block text-sm font-medium text-slate-700 mb-1"),
                    Input(type="color", id="custom-accent", name="accent", value="#6366f1", class_="w-full h-10 rounded border-slate-300 mb-6"),
                    Button("Save Theme", variant="primary", hx_post="/api/theme/create", hx_target="#create-result", hx_swap="innerHTML"),
                    class_="max-w-sm",
                ),
                Div(id="create-result", class_="mt-6"),
                class_="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12",
            ),
            class_="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12",
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/api/theme/create", methods=["POST"])
async def create_theme(ctx) -> Div:
    data = await ctx.form()
    name = data.get("name", "custom").strip().lower().replace(" ", "-")
    bg = data.get("bg", "#0f172a")
    fg = data.get("fg", "#e2e8f0")
    accent = data.get("accent", "#6366f1")

    theme = Theme(
        name=name,
        source="custom",
        framework="css",
        variables={
            "--miki-bg": bg,
            "--miki-fg": fg,
            "--miki-accent": accent,
        },
        extra_classes=[f"miki-theme-{name}"],
    )
    register_theme(theme)
    app.set_theme(name)

    return Div(
        P(f"Theme '{name}' saved and activated.", class_="text-emerald-600 font-semibold"),
        P(f"Variables: bg={bg}, fg={fg}, accent={accent}", class_="text-slate-600 text-sm mt-1"),
        class_="p-4 border border-emerald-200 rounded-lg bg-emerald-50",
    )


@app.route("/export")
def export_theme() -> Div:
    theme = app.theme_registry.get_active()
    variables = dict(theme.variables) if theme else {}
    payload = json.dumps({
        "name": theme.name if theme else "unknown",
        "variables": variables,
        "exported_at": "2026-08-16T01:50:00+01:00",
    }, indent=2)

    return Div(
        Navbar(brand="Theme Studio", links=[("Home", "/"), ("Create", "/create"), ("Export", "/export")]),
        Div(
            H1("Export Theme", class_="text-3xl font-bold text-slate-900 mb-2"),
            P("Download or copy the current theme configuration.", class_="text-slate-600 mb-8"),
            Div(
                P(payload, class_="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-sm overflow-x-auto whitespace-pre"),
                class_="max-w-2xl",
            ),
            Div(
                Button("Copy to Clipboard", variant="secondary", hx_post="/api/theme/copy", hx_target="#copy-result", hx_swap="innerHTML"),
                Div(id="copy-result", class_="mt-3"),
                class_="max-w-2xl mt-4",
            ),
            class_="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12",
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/api/theme/copy", methods=["POST"])
async def copy_theme(ctx) -> Div:
    return Div(P("Theme JSON copied to clipboard.", class_="text-emerald-600"), class_="text-sm")


if __name__ == "__main__":
    app.run(desktop=True)
