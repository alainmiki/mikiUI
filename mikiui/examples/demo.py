"""Demo MikiUI app showcasing all components and widgets with drag-drop, sorting, and interactivity.

Run with: mikiui dev --app mikiui.examples.demo:app

This demo covers:
- All base HTML components (buttons, forms, tables, dialogs, etc.)
- All widgets (DataGrid, SplitView, DockablePanel, Card, Carousel, etc.)
- Layout patterns (Navbar, Sidebar, Footer, Drawer, Hero, etc.)
- Drag-drop and sorting interactions
- HTMX partial updates
- Theme switching (tailwind, bootstrap, dark, light)
"""

from __future__ import annotations

from mikiui import MikiApp, Div, H1, H2, P, Button, A, H3, Section, Span
from mikiui.components import (
    Navbar,
    Form,
    Label,
    Input,
    SubmitButton,
    Table,
    Tr,
    Th,
    Td,
    Dialog,
    DialogTitle,
    DialogBody,
    DialogFooter,
    Modal,
    Tabs,
    Checkbox,
    Radio,
    Slider,
    Select,
    Option,
    Optgroup,
)
from mikiui.widgets import (
    DataGrid,
    TabbedPanel,
    CollapsiblePanel,
    MessageBox,
    ProgressDialog,
    DockablePanel,
    SplitView,
    ScrollPanel,
    GroupBox,
    ColorPicker,
    DatePicker,
    Dial,
    LCDNumber,
    Drawer,
    Rail,
    ContextWindow,
    TabbedPanel as TabsWidget,
    LogViewer,
 
)
from mikiui.widgets.layout_widgets import Sidebar

app = MikiApp(title="MikiUI Demo App.  ")
app.set_theme("dracula")
# app.set_style_framework("tailwind")

@app.route("/")
def home():
    """Home page with quick navigation."""
    return Div(
        Navbar(
            brand="MikiUI Demo.",
            links=[
                ("Home", "/"),
                ("Data", "/data"),
                ("Forms", "/forms"),
                ("Dialog", "/dialog"),
                ("Advanced", "/advanced"),
            ],
            sticky=True,
            dark=True,
        ),
        Div(
            Div(
                H1("MikiUI Demo", class_="text-3xl font-bold"),
                P(
                    "Python-first UI framework with drag-drop, sorting, and interactivity",
                    class_="text-gray-400",
                ),
                class_="space-y-2",
            ),
            Div(
                Button(
                    "Data Tables", variant="primary", hx_get="/data", **{"x-data": "{}"}
                ),
                Button("Forms", variant="secondary", hx_get="/forms"),
                Button("Dialogs", variant="ghost", hx_get="/dialog"),
                class_="flex gap-4 mt-8",
            ),
            class_="p-8",
        ),
    )


@app.route("/data")
def data_demo():
    """Showcase DataGrid with sorting and filtering."""
    columns = ["Name", "Email", "Role", "Status"]
    rows = [
        ["Alice", "alice@example.com", "Admin", "Active"],
        ["Bob", "bob@example.com", "User", "Inactive"],
        ["Carol", "carol@example.com", "User", "Active"],
        ["David", "david@example.com", "Admin", "Active"],
        ["Eve", "eve@example.com", "User", "Pending"],
    ]

    return Div(
        Navbar(
            brand="MikiUI Demo",
            links=[("Home", "/")],
            sticky=True,
        ),
        Div(
            H1("Interactive Data Widgets"),
            H2("Sortable & Filterable DataGrid"),
            Div(
                DataGrid(
                    columns=columns,
                    rows=rows,
                    sortable=True,
                    filterable=True,
                    pagination=True,
                    page_size=3,
                ),
                class_="mt-4",
            ),
            H2("Split View with Dockable Panels"),
            Div(
                SplitView(
                    Div("Left Panel - Files", class_="p-4"),
                    DockablePanel(
                        "Bottom Panel",
                        "Panel content goes here",
                        dock="bottom",
                        closeable=True,
                        collapsible=True,
                    ),
                    orientation="horizontal",
                    min_size=150,
                ),
                class_="border rounded-lg p-4 h-64",
            ),
            H2("Tabbed Interface"),
            Div(
                Tabs(
                    tabs=[
                        ("Overview", Div("Overview content")),
                        ("Details", Div("Details content here")),
                        ("Settings", Div("Settings options")),
                    ],
                ),
                class_="border rounded-lg p-4",
            ),
            H2("Collapsible Panel"),
            Div(
                CollapsiblePanel(
                    "More Details",
                    P("This content can be collapsed/expanded with smooth animation."),
                    open=True,
                    animate=True,
                ),
                class_="border rounded-lg p-4",
            ),
            H2("Log Viewer"),
            Div(
                LogViewer(
                    lines=[
                        "info: Application started",
                        ("info", "Server listening on port 8000"),
                        ("warning", "Connection timeout - retrying"),
                        ("error", "Database connection failed"),
                        "debug: Processing record 12345",
                    ],
                ),
                class_="border rounded-lg p-4 font-mono text-sm",
            ),
            class_="p-8 space-y-8",
        ),
    )


