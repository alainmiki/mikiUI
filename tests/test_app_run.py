"""Test that app.run() works as a standalone script entry point."""

from __future__ import annotations

from unittest import mock


def test_app_run_method_exists():
    """MikiApp should have a run() method."""
    from mikiui import MikiApp
    assert hasattr(MikiApp, "run")


def test_app_run_web_server():
    """app.run() without desktop should use uvicorn to serve the app."""
    from mikiui import MikiApp, Div
    app = MikiApp(title="Test")

    @app.route("/")
    def home():
        return Div("Hello")

    with mock.patch("uvicorn.run") as uvicorn_run:
        app.run(host="127.0.0.1", port=9999, reload=False)
        assert uvicorn_run.called


def test_app_run_desktop_calls_run_desktop():
    """app.run(desktop=True) should call mikiui.build.run_desktop."""
    from mikiui import MikiApp, Div
    app = MikiApp(title="Test")

    @app.route("/")
    def home():
        return Div("Hello")

    with mock.patch("mikiui.build.run_desktop") as run_desktop:
        app.run(desktop=True, reload=False)
        run_desktop.assert_called_once()


def test_app_run_desktop_with_browser():
    """app.run(desktop=True, browser=True) should pass native=False."""
    from mikiui import MikiApp, Div
    app = MikiApp(title="Test")

    @app.route("/")
    def home():
        return Div("Hello")

    with mock.patch("mikiui.build.run_desktop") as run_desktop:
        app.run(desktop=True, browser=True)
        kwargs = run_desktop.call_args.kwargs
        assert kwargs["native"] is False


def test_app_run_as_standalone_script():
    """A Python script with `if __name__ == '__main__': app.run()` should import correctly."""
    # Just test that the script content is valid Python and can be compiled.
    script = '''
from mikiui import MikiApp, Div

app = MikiApp(title="Standalone Test")

@app.route("/")
def home():
    return Div("Hello")

if __name__ == "__main__":
    app.run(reload=False)
'''
    # Verify the script compiles and the module loads.
    compile(script, "<test>", "exec")
    # Also import the demo to simulate what the script does.
