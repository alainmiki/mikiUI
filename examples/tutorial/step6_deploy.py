"""Step 6: Production-Ready App

Demonstrates a production-style MikiUI app with:
- Multiple routes
- State management
- Plugins
- Error handling
- Production build setup
"""
import os
from mikiui import MikiApp, Div, H1, P, Button, Navbar, Plugin, H2
from mikiui.components import Input, Form, SubmitButton, Label
from mikiui.widgets import (
    Hero,
    Footer,
    DataGrid,
    Card,
    MessageBox,
)
from mikiui.router import Router

app = MikiApp(
    title="Production App",
    lang="en",
)

# --- State ---
app.state.page_title = "Production App"
app.state.counter = 0


# --- Plugins ---

class SeoPlugin(Plugin):
    name = "seo"

    def on_render(self, tree):
        tree.append(
            Div(
                '<meta name="description" content="A production MikiUI app.">',
                class_="sr-only",
            )
        )
        return tree


class ErrorTrackerPlugin(Plugin):
    name = "error-tracker"

    def on_error(self, error, request):
        # TODO: Send to error tracking service
        print(f"Error tracked: {error}")


app.use(SeoPlugin())
app.use(ErrorTrackerPlugin())


# --- Admin Router ---

admin = Router(prefix="/admin")

@admin.get("/")
def admin_home():
    return Div(
        H1("Admin Dashboard"),
        P("Welcome to the admin area."),
        class_="p-8",
    )

@admin.get("/users")
def admin_users():
    return Div(
        H1("User Management"),
        DataGrid(
            columns=["ID", "Name", "Email", "Role"],
            rows=[
                ["1", "Alice", "alice@example.com", "Admin"],
                ["2", "Bob", "bob@example.com", "User"],
            ],
            sortable=True,
        ),
        class_="p-8",
    )

app.mount(admin)


# --- Main Routes ---

@app.route("/")
def home():
    return Div(
        Navbar(
            brand="Production App",
            links=[
                ("Home", "/"),
                ("Admin", "/admin"),
                ("About", "/about"),
            ],
            right=Button("Sign In", variant="ghost"),
        ),
        Hero(
            "Production-Ready MikiUI",
            subtitle="Multiple routes, state, plugins, and admin area.",
            action=Button("Get Started", variant="primary"),
        ),
        Div(
            H2("Features"),
            Card(
                "Multi-route app with router mounting.",
                title="Routing",
            ),
            Card(
                "Shared app.state for counters and settings.",
                title="State",
            ),
            Card(
                "SeoPlugin injects meta tags. ErrorTrackerPlugin logs errors.",
                title="Plugins",
            ),
            class_="max-w-4xl mx-auto p-8 grid gap-4",
        ),
        Footer(
            copyright="2026 Production App",
            social=[("GitHub", "https://github.com")],
        ),
        class_="min-h-screen flex flex-col",
    )


@app.route("/about")
def about():
    return Div(
        H1("About"),
        P("This app demonstrates production patterns in MikiUI."),
        P(f"Counter value: {app.state.counter}"),
        class_="max-w-2xl mx-auto p-8",
    )


@app.route("/counter")
def counter():
    app.state.counter += 1
    return Div(
        H1("Counter"),
        P(f"Count: {app.state.counter}"),
        Button("Increment", variant="primary"),
        class_="max-w-md mx-auto p-8",
    )


@app.route("/contact", methods=["GET", "POST"])
def contact(ctx=None):
    if ctx and ctx.request and ctx.request.method == "POST":
        ctx.form()
        return Div(
            MessageBox("Message sent!", type="success"),
            class_="max-w-md mx-auto p-8",
        )
    return Div(
        H1("Contact"),
        Form(
            Label("Name", for_="name"),
            Input(type="text", name="name", required=True),
            Label("Email", for_="email"),
            Input(type="email", name="email", required=True),
            SubmitButton("Send", variant="primary"),
            action="/contact",
            method="post",
        ),
        class_="max-w-md mx-auto p-8",
    )


if __name__ == "__main__":
    env = os.getenv("ENV", "dev")
    if env == "dev":
        app.run(host="127.0.0.1", port=8000, reload=True)
    else:
        app.run(host="0.0.0.0", port=8000)
