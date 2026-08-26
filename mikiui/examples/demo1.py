"""Demo MikiUI app showcasing all components and widgets.

Run with: mikiui dev --app mikiui.examples.demo:app

This demo uses only inline styles so it works with the "plain" CSS framework
(no Tailwind dependency). For Tailwind, swap set_style_framework("plain") for
set_style_framework("tailwind", mode="cdn").
"""

from __future__ import annotations

from mikiui import H1, H2, H3, Button, Div, MikiApp, P, Span
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
from mikiui.components import BottomSheet
from mikiui.widgets import (
    CollapsiblePanel,
    ColorPicker,
    ContextWindow,
    DataGrid,
    DatePicker,
    Dial,
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

app = MikiApp(title="MikiUI Demo")
app.set_theme("dracula")
app.set_style_framework("plain")

# Shared inline style helpers
FLEX_ROW = "display: flex; flex-direction: row"
FLEX_COL = "display: flex; flex-direction: column"
FLEX_CENTER = "display: flex; align-items: center; justify-content: space-between"
CARD = "border: 1px solid var(--miki-border); border-radius: 0.5rem; padding: 1rem"
PADDING = "padding: 2rem"
GAP = "gap: 1rem"


@app.route("/")
def home():
    return Div(
        Navbar(
            brand="MikiUI Demo",
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
                H1("MikiUI Demo", style="font-size: 1.875rem; font-weight: 700; margin: 0"),
                P(
                    "Python-first UI framework with drag-drop, sorting, and interactivity",
                    style="color: var(--miki-text-muted, #9ca3af); margin: 0.5rem 0 0 0",
                ),
                style=FLEX_COL + "; gap: 0.5rem",
            ),
            Div(
                Button("Toggle Theme", variant="success", hx_get="/toggle-theme"),
                Button("Forms", variant="secondary", hx_get="/forms"),
                Button("Data Tables", variant="primary", hx_get="/data"),
                style=FLEX_ROW + f"; {GAP}; margin-top: 2rem; flex-wrap: wrap",
            ),
            Div(
                Div(
                    Button("Open Drawer", onclick="mikiDrawer.open('.demo-drawer')", class_="mb-2"),
                    Button("Open Right Drawer", onclick="mikiDrawer.open('.demo-drawer-right')", class_="mb-2"),
                    Button("Open Bottom Sheet", onclick="mikiBottomSheet.open('.demo-bottomsheet')", class_="mb-2"),
                    class_="flex gap-2",
                ),
                Drawer(
                    Div(
                        P("This drawer slides in from the left. Use ESC, overlay click, or the close button to dismiss it."),
                        Button("Close", onclick="mikiDrawer.close('.demo-drawer')"),
                    ),
                    title="Slide-in Drawer",
                    side="left",
                    open=False,
                    class_="demo-drawer",
                ),
                Drawer(
                    Div(
                        P("This drawer slides in from the right."),
                    ),
                    title="Right Drawer",
                    side="right",
                    open=False,
                    class_="demo-drawer-right",
                ),
                Drawer(
                    Div(
                        P("This drawer slides in from the right but is anchored to the left."),
                        Button("Close", onclick="mikiDrawer.close('.demo-drawer-override')"),
                    ),
                    title="Override Drawer",
                    side="left",
                    open_side="right",
                    open=False,
                    class_="demo-drawer-override",
                ),
                BottomSheet(
                    Div(
                        P("This is a bottom sheet that slides up from the bottom."),
                        Button("Close", onclick="mikiBottomSheet.close('.demo-bottomsheet')"),
                    ),
                    title="Bottom Sheet",
                    size="md",
                    class_="demo-bottomsheet",
                ),
                Dial(value=50, min=0, max=100, step=5, size=140),
                style=PADDING,
            ),
            style=PADDING,
        ),
    )


