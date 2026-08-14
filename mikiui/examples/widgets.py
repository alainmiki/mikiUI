"""MikiUI Widgets demo module.

Submodule showcasing all widgets and panels.

Usage:
    from mikiui.examples.widgets import app
    # app has routes: /, /forms, /data
"""

from __future__ import annotations

from mikiui import MikiApp, Div, H1, H2, Button
from mikiui.components import Navbar, Form, Label, Input, SubmitButton, Calendar, ListView
from mikiui.widgets import (
    DataGrid, TabbedPanel, CollapsiblePanel, MessageBox, ProgressDialog,
    DockablePanel, SplitView, ScrollPanel, GroupBox,
    ColorPicker, DatePicker, Dial, LCDNumber,
)

app = MikiApp(title="MikiUI Widgets")


def Group(title, *children):
    return Div(H2(title), *children, class_="space-y-4")


@app.route("/")
def home():
    """All widgets showcase."""
    return Div(
        Navbar(
            brand="MikiUI Widgets",
            links=[
                ("Home", "/"),
                ("Data", "#data"),
                ("Layouts", "#layouts"),
                ("Inputs", "#inputs"),
            ],
        ),
        Div(
            H1("MikiUI Widgets Demo"),
            Group("Data Widgets",
                DataGrid(
                    columns=["Name", "Email", "Role", "Status"],
                    rows=[
                        ["Alice", "alice@example.com", "Admin", "Active"],
                        ["Bob", "bob@example.com", "User", "Active"],
                        ["Carol", "carol@example.com", "User", "Inactive"],
                        ["David", "david@example.com", "Moderator", "Active"],
                    ],
                    sortable=True,
                    filterable=True,
                ),
            ),
            Group("Layout Widgets",
                SplitView(
                    Div("Left Pane - Content", class_="border-r pr-4"),
                    Div("Right Pane - Editor"),
                ),
                CollapsiblePanel("Collapsible", "Toggle me!"),
                DockablePanel("Properties", "Panel content here."),
            ),
            Group("Dialog Widgets",
                Button("Show Dialog", onclick="document.querySelector('dialog').showModal()"),
                Button("Show MessageBox", onclick="document.querySelector('.miki-messagebox').style.display='block'"),
                MessageBox(title="MessageBox", message="This is a message.", kind="info"),
                Button("Show ProgressDialog", onclick="document.querySelector('.miki-progressdialog').style.display='block'"),
                ProgressDialog(title="Loading...", message="Please wait...", value=50),
            ),
            class_="space-y-6",
        ),
        class_="p-6 max-w-4xl mx-auto",
    )


@app.route("/forms")
def forms():
    """Widget-based forms."""
    return Div(
        Navbar(brand="MikiUI Widgets", links=[("Home", "/"), ("Forms", "/forms")]),
        Group("Form Widgets",
            Form(
                Div(
                    Label("Name:"),
                    Input(type="text", name="name", class_="w-full"),
                    Label("Email:"),
                    Input(type="email", name="email", class_="w-full"),
                    Label("Color:"),
                    ColorPicker(label="Color:", name="color"),
                    Button("Submit", variant="primary"),
                    class_="space-y-3 w-full max-w-sm",
                ),
            ),
        ),
        class_="p-6",
    )


@app.route("/data")
def data():
    """Data-focused widgets."""
    return Div(
        Navbar(brand="MikiUI Widgets", links=[("Home", "/"), ("Data", "/data")]),
        Group("Data Grid",
            DataGrid(
                columns=["Name", "Email", "Role", "Status"],
                rows=[
                    ["Alice", "alice@example.com", "Admin"],
                    ["Bob", "bob@example.com", "User"],
                    ["Carol", "carol@example.com", "User"],
                    ["David", "david@example.com", "Moderator"],
                ],
                sortable=True,
            ),
        ),
        Group("List View",
            ListView(items=["Item 1", "Item 2", "Item 3"]),
        ),
        class_="p-6",
    )


@app.route("/calendar")
def calendar():
    """Calendar widget."""
    return Div(
        Navbar(brand="MikiUI Widgets", links=[("Home", "/"), ("Calendar", "/calendar")]),
        Group("Calendar",
            Calendar(weekdays=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
        ),
        class_="p-6",
    )


@app.route("/controls")
def controls():
    """Interactive control widgets."""
    return Div(
        Navbar(brand="MikiUI Widgets", links=[("Home", "/"), ("Controls", "/controls")]),
        Group("Input Controls",
            DatePicker(label="Date:", name="date"),
            ColorPicker(label="Color:", name="color"),
            H2("Dial Control"),
            Dial(value=50, min=0, max=100),
            LCDNumber(value=42, digits=6),
        ),
        class_="p-6",
    )


@app.route("/scroll")
def scroll():
    """Scrollable widgets."""
    return Div(
        Navbar(brand="MikiUI Widgets", links=[("Home", "/"), ("Scroll", "/scroll")]),
        Group("Scrollable Panel",
            ScrollPanel(
                Div(*[Div(f"Line {i}") for i in range(1, 30)]),
                style="height: 200px",
            ),
        ),
        class_="p-6",
    )