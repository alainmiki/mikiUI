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

from mikiui import H1, H2, Button, Div, MikiApp, P
from mikiui.components import (
    Form,
    Input,
    Label,
    Modal,
    Navbar,
    Option,
    Radio,
    Select,
    Slider,
    SubmitButton,
    Tabs,
)
from mikiui.widgets import (
    CollapsiblePanel,
    ColorPicker,
    ContextWindow,
    DataGrid,
    DatePicker,
    DockablePanel,
    Drawer,
    FilePicker,
    GroupBox,
    KanbanBoard,
    LogViewer,
    MessageBox,
    ProgressDialog,
    Rail,
    SplitView,
    TabbedPanel,
)
from mikiui.widgets.layout_widgets import Sidebar

app = MikiApp(title="MikiUI Demo App 1.  ")
app.set_theme("dark")
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
                class_="space-y-2 ",
            ),
            Div(
                Button("Theme", variant="success", hx_get="/toggle-theme"),
                Button("Forms", variant="secondary", hx_get="/forms"),
                Button(
                    "Data Tables", variant="primary", hx_get="/data"
                ),
                Button("theming", variant="ghost", hx_get="/toggle-theme"),
                class_="flex gap-4 mt-8 pt-3",
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
            H2("Split View with Nested SplitView + Dockable Panel"),
            Div(
                SplitView(
                    Div(
                        SplitView(
                            Div("Editor Content", class_="p-4"),
                            Div("Output Panel", class_="p-4 bg-gray-800/30"),
                            orientation="vertical",
                            min_size=60,
                            resize_mode="vertical",
                        ),
                        class_="h-full",
                    ),
                    DockablePanel(
                        "Properties",
                        "Right panel content — drag the header to dock or float.",
                        dock="right",
                        closeable=True,
                        collapsible=True,
                        detachable=True,
                        snap_threshold=80,
                        dock_width="280px",
                        float_width="45vw",
                        float_height="60vh",
                    ),
                    orientation="horizontal",
                    min_size=200,
                    resize_mode="horizontal",
                ),
                class_="border rounded-lg p-4 h-96",
            ),
            H2("Horizontal Split (min-size=50)"),
            Div(
                SplitView(
                    Div("Left Pane", class_="p-4"),
                    Div("Right Pane", class_="p-4"),
                    orientation="horizontal",
                    min_size=50,
                    resize_mode="horizontal",
                ),
                class_="border rounded-lg p-4 h-32",
            ),
            H2("Vertical Split (min-size=60)"),
            Div(
                SplitView(
                    Div("Top Pane", class_="p-4"),
                    Div("Bottom Pane", class_="p-4"),
                    orientation="vertical",
                    min_size=60,
                    resize_mode="vertical",
                ),
                class_="border rounded-lg p-4 h-32",
            ),
            H2("Kanban Board"),
            Div(
                KanbanBoard({
                    "Todo": ["Write specs", "Design API", "Setup CI"],
                    "In Progress": ["Implement widgets", "Add tests"],
                    "Done": ["Project scaffold", "CLI setup"],
                }),
                class_="mt-4",
            ),
            H2("Drag & Drop File Picker"),
            Div(
                FilePicker(name="upload", label="Drop files here or click to browse", accept="image/*"),
                class_="mt-4",
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

@app.route("/toggle-theme")
def toggle_theme():
    """Return a random theme button for HTMX partial update."""
    from random import choice
    themes = ["light", "dark", "dracula", "cyberpunk", "retro", "forest", "aqua", "cupcake"]
    return Button(choice(themes), variant="success")

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
            H2("Dockable Panel (In-Page / Float / Dock)"),
            Div(
                DockablePanel(
                    "Properties Panel",
                    "This panel starts in-page (inline in the page). "
                    "Click the detach button (⇋) to float it, or drag "
                    "the header toward a screen edge to snap-dock. "
                    "Click detach again to return to in-page.",
                    dock="in-page",
                    closeable=True,
                    collapsible=True,
                    detachable=True,
                    snap_threshold=100,
                    dock_width="280px",
                    float_width="45vw",
                    float_height="60vh",
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
    app.run(desktop=True,reload=True)
