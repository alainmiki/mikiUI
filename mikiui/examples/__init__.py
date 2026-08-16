"""MikiUI example applications.

This package contains multiple example apps demonstrating different MikiUI features.
Each file defines an `app` variable that is a MikiApp instance.

Usage:
    mikiui dev --app mikiui.examples.components:app
    mikiui dev --app mikiui.examples.widgets:app
    mikiui dev --app mikiui.examples.layouts:app
    mikiui dev --app mikiui.examples.forms:app
"""

from mikiui import MikiApp

app = MikiApp(title="MikiUI Examples")

@app.route("/")
def home():
    from mikiui import H1, A, Div, P
    return Div(
        H1("MikiUI Examples"),
        P("Choose an example app:"),
        [
            A("Components Demo", href="/components"),
            A(" | ", class_="mx-2"),
            A("Widgets Demo", href="/widgets"),
            A(" | ", class_="mx-2"),
            A("Layouts Demo", href="/layouts"),
            A(" | ", class_="mx-2"),
            A("Forms Demo", href="/forms"),
        ],
        class_="space-y-4 p-6",
    )