@app.route("/data")
def data_demo():
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
                style="margin-top: 1rem",
            ),
            H2("Split View with Nested SplitView + Dockable Panel"),
            Div(
                SplitView(
                    Div(
                        SplitView(
                            Div("Editor Content", style="padding: 1rem; height: 100%"),
                            Div("Output Panel", style="padding: 1rem; height: 100%"),
                            orientation="vertical",
                            min_size=60,
                            resize_mode="vertical",
                        ),
                        style="height: 100%",
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
                    resize_mode="both",
                ),
                style=CARD + "; height: 24rem",
            ),
            Div(
                SplitView(
                    Div("Left Pane", style="padding: 1rem"),
                    Div("Right Pane", style="padding: 1rem"),
                    orientation="horizontal",
                    min_size=100,
                    resize_mode="both",
                ),
                style=CARD + "; height: 12rem",
            ),
            H2("vertical Split (min-size=50)"),
            Div(
                SplitView(
                    Div("Left Pane", style="padding: 1rem"),
                    Div("Right Pane", style="padding: 1rem"),
                    orientation="vertical",
                    min_size=50,
                    resize_mode="vertical",
                ),
                style=CARD + "; height: 8rem",
            ),
            H2("horizontal Split (min-size=60)"),
            Div(
                SplitView(
                    Div("Top Pane", style="padding: 1rem"),
                    Div("Bottom Pane", style="padding: 1rem"),
                    orientation="horizontal",
                    min_size=60,
                    resize_mode="horizontal",
                ),
                style=CARD + "; height: 8rem",
            ),
            H2("Kanban Board"),
            Div(
                KanbanBoard({
                    "Todo": ["Write specs", "Design API", "Setup CI"],
                    "In Progress": ["Implement widgets", "Add tests"],
                    "Done": ["Project scaffold", "CLI setup"],
                }),
                style="margin-top: 1rem",
            ),
            H2("Drag & Drop File Picker"),
            Div(
                FilePicker(name="upload", label="Drop files here or click to browse", accept="image/*"),
                style="margin-top: 1rem",
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
                style=CARD,
            ),
            H2("Collapsible Panel"),
            Div(
                CollapsiblePanel(
                    "More Details",
                    P("This content can be collapsed/expanded with smooth animation."),
                    open=True,
                    animate=True,
                ),
                style=CARD,
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
                style=CARD + "; font-family: ui-monospace, monospace; font-size: 0.875rem",
            ),
            style=PADDING + f"; {FLEX_COL}; gap: 2rem",
        ),
    )


@app.route("/forms")
def forms_demo():
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
                        Input(type="text", name="username", placeholder="Enter username"),
                        style=FLEX_COL,
                    ),
                    Div(
                        Label("Email"),
                        Input(type="email", name="email", placeholder="user@example.com"),
                        style=FLEX_COL,
                    ),
                    Div(
                        Label("Role"),
                        Select(
                            Option("Select role", value="", selected=True),
                            Option("Administrator", value="admin"),
                            Option("User", value="user"),
                            Option("Guest", value="guest"),
                        ),
                        style=FLEX_COL,
                    ),
                    Div(
                        Label("Status"),
                        Radio("Active", name="status", value="active", checked=True),
                        Radio("Inactive", name="status", value="inactive"),
                        Radio("Pending", name="status", value="pending"),
                        style=FLEX_ROW + f"; {GAP}",
                    ),
                    Div(
                        Label("Slider Value"),
                        Slider(type="range", min=0, max=100, value=50),
                        style=FLEX_COL + "; width: 12rem",
                    ),
                    SubmitButton("Register"),
                    style=FLEX_COL + "; gap: 1rem",
                ),
                style="padding: 1rem",
            ),
            H2("Date & Color Pickers"),
            Div(
                Div(
                    DatePicker(label="Select Date:"),
                    ColorPicker(label="Pick Color:", name="color"),
                    style=FLEX_ROW + "; gap: 2rem; align-items: center",
                ),
                style=CARD,
            ),
            style=PADDING + f"; {FLEX_COL}; gap: 2rem",
        ),
    )


@app.route("/dialog")
def dialog_demo():
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
                style=CARD,
            ),
            H2("Progress Dialog"),
            Div(
                ProgressDialog(title="Installing", message="Please wait...", value=75),
                style=CARD,
            ),
            H2("Message Box Types"),
            Div(
                Div(
                    MessageBox("Info", "Information message", kind="info"),
                    MessageBox("Warning", "Warning message", kind="warning"),
                    MessageBox("Error", "Error message", kind="error"),
                    MessageBox("Question", "Are you sure?", kind="question"),
                    style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem",
                ),
                style=CARD,
            ),
            H2("Modal Dialog"),
            Modal(
                "This is a modal dialog body.",
                title="Modal Title",
                open=False,
            ),
            style=PADDING + f"; {FLEX_COL}; gap: 2rem",
        ),
    )


@app.route("/toggle-theme")
def toggle_theme():
    from random import choice
    themes = ["light", "dark", "dracula", "cyberpunk", "retro", "forest", "aqua", "cupcake"]
    return Button(choice(themes), variant="success")


@app.route("/advanced")
def advanced_demo():
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
                style=CARD + "; height: 12rem",
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
                    style="width: 12rem",
                ),
                Div(
                    Span("Main content area with Rail navigation"),
                    Rail(
                        ("Home", "/", "home"),
                        ("Settings", "/settings", "settings"),
                        ("Profile", "/profile", "user"),
                        side="left",
                    ),
                    style=FLEX_ROW,
                ),
                style=CARD + "; height: 12rem",
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
                style=CARD + "; height: 8rem",
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
                style=CARD,
            ),
        H2("Drawer (Slide-in Panel)"),
        Div(
            Drawer(
                "Drawer content goes here!",
                title="Slide-in Drawer",
                side="left",
                open=True,
            ),
            style=CARD,
        ),
    ),
)

if __name__ == "__main__":
    app.run(desktop=True, reload=True)
