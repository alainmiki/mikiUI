"""Step 2: Using Components

Demonstrates base HTML components: headings, paragraphs, images,
lists, tables, dialogs, and forms.
"""
from mikiui import (
    MikiApp,
    Div,
    H1,
    H2,
    P,
    Img,
    Ul,
    Li,
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    Button,
    Input,
    Form,
    Dialog,
)

app = MikiApp(title="Step 2: Components")


@app.route("/")
def home():
    return Div(
        H1("Component Gallery"),
        P("A tour of the base HTML components MikiUI provides."),

        H2("Image"),
        Img(
            src="https://via.placeholder.com/400x200",
            alt="Placeholder",
            width=400,
            height=200,
        ),

        H2("List"),
        Ul(
            Li("First item"),
            Li("Second item"),
            Li("Third item"),
        ),

        H2("Table"),
        Table(
            Thead(Tr(Th("Name"), Th("Role"), Th("Status"))),
            Tbody(
                Tr(Td("Alice"), Td("Admin"), Td("Active")),
                Tr(Td("Bob"), Td("User"), Td("Inactive")),
            ),
        ),

        H2("Dialog"),
        Dialog(
            Button("Close", onclick="this.closest('dialog').close()"),
            title="Sample Dialog",
            open=False,
        ),

        class_="max-w-2xl mx-auto p-8 space-y-6",
    )


@app.route("/form")
def form_demo():
    return Form(
        Input(type="text", placeholder="Your name", name="name"),
        Input(type="email", placeholder="you@example.com", name="email"),
        Button("Submit", type="submit", variant="primary"),
        action="/form",
        method="post",
        class_="flex flex-col gap-4 max-w-md mx-auto p-8",
    )


if __name__ == "__main__":
    app.run()