@app.route("/forms")
def forms_demo():
    """Showcase forms with drag-drop and sorting."""
    return Div(
        Navbar(
            brand="MikiUI Demo",
            links=[("Home", "/")],
            sticky=True,
        ),
        Div(
            H1("Interactive Forms"),
            H2("Form Group with Multiple Inputs"),
            GroupBox(
                "User Registration",
                Form(
                    Div(
                        Label("Username"),
                        Input(
                            type="text", name="username", placeholder="Enter username"
                        ),
                        class_="flex flex-col",
                    ),
                    Div(
                        Label("Email"),
                        Input(
                            type="email", name="email", placeholder="user@example.com"
                        ),
                        class_="flex flex-col",
                    ),
                    Div(
                        Label("Role"),
                        Select(
                            Option("Select role", value="", selected=True),
                            Option("Administrator", value="admin"),
                            Option("User", value="user"),
                            Option("Guest", value="guest"),
                        ),
                        class_="flex flex-col",
                    ),
                    Div(
                        Label("Status"),
                        Radio("Active", name="status", value="active", checked=True),
                        Radio("Inactive", name="status", value="inactive"),
                        Radio("Pending", name="status", value="pending"),
                        class_="flex gap-4",
                    ),
                    Div(
                        Label("Slider Value"),
                        Slider(type="range", min=0, max=100, value=50),
                        class_="flex flex-col w-48",
                    ),
                    SubmitButton("Register"),
                    class_="space-y-4",
                ),
                class_="p-4",
            ),
            H2("Date & Color Pickers"),
            Div(
                Div(
                    DatePicker(label="Select Date:"),
                    ColorPicker(label="Pick Color:", name="color"),
                    class_="flex gap-8 items-center",
                ),
                class_="border rounded-lg p-4",
            ),
            class_="p-8 space-y-8",
        ),
    )


@app.route("/dialog")
def dialog_demo():
    """Showcase dialogs and modals."""
    return Div(
        Navbar(
            brand="MikiUI Demo",
            links=[("Home", "/")],
            sticky=True,
        ),
        Div(
            H1("Dialogs & Modals"),
            H2("Alert Dialog"),
            Div(
                MessageBox(
                    "Success!",
                    "Your changes have been saved successfully.",
                    kind="success",
                    buttons=[("OK", "ok"), ("Cancel", "cancel")],
                ),
                class_="border rounded-lg p-4",
            ),
            H2("Progress Dialog"),
            Div(
                ProgressDialog(title="Installing", message="Please wait...", value=75),
                class_="border rounded-lg p-4",
            ),
            H2("Message Box Types"),
            Div(
                Div(
                    MessageBox("Info", "Information message", kind="info"),
                    MessageBox("Warning", "Warning message", kind="warning"),
                    MessageBox("Error", "Error message", kind="error"),
                    MessageBox("Question", "Are you sure?", kind="question"),
                    class_="grid grid-cols-2 gap-4",
                ),
                class_="border rounded-lg p-4",
            ),
            H2("Modal Dialog"),
            Modal(
                ModalTitle("Modal Title"),
                ModalBody("This is a modal dialog body."),
                class_="w-full max-w-md",
            ),
            class_="p-8 space-y-8",
        ),
    )


@app.route("/advanced")
def advanced_demo():
    """Showcase advanced widgets with drag-drop."""
    return Div(
        Navbar(
            brand="MikiUI Demo",
            links=[("Home", "/")],
            sticky=True,
        ),
        Div(
            H1("Advanced Widgets"),
            H2("Dockable Panel (Draggable)"),
            Div(
                DockablePanel(
                    "Draggable Panel",
                    "Drag me around! The panel can be detached or collapsed.",
                    dock="right",
                    closeable=True,
                    resizable=True,
                    detachable=True,
                ),
                class_="border rounded-lg p-4 h-48",
            ),
            H2("Sidebar with Navigation"),
            Div(
                Div(
                    Sidebar(
                        ("Dashboard", "/"),
                        ("Settings", "/settings"),
                        ("Profile", "/profile"),
                        title="Main Menu",
                    ),
                    class_="w-48",
                ),
                Div(
                    "Main content area with Rail navigation",
                    Rail(
                        ("Home", "/", "home"),
                        ("Settings", "/settings", "settings"),
                        ("Profile", "/profile", "user"),
                        side="left",
                    ),
                    class_="flex",
                ),
                class_="border rounded-lg h-48",
            ),
            H2("Tabbed Panel"),
            Div(
                TabbedPanel(
                    tabs=[
                        ("Tab 1", "Content for tab 1"),
                        ("Tab 2", "Content for tab 2"),
                        ("Tab 3", "Content for tab 3"),
                    ],
                    closable=True,
                ),
                class_="border rounded-lg p-4 h-32",
            ),
            H2("Context Window"),
            Div(
                ContextWindow(
                    ("Action 1", "#"),
                    ("Action 2", "#"),
                    ("Action 3", "#"),
                    trigger=Button("Show Menu"),
                    position="bottom",
                ),
                class_="border rounded-lg p-4",
            ),
            H2("Drawer (Slide-in Panel)"),
            Div(
                Drawer(
                    "Drawer content goes here!",
                    title="Slide-in Drawer",
                    side="left",
                    open=True,
                ),
                class_="border rounded-lg",
            ),
            class_="p-8 space-y-8",
        ),
    )


# Helper components that need to exist


class ModalTitle(Div):
    tag = "div"


class ModalBody(Div):
    tag = "div"



if __name__ == "__main__":
    app.run()
