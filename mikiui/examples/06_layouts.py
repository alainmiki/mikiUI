"""06_layouts.py — VS Code-like IDE layout.

Demonstrates Rail, Sidebar with TreeView, TabbedPanel, TerminalWidget,
StatusBar, Toolbar, and SplitView for resizable panels.

Run with: mikiui dev --app mikiui.examples.06_layouts:app
"""

from __future__ import annotations

from mikiui import Div, H1, H2, MikiApp, P
from mikiui.components import Button, Navbar, TreeView
from mikiui.widgets import (
    ContextWindow,
    DockablePanel,
    FilePicker,
    GroupBox,
    IDEEditor,
    LogViewer,
    MessageBox,
    MdiArea,
    MdiSubWindow,
    ProgressDialog,
    Rail,
    ScrollPanel,
    SidePanel,
    SplitView,
    StackedPanel,
    StatusBar,
    TabbedPanel,
    TerminalWidget,
    Toolbar,
    ToolboxPanel,
)

app = MikiApp(title="MikiUI Studio", lang="en")


@app.route("/")
def home() -> Div:
    explorer = SidePanel(
        "left",
        GroupBox("Explorer", TreeView([
            ("project", [
                ("src", [
                    ("main.py", None),
                    ("components", [("button.py", None), ("input.py", None), ("form.py", None)]),
                    ("widgets", [("datagrid.py", None), ("kanban.py", None), ("chatui.py", None)]),
                    ("utils.py", None),
                ]),
                ("tests", [("test_main.py", None), ("test_widgets.py", None)]),
                ("pyproject.toml", None),
                ("README.md", None),
            ]),
        ])),
        header="Explorer",
        collapsible=True,
    )

    editor = Div(
        MdiArea(
            MdiSubWindow("main.py", IDEEditor(content='import mikiui as mk\n\napp = mk.MikiApp("IDE Demo")\n\n@app.route("/")\ndef home():\n    return mk.Div(mk.H1("Hello, IDE!"))', language="python")),
            MdiSubWindow("styles.css", IDEEditor(content=':root {\n  --miki-bg: #0f172a;\n  --miki-fg: #e2e8f0;\n  --miki-accent: #6366f1;\n}', language="css")),
            class_="flex-1 bg-white",
        ),
        class_="flex-1 min-w-0 flex flex-col",
    )

    right_panel = SidePanel(
        "right",
        GroupBox("Search", P("Search across files, symbols, and references.", class_="text-sm text-slate-600")),
        GroupBox("Outline", P("No symbols found.", class_="text-sm text-slate-500")),
        header="Inspector",
        collapsible=True,
    )

    terminal = Div(
        TerminalWidget([
            "$ python -m mikiui dev",
            "INFO:     Uvicorn running on http://127.0.0.1:8000",
            "INFO:     Hot reload enabled",
            "$ ",
        ]),
        LogViewer(lines=[
            "info: Worker started",
            ("info", "Database connected"),
            ("warning", "Slow query detected (142ms)"),
            ("error", "Connection pool exhausted"),
            ("debug", "GC pause: 12ms"),
        ]),
        class_="h-full",
    )

    main_split = SplitView(
        SplitView(explorer, editor, orientation="horizontal", min_size=220),
        StackedPanel([
            ("Terminal", terminal),
            ("Problems", Div(P("2 warnings, 1 error."), class_="p-4 text-amber-600")),
            ("Output", Div(P("Build finished successfully."), class_="p-4 text-emerald-600")),
            ("Debug Console", Div(P("No active debug session."), class_="p-4 text-slate-500")),
        ]),
        orientation="vertical",
        min_size=180,
    )

    return Div(
        Toolbar(
            Button("Open", variant="secondary", class_="mr-1"),
            Button("Save", variant="secondary", class_="mr-1"),
            Button("Undo", variant="secondary", class_="mr-1"),
            Button("Redo", variant="secondary", class_="mr-1"),
            Div(class_="w-px h-6 bg-slate-300 mx-2"),
            Button("Run", variant="primary", class_="mr-1"),
            Button("Debug", variant="secondary", class_="mr-1"),
            Button("Stop", variant="secondary"),
            class_="px-2 py-1 border-b border-slate-200 bg-white",
        ),
        Div(
            Rail(
                Div(P("Files", class_="text-xs font-medium"), class_="p-2 text-center"),
                Div(P("Search", class_="text-xs font-medium"), class_="p-2 text-center"),
                Div(P("Git", class_="text-xs font-medium"), class_="p-2 text-center bg-indigo-50 text-indigo-700"),
                Div(P("Debug", class_="text-xs font-medium"), class_="p-2 text-center"),
                Div(P("Extensions", class_="text-xs font-medium"), class_="p-2 text-center"),
                width="64px",
            ),
            Div(
                main_split,
                class_="flex-1 min-w-0",
            ),
            class_="flex flex-1 min-h-0",
        ),
        StatusBar(
            Div(P("main.py · Python"), class_="text-xs"),
            Div(P("Ln 14, Col 28"), class_="text-xs"),
            Div(P("UTF-8"), class_="text-xs"),
            Div(P("Spaces: 4"), class_="text-xs"),
            Div(P("Ln 14, Col 28"), class_="text-xs"),
            Div(P("Python 3.14"), class_="text-xs"),
            class_="px-4 py-1 bg-slate-800 text-slate-300 text-xs border-t border-slate-700",
        ),
        class_="h-screen flex flex-col bg-white",
    )


if __name__ == "__main__":
    app.run(desktop=True, width=1280, height=800)
