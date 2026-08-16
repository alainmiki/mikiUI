"""05_widgets_gallery.py — Interactive widget playground.

Showcases DataGrid, KanbanBoard, Carousel, ChatUI, FormWizard,
and a curated set of input and layout widgets.

Run with: mikiui dev --app mikiui.examples.05_widgets_gallery:app
"""

from __future__ import annotations

from mikiui import H1, H2, MikiApp, P
from mikiui.components import Navbar
from mikiui.components.form import Label
from mikiui.components.html import Div
from mikiui.components.input import Input, Textarea
from mikiui.components.treeview import TreeView
from mikiui.widgets import (
    Avatar,
    Badge,
    Carousel,
    ChatUI,
    ColorPicker,
    CollapsiblePanel,
    ContextWindow,
    DataGrid,
    DatePicker,
    Dial,
    DockablePanel,
    Drawer,
    FilePicker,
    FormWizard,
    GroupBox,
    KanbanBoard,
    LCDNumber,
    LogViewer,
    MessageBox,
    Progress,
    ProgressDialog,
    ScrollPanel,
    SearchPanel,
    SidePanel,
    SplitView,
    StackedPanel,
    StatusBar,
    StreamingPanel,
    TabbedPanel,
    TerminalWidget,
    Toolbar,
    ToolboxPanel,
)

app = MikiApp(title="Widget Playground", lang="en")


def Section(title: str, *children, **attrs) -> Div:
    extra_class = attrs.pop("class_", "")
    merged_class = f"space-y-4 {extra_class}".strip()
    return Div(H2(title, class_="text-2xl font-bold text-slate-800 mb-4"), *children, class_=merged_class, **attrs)


EMPLOYEES = [
    {"name": "Alice Kim", "email": "alice@acme.com", "role": "Engineer", "status": "Active", "team": "Platform"},
    {"name": "Bob Osei", "email": "bob@acme.com", "role": "Designer", "status": "Active", "team": "Product"},
    {"name": "Carol Wu", "email": "carol@acme.com", "role": "PM", "status": "Away", "team": "Product"},
    {"name": "David Park", "email": "david@acme.com", "role": "Engineer", "status": "Active", "team": "Infra"},
    {"name": "Elena Rossi", "email": "elena@acme.com", "role": "QA Lead", "status": "Active", "team": "Quality"},
    {"name": "Frank Müller", "email": "frank@acme.com", "role": "DevOps", "status": "Offline", "team": "Infra"},
    {"name": "Grace Li", "email": "grace@acme.com", "role": "Engineer", "status": "Active", "team": "Mobile"},
    {"name": "Hassan Ali", "email": "hassan@acme.com", "role": "Data", "status": "Active", "team": "Analytics"},
]


