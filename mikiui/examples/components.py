"""MikiUI Components module.

Submodule for the examples app - contains component showcase routes.

Usage:
    from mikiui.examples.components import app
    # app has routes: /components, /tables, /forms
"""

from __future__ import annotations

from mikiui import MikiApp, Div, H1, H2, P, A, Button
from mikiui.components import (
    Navbar,
    H1, H2, H3, P as PComp, A as AComp, Span, Button as ButtonComp, SubmitButton,
    Input, Textarea, Checkbox, Radio, Select, Option, Label, Form,
    Table, Thead, Tbody, Tr, Th, Td, Caption,
    Dialog, Details, Summary,
    Ul, Ol, Li,
    Img, Figure, Figcaption,
    Code, Blockquote, Mark, Small, Em, Strong,
    Progress, Meter,
)

app = MikiApp(title="MikiUI Components")


def Group(title, *children):
    return Div(H2(title), *children, class_="space-y-4")


@app.route("/")
def home():
    """All HTML components showcase."""
    return Div(
        Navbar(
            brand="MikiUI Components",
            links=[
                ("Home", "/"),
                ("Headings", "#headings"),
                ("Lists", "#lists"),
                ("Media", "#media"),
            ],
        ),
        Div(
            H1("MikiUI Components Demo"),
            PComp("This demo showcases all base HTML components."),
            Group("Text Elements",
                H2("Headings"),
                Div(H1("H1 Title"), H2("H2 Subtitle"), H3("H3 Sub-subtitle"), class_="space-y-1"),
                PComp("Paragraph with "),
                AComp("link", href="#"),
                Span(" inline span"),
                Strong(" bold"),
                Em(" emphatic"),
                Mark(" highlighted"),
                Code("code()"),
                Small("small"),
                class_="space-y-2",
            ),
            Group("Lists & Media",
                H2("Lists"),
                Ul(Li("List item 1"), Li("List item 2"), Li("List item 3")),
                Ol(Li("Ordered 1"), Li("Ordered 2")),
                H2("Media"),
                Figure(
                    Img(src="https://via.placeholder.com/80", alt="Placeholder"),
                    Figcaption("Figure caption"),
                ),
            ),
            Group("Tables",
                H2("Table Example"),
                Table(
                    Caption("User Data"),
                    Thead(Tr(Th("Name"), Th("Email"))),
                    Tbody(Tr(Td("Alice"), Td("alice@example.com"))),
                ),
            ),
            Group("Forms",
                H2("Form Example"),
                Form(
                    Div(
                        Label("Name:"),
                        Input(type="text", name="name", placeholder="Enter name"),
                        Label("Email:"),
                        Input(type="email", name="email"),
                        ButtonComp("Submit", variant="primary"),
                        class_="space-y-3",
                    ),
                ),
            ),
            class_="space-y-6",
        ),
        class_="p-6 max-w-3xl mx-auto",
    )


@app.route("/advanced")
def advanced():
    """Advanced components like progress, meter, calendar."""
    return Div(
        Navbar(
            brand="MikiUI Components",
            links=[("Home", "/"), ("Progress", "#progress")],
        ),
        Group("Progress & Meter",
            PComp("Progress: 75%"),
            Progress(value=75),
            PComp("Meter: 75/100"),
            Meter(value=75, min=0, max=100),
        ),
        class_="p-6",
    )


@app.route("/dialogs")
def dialogs():
    """Dialog and modal examples."""
    return Div(
        Navbar(
            brand="MikiUI Components",
            links=[("Home", "/"), ("Dialogs", "/dialogs")],
        ),
        Group("Dialogs",
            Button("Open Dialog", onclick="document.querySelector('dialog').showModal()"),
            Dialog("Dialog Title", "Dialog content here."),
        ),
        class_="p-6",
    )


@app.route("/media")
def media():
    """Media components like date picker, file picker, chart."""
    from mikiui.widgets import Calendar, FilePicker, Chart
    from mikiui.widgets import ColorPicker, DatePicker
    
    return Div(
        Navbar(
            brand="MikiUI Components",
            links=[("Home", "/"), ("Media", "#media")],
        ),
        Group("Date & Color Pickers",
            DatePicker(label="Pick Date:", name="date"),
            ColorPicker(label="Pick Color:", name="color"),
        ),
        Group("Calendar",
            Calendar(),
        ),
        Group("File Picker",
            FilePicker(label="Choose file:"),
        ),
        class_="p-6",
    )