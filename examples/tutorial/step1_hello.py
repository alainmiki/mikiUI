"""Step 1: Hello World

The absolute minimum MikiUI app. One route, one component tree.
"""
from mikiui import MikiApp, Div, H1, P, Button

app = MikiApp(title="Step 1: Hello World")


@app.route("/")
def home():
    return Div(
        H1("Hello, MikiUI!"),
        P("You are looking at your first MikiUI app."),
        Button(
            "Say hello",
            variant="primary",
            onclick="alert('Hello from MikiUI!')",
        ),
        class_="flex flex-col items-center justify-center h-screen gap-4",
    )


if __name__ == "__main__":
    app.run()
