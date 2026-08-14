"""Demo MikiUI app showcasing all components and widgets.

Run with: mikiui dev --app mikiui.examples.demo:app

This demo covers:
- All base HTML components (buttons, forms, tables, dialogs, etc.)
- All widgets (DataGrid, SplitView, DockablePanel, Card, Carousel, etc.)
- Layout patterns (Navbar, Sidebar, Footer, Drawer, Hero, etc.)
- Icon system (28 built-in SVG icons)
- HTMX partial updates
- Theme switching (tailwind, bootstrap, dark, light)
"""

from __future__ import annotations

from mikiui import MikiApp, Div, H1, H2, P, Button, A, H3
from mikiui.components import Navbar, Form, Label, Input, SubmitButton
from mikiui.widgets import (
    # Data widgets
    DataGrid, TabbedPanel, CollapsiblePanel, MessageBox, ProgressDialog,
    DockablePanel, SplitView, ScrollPanel, GroupBox,
    ColorPicker, DatePicker, Dial, LCDNumber,
    # Layout widgets
    Hero, Footer, Sidebar, Drawer, Rail, ContextWindow,
    # Advanced widgets
    Card, Carousel, Pagination, Avatar, Badge, Progress as ProgressBar,
    # Icon system
    Icon, IconSet,
    # Editor & media
    IDEEditor,
)
from mikiui.widgets import LogViewer
from mikiui.components import Chart

app = MikiApp(title="MikiUI Demo App")
app.set_theme("dark")


@app.route("/")
def home(ctx):
    """Home page with quick navigation."""
    count = ctx.app.state.get("count", 0)
    return Div(
        Navbar(
            brand="MikiUI Demo",
            links=[
                ("Home", "/"),
                ("Layout", "/layout"),
                ("Cards", "/cards"),
                ("Forms", "/forms"),
                ("Data", "/data"),
                ("Icons", "/icons"),
            ],
            sticky=True, dark=True,
            right=Button("Login", variant="ghost"),
        ),
        Hero(
            "MikiUI Demo",
            subtitle="Python-first UI framework showcasing all widgets",
            action=Button("Get Started", variant="primary", hx_get="/layout"),
        ),
        Div(
            P(f"Counter: {count}", id="count", class_="font-bold"),
            Button("Increment", hx_post="/increment", hx_target="#count", hx_swap="outerHTML"),
            class_="flex gap-2 items-center mt-4",
        ),
    )


@app.route("/layout")
def layout_demo():
    """Showcase Navbar, Hero, Sidebar, Footer, Drawer, Rail, ContextWindow."""
    return Div(
        Navbar(
            brand="MikiUI",
            links=[("Home", "/")],
            sticky=True, dark=True,
            right=Button("Login", variant="ghost"),
        ),
        Hero(
            "Build Beautiful UIs",
            subtitle="Python-first UI framework with Tailwind, Bootstrap, and DaisyUI support.",
            action=Button("Get Started", variant="primary"),
        ),
        Div(
            Sidebar(
                ("Dashboard", "/"),
                ("Components", "/components"),
                ("Forms", "/forms"),
                ("Tables", "/tables"),
                title="Navigation",
            ),
            Div(
                Card("Content card body", title="Card Title", footer="Footer content"),
                Card(
                    Icon("home", size=48),
                    title="Icon Example",
                ),
                Pagination(current=3, total=10, base_url="/page"),
                Div(
                    Badge("New", variant="primary"),
                    Badge("Beta", variant="warning"),
                    Badge("Deprecated", variant="error"),
                ),
                Avatar("https://via.placeholder.com/48", alt="User", status="online"),
                ProgressBar(75, label="Loading", variant="success"),
                Carousel(
                    ("https://via.placeholder.com/600x300", "Slide 1"),
                    ("https://via.placeholder.com/600x300", "Slide 2"),
                    autoplay=True,
                ),
                class_="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
            ),
            class_="flex gap-6",
        ),
        Footer(
            Div(
                P("© 2024 MikiUI. All rights reserved."),
                class_="flex justify-between items-center",
            ),
            copyright="MikiUI v0.1.0",
            social=[("GitHub", "https://github.com"), ("Docs", "https://kilo.ai/docs")],
        ),
    )


@app.route("/cards")
def cards_demo():
    """Showcase Card widget variants."""
    return Div(
        Navbar(brand="MikiUI Demo", links=[("Home", "/")]),
        H1("Cards & Layout"),
        Div(
            Card("Body content", title="Card Title", footer="Footer content"),
            Card("Outlined card", variant="outlined"),
            Card("Filled card", variant="filled"),
            class_="grid grid-cols-1 md:grid-cols-3 gap-4",
        ),
    )


@app.route("/forms")
def forms_demo():
    """Showcase forms with various input types."""
    return Div(
        Navbar(brand="MikiUI Demo", links=[("Home", "/")]),
        H1("Forms & Inputs"),
        GroupBox("Form Controls",
            Form(
                Div(
                    Label("Username:"),
                    Input(type="text", name="username", placeholder="Enter username"),
                    class_="space-y-2 w-full max-w-sm",
                ),
                SubmitButton("Submit"),
            ),
        ),
        GroupBox("Specialized Inputs",
            Div(
                DatePicker(label="Pick Date:", name="date"),
                ColorPicker(label="Pick Color:", name="color"),
                style="display: flex; gap: 1rem",
            ),
        ),
    )


@app.route("/data")
def data_demo():
    """Showcase DataGrid, TabbedPanel, LogViewer."""
    columns = ["Name", "Email", "Role", "Status"]
    rows = [
        ["Alice", "alice@example.com", "Admin", "Active"],
        ["Bob", "bob@example.com", "User", "Active"],
        ["Carol", "carol@example.com", "User", "Inactive"],
    ]
    return Div(
        Navbar(brand="MikiUI Demo", links=[("Home", "/")]),
        H1("Data Widgets"),
        GroupBox("DataGrid with Sorting",
            DataGrid(columns=columns, rows=rows, sortable=True, filterable=True),
        ),
        GroupBox("Tabbed Panel",
            TabbedPanel([
                ("Overview", P("Content for Overview")),
                ("Details", P("Content for Details")),
            ]),
        ),
        GroupBox("Log Viewer",
            LogViewer(lines=["info: Server started", "debug: Processing request"]),
        ),
    )


@app.route("/icons")
def icons_demo():
    """Showcase all available icons."""
    return Div(
        Navbar(brand="MikiUI Demo", links=[("Home", "/")]),
        H1("Icon Gallery"),
        P(f"{len(IconSet.icon_names())} built-in SVG icons (no external deps)."),
        Div(
            *[
                Card(
                    Div(Icon(name, size=32), class_="mb-2"),
                    title=name,
                    class_="text-center",
                )
                for name in IconSet.icon_names()
            ],
            class_="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4",
        ),
    )


@app.post("/increment")
def increment(ctx):
    """Increment the counter (HTMX partial update)."""
    ctx.app.state["count"] = ctx.app.state.get("count", 0) + 1
    return P(f"Counter: {ctx.app.state['count']}", id="count", class_="font-bold")