@app.route("/")
def home() -> Div:
    return Div(
        Navbar(
            brand="Widget Playground",
            links=[
                ("Data", "#data"),
                ("Layout", "#layout"),
                ("Inputs", "#inputs"),
                ("Chat", "#chat"),
                ("Wizard", "#wizard"),
            ],
            dark=True,
        ),
        Div(
            Section("Data Widgets",
                Div(
                    P("Sortable, filterable DataGrid backed by in-memory employee records.", class_="text-slate-600 mb-4"),
                    DataGrid(
                        columns=["Name", "Email", "Role", "Status", "Team"],
                        rows=EMPLOYEES,
                        sortable=True,
                        filterable=True,
                        pagination=True,
                        page_size=5,
                        search=True,
                    ),
                    class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100",
                ),
                Div(
                    P("Kanban board for sprint planning.", class_="text-slate-600 mb-4"),
                    KanbanBoard({
                        "Backlog": ["Write RFC for caching", "Evaluate Redis vs Valkey"],
                        "In Progress": ["Migrate auth service", "Dashboard redesign"],
                        "Review": ["Security patch #4021", "API rate-limit refactor"],
                        "Done": ["CI pipeline upgrade", "Docker multi-stage builds"],
                    }),
                    class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100",
                ),
                id="data",
            ),
            Section("Layout Widgets",
                Div(
                    SplitView(
                        Div(
                            P("File Explorer", class_="font-semibold text-slate-700 mb-2"),
                            TreeView([
                                ("src", [
                                    ("main.py", None),
                                    ("config.py", None),
                                    ("models", [("user.py", None), ("post.py", None)]),
                                    ("routes", [("api.py", None), ("web.py", None)]),
                                ]),
                                ("tests", [("test_api.py", None), ("test_web.py", None)]),
                                ("pyproject.toml", None),
                                ("README.md", None),
                            ]),
                            class_="p-4",
                        ),
                        Div(
                            TabbedPanel([
                                ("Editor", Div(P("Tabbed editor content with syntax highlighting."), class_="p-4")),
                                ("Preview", Div(P("Rendered output preview."), class_="p-4")),
                                ("Problems", Div(P("No problems detected."), class_="p-4 text-emerald-600")),
                            ]),
                            class_="p-2",
                        ),
                        orientation="horizontal",
                    ),
                    class_="h-96",
                ),
                Div(
                    SidePanel(
                        "left",
                        Div(
                            P("Dashboard", class_="font-semibold"),
                            P("Projects"),
                            P("Calendar"),
                            P("Team"),
                            P("Settings"),
                            class_="space-y-3",
                        ),
                        header="Navigation",
                    ),
                    Div(
                        P("Main content area with persistent left navigation.", class_="text-slate-600"),
                        class_="p-6",
                    ),
                    class_="bg-white rounded-xl shadow-sm border border-slate-100 h-72",
                ),
                id="layout",
            ),
            Section("Inputs & Controls",
                Div(
                    Div(
                        DatePicker(label="Start date:", name="start", value="2026-09-01"),
                        ColorPicker(label="Brand color:", name="color", value="#6366f1"),
                        Dial(value=65, min=0, max=100),
                        LCDNumber(value=3.14159, digits=8),
                        class_="flex flex-wrap gap-6 items-end",
                    ),
                    class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100",
                ),
                Div(
                    SearchPanel(placeholder="Search employees, tickets, docs...", on_search="/api/search"),
                    class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100",
                ),
                Div(
                    FilePicker(name="avatar", accept="image/*", label="Upload profile picture"),
                    class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100 max-w-xl",
                ),
                id="inputs",
            ),
            Section("Carousel & Chat",
                Div(
                    P("Image carousel with real placeholder images.", class_="text-slate-600 mb-4"),
                    Carousel(
                        ("https://picsum.photos/seed/a1/800/350", "Mountain landscape"),
                        ("https://picsum.photos/seed/a2/800/350", "City skyline"),
                        ("https://picsum.photos/seed/a3/800/350", "Ocean view"),
                        ("https://picsum.photos/seed/a4/800/350", "Forest trail"),
                        autoplay=True,
                        interval=4000,
                    ),
                    class_="bg-white p-2 rounded-xl shadow-sm border border-slate-100",
                ),
                Div(
                    P("Chat UI with pre-filled messages.", class_="text-slate-600 mb-4"),
                    ChatUI([
                        {"role": "bot", "text": "Welcome to the Widget Playground support channel."},
                        {"role": "user", "text": "How do I use the DataGrid?"},
                        {"role": "bot", "text": "Set columns and rows, then enable sortable=True and filterable=True."},
                        {"role": "user", "text": "Can I paginate?"},
                        {"role": "bot", "text": "Yes — pass pagination=True and page_size=N."},
                    ]),
                    class_="bg-white p-2 rounded-xl shadow-sm border border-slate-100 max-w-2xl",
                ),
                id="chat",
            ),
            Section("Multi-Step Form Wizard",
                Div(
                    FormWizard([
                        ("Account", Div(
                            P("Create your account credentials.", class_="text-slate-600 mb-4"),
                            Div(
                                Label("Username", for_="wiz-user"),
                                Input(type="text", id="wiz-user", name="username", placeholder="jdoe", class_="w-full rounded border-slate-300"),
                                Label("Email", for_="wiz-email"),
                                Input(type="email", id="wiz-email", name="email", placeholder="jdoe@acme.com", class_="w-full rounded border-slate-300"),
                                class_="space-y-3",
                            ),
                        )),
                        ("Profile", Div(
                            P("Tell us about yourself.", class_="text-slate-600 mb-4"),
                            Div(
                                Label("Display Name", for_="wiz-display"),
                                Input(type="text", id="wiz-display", name="display", placeholder="John Doe", class_="w-full rounded border-slate-300"),
                                Label("Bio", for_="wiz-bio"),
                                Textarea(id="wiz-bio", name="bio", placeholder="Software engineer...", rows=3, class_="w-full rounded border-slate-300"),
                                class_="space-y-3",
                            ),
                        )),
                        ("Confirm", Div(
                            P("Review your details before finishing.", class_="text-slate-600 mb-4"),
                            Div(P("Username: jdoe", class_="text-sm"), P("Email: jdoe@acme.com", class_="text-sm"), P("Display: John Doe", class_="text-sm"), class_="space-y-1"),
                        )),
                    ], current=0),
                    class_="max-w-2xl",
                ),
                id="wizard",
            ),
            Section("Panels & Feedback",
                Div(
                    CollapsiblePanel("Advanced Settings", Div(P("Enable experimental caching, WebSocket compression, and prefetch thresholds."), class_="text-slate-600"), open=True),
                    CollapsiblePanel("Danger Zone", Div(P("Delete account, revoke all tokens, and purge cache."), class_="text-red-600"), open=False),
                    class_="max-w-2xl space-y-3",
                ),
                Div(
                    Progress(value=72, label="Upload progress", variant="success"),
                    ProgressDialog(title="Building project", message="Compiling assets...", value=45),
                    MessageBox("Changes saved", "Your preferences have been updated.", kind="success"),
                    class_="max-w-2xl space-y-4",
                ),
                Div(
                    StreamingPanel(title="Live Build Log"),
                    class_="max-w-2xl",
                ),
                class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100",
            ),
            Section("Terminal & Logs",
                Div(
                    TerminalWidget([
                        "$ python -m mikiui dev",
                        "INFO:     Started server process",
                        "INFO:     Uvicorn running on http://127.0.0.1:8000",
                        "INFO:     Application startup complete",
                    ]),
                    class_="max-w-2xl",
                ),
                Div(
                    LogViewer(lines=[
                        "info: Worker started",
                        ("info", "Connected to database"),
                        ("warning", "High memory usage on worker-3"),
                        ("error", "Job #1024 failed: timeout"),
                        ("debug", "Heartbeat OK"),
                        ("info", "Cache hit ratio: 94.2%"),
                    ], line_numbers=True),
                    class_="max-w-2xl mt-4",
                ),
                class_="bg-slate-900 p-6 rounded-xl",
            ),
            class_="max-w-6xl mx-auto space-y-16 py-12",
        ),
        class_="min-h-screen bg-slate-50",
    )


if __name__ == "__main__":
    app.run(desktop=True)
