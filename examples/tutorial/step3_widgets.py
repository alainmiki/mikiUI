"""Step 3: Using Widgets

Demonstrates high-level widgets built from components:
Hero, Footer, DataGrid, Card, Carousel, and TabbedPanel.
"""
from mikiui import MikiApp, Div,Button
from mikiui.widgets import (
    Hero,
    Footer,
    DataGrid,
    Card,
    Carousel,
    TabbedPanel,
    Badge,
    Progress,

)

app = MikiApp(title="Step 3: Widgets")


@app.route("/")
def home():
    return Div(
        Hero(
            "Widget Gallery",
            subtitle="High-level composite components for common UI patterns.",
            action=Button("Get Started", variant="primary"),
        ),

        Div(
            H2("DataGrid"),
            P("Sortable and filterable data tables."),
            DataGrid(
                columns=["Name", "Email", "Role"],
                rows=[
                    ["Alice", "alice@example.com", "Admin"],
                    ["Bob", "bob@example.com", "User"],
                    ["Carol", "carol@example.com", "Admin"],
                ],
                sortable=True,
                filterable=False,
                page_size=5,
            ),
            class_="max-w-4xl mx-auto p-8",
        ),

        Div(
            H2("Cards"),
            Card(
                "Card body content goes here.",
                title="Sample Card",
                footer="Footer info",
            ),
            class_="max-w-4xl mx-auto p-8",
        ),

        Div(
            H2("Carousel"),
            Carousel(
                ("https://via.placeholder.com/600x300?text=Slide+1", "Slide 1"),
                ("https://via.placeholder.com/600x300?text=Slide+2", "Slide 2"),
                autoplay=True,
                interval=4000,
            ),
            class_="max-w-4xl mx-auto p-8",
        ),

        Div(
            H2("Tabs"),
            TabbedPanel(
                ("Tab A", Div("Content for tab A")),
                ("Tab B", Div("Content for tab B")),
                ("Tab C", Div("Content for tab C")),
            ),
            class_="max-w-4xl mx-auto p-8",
        ),

        H2("Small Widgets"),
        Div(
            Badge("New", variant="success"),
            Badge("Beta", variant="warning"),
            Progress(75, label="Loading", variant="primary"),
            class_="max-w-4xl mx-auto p-8 flex gap-4 items-center",
        ),

        Footer(
            copyright="MikiUI Tutorial — Step 3",
            social=[("Docs", "https://kilo.ai/docs")],
        ),
    )


# Import H2 and P locally for cleaner route handlers
from mikiui.components import H2, P  # noqa: E402

if __name__ == "__main__":
    app.run()
