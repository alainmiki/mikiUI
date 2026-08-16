"""Playwright fixtures for E2E tests."""

from __future__ import annotations

import time

import pytest

from mikiui import Div, MikiApp
from mikiui.backend.server import create_app


def _create_test_app() -> MikiApp:
    app = MikiApp(title="MikiUI E2E Test")
    app.set_theme("light")

    @app.get("/")
    def home():
        return Div("Hello E2E")

    @app.get("/data")
    def data():
        return Div("Data Page")

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
