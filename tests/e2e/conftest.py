"""Playwright fixtures for E2E tests."""

from __future__ import annotations

import time

import pytest

from mikiui import Div, MikiApp
from mikiui.backend.server import create_app
from mikiui.components import BottomSheet
from mikiui.widgets import Dial, Drawer


def _create_test_app() -> MikiApp:
    app = MikiApp(title="MikiUI E2E Test")
    app.set_theme("light")

    @app.get("/")
    def home():
        from mikiui import H4, Button, Div, P
        return Div(
            Div("Hello E2E"),
            Div(
                Button("Open Drawer", onclick="mikiDrawer.open('.test-drawer')"),
                Drawer(
                    Div(
                        H4("Test Drawer"),
                        P("This is a test drawer accessible via JS API."),
                        Button("Close", onclick="mikiDrawer.close('.test-drawer')"),
                    ),
                    title="Drawer",
                    side="left",
                    open=False,
                    class_="test-drawer",
                ),
                style="margin: 1rem",
            ),
            Div(
                Button("Open Bottom Sheet", onclick="mikiBottomSheet.open('.test-bottomsheet')"),
                BottomSheet(
                    Div(
                        P("This is a test bottom sheet."),
                        Button("Close", onclick="mikiBottomSheet.close('.test-bottomsheet')"),
                    ),
                    title="Bottom Sheet",
                    size="md",
                    class_="test-bottomsheet",
                ),
                style="margin: 1rem",
            ),
            Div(
                Dial(value=50, min=0, max=100, step=5, size=140),
                style="margin: 1rem",
            ),
        )

    @app.get("/data")
    def data():
        from mikiui import Tabs
        from mikiui.widgets import KanbanBoard, SplitView
        return Div(
            Div(
                SplitView(
                    Div("Left pane", style="height:200px"),
                    Div("Right pane", style="height:200px"),
                    orientation="horizontal",
                    min_size=100,
                    resize_mode="both",
                ),
                style="height:300px",
            ),
            Tabs(
                [("Tab 1", Div("Content 1")), ("Tab 2", Div("Content 2"))],
                id="data-tabs",
            ),
            KanbanBoard(
                columns={
                    "TODO": ["Task A", "Task B"],
                    "IN PROGRESS": ["Task C"],
                    "DONE": ["Task D"],
                }
            ),
            style="max-width:800px; margin:0 auto; padding:1rem",
        )

    @app.get("/forms")
    def forms():
        from mikiui.components import Form, Input, SubmitButton
        return Form(
            Input(name="name", placeholder="Enter name"),
            SubmitButton("Submit"),
            action="/submit",
        )

    @app.post("/submit")
    def submit(ctx, name):
        return Div(f"Submitted: {name}")

    return app


@pytest.fixture(scope="session")
def test_app():
    return _create_test_app()


@pytest.fixture(scope="session")
def server(test_app):
    import uvicorn

    fastapi_app = create_app(test_app)
    config = uvicorn.Config(fastapi_app, host="127.0.0.1", port=8765, log_level="warning")
    server = uvicorn.Server(config)
    thread = __import__("threading").Thread(target=server.run, daemon=True)
    thread.start()

    for _ in range(50):
        try:
            import urllib.request
            urllib.request.urlopen("http://127.0.0.1:8765/", timeout=0.5)
            break
        except Exception:
            time.sleep(0.2)
    else:
        raise RuntimeError("Test server failed to start")

    yield {"url": "http://127.0.0.1:8765", "app": test_app, "server": server, "thread": thread}

    if hasattr(server, "should_exit"):
        server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture()
def page(server, playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(base_url=server["url"])
    page = context.new_page()
    yield page
    context.close()
    browser.close()
