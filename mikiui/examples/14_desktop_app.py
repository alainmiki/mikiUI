"""14_desktop_app.py — Desktop text editor with native feel.

Demonstrates MenuBar, Toolbar, StatusBar, IDEEditor, TreeView,
TerminalWidget, SplitView, MdiArea, and About dialog.

Run with: python mikiui/examples/14_desktop_app.py
"""

from __future__ import annotations

from mikiui import Div, H1, H2, MikiApp, P
from mikiui.components import Button, Navbar, TreeView
from mikiui.widgets import (
    FilePicker,
    IDEEditor,
    LogViewer,
    MenuBar,
    MdiArea,
    MdiSubWindow,
    MessageBox,
    Progress,
    SidePanel,
    SplitView,
    StatusBar,
    TerminalWidget,
    Toolbar,
)

app = MikiApp(title="MikiUI Studio", lang="en", desktop_icon="icon.ico")


@app.route("/")
def home() -> Div:
    file_tree = SidePanel(
        "left",
        TreeView([
            ("studio", [
                ("src", [
                    ("components", [("button.py", None), ("navbar.py", None), ("form.py", None)]),
                    ("widgets", [("datagrid.py", None), ("kanban.py", None), ("ide_editor.py", None)]),
                    ("engine", [("render.py", None), ("dom.py", None), ("diff.py", None)]),
                    ("main.py", None),
                    ("cli.py", None),
                ]),
                ("tests", [("test_main.py", None), ("test_engine.py", None)]),
                ("pyproject.toml", None),
                ("README.md", None),
                (".gitignore", None),
            ]),
        ]),
        header="Project Explorer",
        collapsible=True,
    )

    editor = MdiArea(
        MdiSubWindow("main.py", IDEEditor(
            content='"""MikiUI Studio entry point."""\n\nfrom mikiui import MikiApp, Div, H1\n\napp = MikiApp(title="Studio")\n\n@app.route("/")\ndef home():\n    return Div(\n        H1("Hello, MikiUI!"),\n        P("Edit this file to get started."),\n    )\n\nif __name__ == "__main__":\n    app.run()',
            language="python",
        )),
        MdiSubWindow("styles.css", IDEEditor(
            content=':root {\n  --miki-bg: #0f172a;\n  --miki-fg: #e2e8f0;\n  --miki-accent: #6366f1;\n  --miki-card: #1e293b;\n  --miki-border: #334155;\n}',
            language="css",
        )),
        class_="flex-1 bg-white",
    )

    bottom = SplitView(
        Div(
            TerminalWidget([
                "$ python -m mikiui dev",
                "INFO:     Uvicorn running on http://127.0.0.1:8000",
                "INFO:     Hot reload enabled",
                "$ ",
            ]),
            class_="h-full overflow-auto",
        ),
        Div(
            LogViewer(lines=[
                "info: Application started",
                ("info", "Hot reload watcher active"),
                ("warning", "Slow import: matplotlib (340ms)"),
                ("error", "ModuleNotFoundError: optional_dep (ignored)"),
            ], line_numbers=True),
            class_="h-full overflow-auto",
        ),
        orientation="vertical",
        class_="h-48",
    )

    return Div(
        MenuBar([
            ("File", [("New File", "/file/new"), ("Open", "/file/open"), ("Save", "/file/save"), ("Save As", "/file/saveas"), ("Exit", "/app/exit")]),
            ("Edit", [("Undo", "/edit/undo"), ("Redo", "/edit/redo"), ("Cut", "/edit/cut"), ("Copy", "/edit/copy"), ("Paste", "/edit/paste")]),
            ("View", [("Command Palette", "/view/palette"), ("Toggle Terminal", "/view/terminal"), ("Full Screen", "/view/fullscreen")]),
            ("Help", [("Documentation", "/help/docs"), ("Keyboard Shortcuts", "/help/shortcuts"), ("About", "/about")]),
        ]),
        Toolbar(
            Button("New", variant="secondary", class_="mr-1"),
            Button("Open", variant="secondary", class_="mr-1"),
            Button("Save", variant="secondary", class_="mr-1"),
            Div(class_="w-px h-6 bg-slate-300 mx-2"),
            Button("Run", variant="primary", class_="mr-1"),
            Button("Debug", variant="secondary", class_="mr-1"),
            Button("Stop", variant="secondary"),
            class_="px-2 py-1 border-b border-slate-200 bg-white",
        ),
        Div(
            file_tree,
            SplitView(editor, bottom, orientation="vertical", min_size=160),
            class_="flex flex-1 min-h-0",
        ),
        StatusBar(
            Div(P("main.py · Python"), class_="text-xs"),
            Div(P("Ln 12, Col 4"), class_="text-xs"),
            Div(P("UTF-8"), class_="text-xs"),
            Div(P("Spaces: 4"), class_="text-xs"),
            Div(P("Ready"), class_="text-xs"),
            class_="px-4 py-1 bg-slate-800 text-slate-300 text-xs border-t border-slate-700",
        ),
        class_="h-screen flex flex-col bg-white",
    )


@app.route("/about")
def about() -> Div:
    return Div(
        MessageBox(
            "About MikiUI Studio",
            "Version 0.1.0 — Built with MikiUI, FastAPI, and HTMX.\n© 2026 MikiUI Framework.",
            kind="info",
            buttons=[("Close", "/")],
        ),
        class_="p-8",
    )


@app.route("/file/open")
def open_file() -> Div:
    return Div(
        Navbar(brand="Studio"),
        Div(
            H1("Open File", class_="text-2xl font-bold mb-4"),
            FilePicker(name="file", accept=".py,.css,.md,.txt", label="Choose a file to open..."),
            class_="max-w-xl p-8",
        ),
    )


if __name__ == "__main__":
    app.run(desktop=True, width=1280, height=800)
