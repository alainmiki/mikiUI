"""MikiUI Layouts demo.

Shows layout widgets including SplitView, DockablePanel, TabbedPanel, and SidePanel.
"""

from __future__ import annotations

from mikiui import MikiApp, Div, H1, H3, Button, P
from mikiui.components import Dialog, Tabs
from mikiui.widgets import (
    SplitView,
    DockablePanel,
    TabbedPanel,
    SidePanel,
    CollapsiblePanel,
    ScrollPanel,
    GroupBox,
)

app = MikiApp(title="MikiUI Layouts Demo")


@app.route("/")
def home():
    return Div(
        H1("MikiUI Layouts Demo"),
        P("Layout widgets for building complex UIs."),
        class_="p-6 max-w-4xl mx-auto",
    )


@app.route("/splitview")
def splitview_demo():
    """Horizontal and vertical split views."""
    return Div(
        H1("SplitView Demo"),
        GroupBox(
            "Horizontal Split",
            SplitView(
                Div(
                    "File Explorer",
                    class_="border-r border-gray-300 pr-2",
                ),
                Div("Editor"),
                orientation="horizontal",
            ),
        ),
        GroupBox(
            "Vertical Split",
            SplitView(
                Div("Top Content"),
                Div("Bottom Content"),
                orientation="vertical",
            ),
        ),
        class_="p-6 space-y-6",
    )


@app.route("/dockable")
def dockable_demo():
    """Dockable panels (like VS Code panels)."""
    return Div(
        H1("Dockable Panel Demo"),
        P("Panels that can be docked to any side."),
        Div(
            DockablePanel(
                "Explorer",
                P("File tree would go here"),
            ),
            DockablePanel(
                "Properties",
                Div("Selected item details here"),
            ),
            class_="flex space-x-4",
        ),
        class_="p-6",
    )


@app.route("/tabs")
def tabs_demo():
    """Tabbed interfaces."""
    return Div(
        H1("Tabbed Interface Demo"),
        TabbedPanel([
            ("Overview", Div(
                H3("Overview Tab"),
                P("Welcome to the overview tab."),
                class_="space-y-2",
            )),
            ("Editor", Div(
                H3("Editor Tab"),
                P("This could be a code editor."),
                Dialog(
                    H1("Dialog Example"),
                    P("Click outside or press Esc to close."),
                    Button("Close", onclick="this.closest('dialog').close()"),
                ),
                Button("Open Dialog", onclick="document.querySelector('dialog').showModal()"),
                class_="space-y-2",
            )),
            ("Settings", Div(
                H3("Settings Tab"),
                FormControls(),
            )),
        ]),
        class_="p-6",
    )


@app.route("/sidepanel")
def sidepanel_demo():
    """Side panels (like VS Code sidebar)."""
    return Div(
        H1("Side Panel Demo"),
        SidePanel(
            "left",
            Div(
            Button("Home", onclick="alert('Home')", class_="w-full mb-2"),
            Button("Explorer", onclick="alert('Explorer')", class_="w-full mb-2"),
            Button("Debug", onclick="alert('Debug')", class_="w-full mb-2"),
                class_="space-y-2",
            ),
        ),
        Div(
            "Main Content",
            class_="ml-[300px] p-6",
        ),
        class_="min-h-screen",
    )


@app.route("/collapsible")
def collapsible_demo():
    """Collapsible panels and accordions."""
    return Div(
        H1("Collapsible Panels Demo"),
        CollapsiblePanel("Section 1", P("Content for section 1."), open=True),
        CollapsiblePanel("Section 2", P("Content for section 2.")),
        CollapsiblePanel("Section 3", P("Content for section 3.")),
        class_="p-6",
    )


@app.route("/scroll")
def scroll_demo():
    """Scrollable panels."""
    return Div(
        H1("Scroll Panel Demo"),
        ScrollPanel(
            Div(
                *[P(f"Line {i}") for i in range(1, 50)],
            ),
            style="height: 300px",
        ),
        class_="p-6",
    )


def FormControls():
    from mikiui.components import Form, Input, Select, Option, SubmitButton, Label
    return Form(
        Div(
            Label("Name:", for_="name"),
            Input(type="text", name="name", id="name"),
            Label("Email:", for_="email"),
            Input(type="email", name="email", id="email"),
            class_="space-y-3",
        ),
        SubmitButton("Save"),
    )