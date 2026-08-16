"""Step 4: Forms and Validation

Demonstrates form handling, validation states, and reading request data.
"""
from mikiui import MikiApp, Div, H1, P, Form
from mikiui.components import (
    Input,
    Textarea,
    Select,
    Option,
    Button,
    SubmitButton,
    Label,
)
from mikiui.widgets import MessageBox

app = MikiApp(title="Step 4: Forms")


@app.route("/")
def home():
    return Div(
        H1("Contact Form"),
        P("Fill out the form below. Validation is handled client-side and server-side."),
        contact_form(),
        class_="max-w-xl mx-auto p-8",
    )


def contact_form():
    return Form(
        Label("Name", for_="name"),
        Input(
            type="text",
            name="name",
            placeholder="Your name",
            required=True,
            state="default",
        ),

        Label("Email", for_="email"),
        Input(
            type="email",
            name="email",
            placeholder="you@example.com",
            required=True,
            state="default",
        ),

        Label("Subject", for_="subject"),
        Select(
            Option("General inquiry", value="general"),
            Option("Support", value="support"),
            Option("Sales", value="sales"),
            name="subject",
        ),

        Label("Message", for_="message"),
        Textarea(
            placeholder="How can we help?",
            name="message",
            rows=5,
        ),

        SubmitButton("Send Message", variant="primary"),

        action="/submit",
        method="post",
        class_="flex flex-col gap-4",
    )


@app.post("/submit")
def handle_submit(ctx):
    data = ctx.form() if ctx else {}
    name = data.get("name", "Anonymous")
    email = data.get("email", "")
    subject = data.get("subject", "general")
    message = data.get("message", "")

    # Simple validation
    if not name or not email or not message:
        return Div(
            MessageBox("Please fill in all required fields.", type="error"),
            contact_form(),
            class_="max-w-xl mx-auto p-8",
        )

    # TODO: Persist to database (MikiORM integration)
    return Div(
        MessageBox(
            f"Thanks {name}! We received your {subject} message.",
            type="success",
        ),
        P(f"We will reply to {email}."),
        Button("Send another", variant="secondary"),
        class_="max-w-xl mx-auto p-8",
    )


if __name__ == "__main__":
    app.run()
