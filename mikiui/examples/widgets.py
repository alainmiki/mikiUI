"""MikiUI Widgets demo module.

Submodule showcasing all widgets and panels.

Usage:
    from mikiui.examples.widgets import app
    # app has routes: /, /forms, /data
"""

from __future__ import annotations

from mikiui import H1, H2, Button, Div, MikiApp
from mikiui.components import Calendar, Form, Input, Label, ListView, Navbar
from mikiui.widgets import (
    Carousel,
    ChatUI,
    CollapsiblePanel,
    ColorPicker,
    DataGrid,
    DatePicker,
    Dial,
    DockablePanel,
    Drawer,
    FilePicker,
    KanbanBoard,
    LCDNumber,
    MessageBox,
    ProgressDialog,
    ScrollPanel,
    SplitView,
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
            Group("Chat Widget",
                ChatUI([
                    {"role": "bot", "text": "Hello! How can I help?"},
                    {"role": "user", "text": "Show me a demo"},
                    {"role": "bot", "text": "Here is the MikiUI demo."},
                ]),
            ),
            Group("Layout Widgets",
                SplitView(
                    Div("Left Pane - Content", class_="border-r pr-4"),
                    Div("Right Pane - Editor"),
                ),
                CollapsiblePanel("Collapsible", "Toggle me!", animate=True),
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
                    Label("File:"),
                    FilePicker(name="upload", label="Drop files here or click to browse"),
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
        Group("Kanban Board",
            KanbanBoard({
                "Todo": ["Task A", "Task B"],
                "In Progress": ["Task C"],
                "Done": ["Task D"],
            }),
        ),
        Group("Carousel",
            Carousel(
                "https://via.placeholder.com/800x400/2563eb/ffffff?text=Slide+1",
                "https://via.placeholder.com/800x400/16a34a/ffffff?text=Slide+2",
                "https://via.placeholder.com/800x400/dc2626/ffffff?text=Slide+3",
            ),
        ),
        Group("Drawer Example",
            Button("Open Drawer", onclick="mikiDrawer.open(document.querySelector('.demo-drawer'))"),
            Button("Toggle Drawer", onclick="mikiDrawer.toggle(document.querySelector('.demo-drawer'))", class_="ml-2"),
            Drawer(
                Div(
                    P("This is the drawer content. Close via ESC, overlay, or ✕ button."),
                    Button("Close", onclick="mikiDrawer.close(document.querySelector('.demo-drawer'))"),
                ),
                title="Drawer",
                side="left",
                open=False,
                class_="demo-drawer",
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
            Dial(value=50, min=0, max=100, step=5, size=160),
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