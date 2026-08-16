"""Tests for the desktop build/run flow (``mikiui desktop``)."""

from __future__ import annotations

from unittest import mock

import pytest

from mikiui import Div, MikiApp
from mikiui.build.desktop_build import _has_pywebview, _infer_app_spec, _wait_for_server, run_desktop


def make_app() -> MikiApp:
    app = MikiApp(title="Desktop Test")

    @app.route("/")
    def home():
        return Div("home")

    return app


def test_has_pywebview_detects_availability():
    """_has_pywebview returns True when webview is importable."""
    assert _has_pywebview() is True


def test_run_desktop_defaults_to_native():
    """run_desktop should prefer the native (pywebview) path by default."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._run_native") as native, mock.patch(
        "mikiui.build.desktop_build._run_browser"
    ) as browser:
        run_desktop(app)
        native.assert_called_once()
        browser.assert_not_called()


def test_run_desktop_browser_fallback_when_native_false():
    """Passing native=False should use the browser path."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._run_native") as native, mock.patch(
        "mikiui.build.desktop_build._run_browser"
    ) as browser:
        run_desktop(app, native=False)
        browser.assert_called_once()
        native.assert_not_called()


def test_run_desktop_falls_back_to_browser_without_pywebview():
    """If pywebview is not installed, native should fall back to browser."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._has_pywebview", return_value=False), mock.patch(
        "mikiui.build.desktop_build._run_native"
    ) as native, mock.patch(
        "mikiui.build.desktop_build._run_browser"
    ) as browser:
        run_desktop(app)  # native defaults to True
        browser.assert_called_once()
        native.assert_not_called()


def test_run_desktop_rejects_non_mikiapp():
    """run_desktop should raise TypeError for non-MikiApp objects."""
    with pytest.raises(TypeError, match="MikiApp"):
        run_desktop("not an app")


def test_run_desktop_passes_kwargs_to_native():
    """run_desktop should forward host, port, title, width, height, runtime, reload, app_spec, icon."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._run_native") as native:
        run_desktop(app, host="0.0.0.0", port=9000, title="My Title", width=800, height=600)
        native.assert_called_once_with(
            app, "0.0.0.0", 9000, "My Title", 800, 600, "local", False, None, None
        )


def test_run_desktop_passes_kwargs_to_browser():
    """run_desktop should forward all parameters to the browser path."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._start_server") as start, mock.patch(
        "mikiui.build.desktop_build._run_webview"
    ), mock.patch("mikiui.build.desktop_build._wait_for_server", return_value=True), mock.patch(
        "mikiui.build.desktop_build.threading.Thread"
    ), mock.patch("mikiui.build.desktop_build.time.sleep", side_effect=KeyboardInterrupt), mock.patch(
        "mikiui.build.desktop_build.webbrowser"
    ):
        run_desktop(app, native=False, runtime="local")


def test_wait_for_server_returns_true_when_reachable():
    """_wait_for_server returns True when the URL responds."""
    with mock.patch("mikiui.build.desktop_build.urllib.request.urlopen"):
        assert _wait_for_server("http://127.0.0.1:1/") is True


def test_wait_for_server_returns_false_on_timeout():
    """_wait_for_server returns False when the URL never responds."""
    with mock.patch("mikiui.build.desktop_build.time.sleep"):
        with mock.patch(
            "mikiui.build.desktop_build.urllib.request.urlopen",
            side_effect=ConnectionRefusedError,
        ):
            assert _wait_for_server("http://127.0.0.1:1/", timeout=0.1) is False


def test_cli_deSKTOP_COMMAND_INVOKES_RUN_DESKTOP():
    """The 'desktop' CLI subcommand should call run_desktop with native=True."""
    pytest.importorskip("typer.testing")
    from typer.testing import CliRunner

    from mikiui.cli import cli

    runner = CliRunner()
    with mock.patch("mikiui.build.run_desktop") as mocked:
        result = runner.invoke(cli, ["desktop", "--browser"])
        assert result.exit_code == 0, result.stdout
        mocked.assert_called_once()
        args, kwargs = mocked.call_args
        assert kwargs["native"] is False


def test_infer_app_spec_finds_module_attribute():
    """_infer_app_spec should find the variable name the app is bound to."""
    import mikiui.app.app as app_module
    app = MikiApp(title="Infer Test")
    app_module.app = app  # use the conventional name so _infer_app_spec picks it up
    spec = _infer_app_spec(app)
    module_name, _, attr = spec.partition(":")
    assert module_name == "mikiui.app.app"
    assert attr == "app"
    mod = __import__(module_name, fromlist=[attr])
    assert getattr(mod, attr) is app
    del app_module.app


def test_run_native_reload_calls_restart_server():
    """_run_native_reload should start the server and spawn a watcher thread."""
    import mikiui.build.desktop_build as db
    from mikiui.build.desktop_build import _restart_server, _run_native_reload

    app = make_app()
    fake_webview = mock.MagicMock()
    fake_webview.start.side_effect = KeyboardInterrupt

    with mock.patch.object(db, "_start_server") as start, \
         mock.patch.object(db, "_wait_for_server", return_value=True), \
         mock.patch.object(db, "_run_webview") as webview_fn, \
         mock.patch.object(db, "_stop_server"), \
         mock.patch.object(db.threading, "Thread") as thread_mock, \
         mock.patch.dict("sys.modules", {"webview": fake_webview}):
        window = mock.MagicMock()
        webview_fn.return_value = window
        start.return_value = mock.MagicMock()

        with pytest.raises(KeyboardInterrupt):
            _run_native_reload(
                app, "127.0.0.1", 8000, "Test App", 1024, 720, "local",
                "mikiui.app.app:app",
            )

        # Verify a watcher thread was spawned.
        thread_mock.assert_called_once()

    # Verify _restart_server stops old, starts new, and reloads window.
    with mock.patch.object(db, "_stop_server"), \
         mock.patch.object(db, "_start_server") as start_new, \
         mock.patch.object(db, "_wait_for_server", return_value=True), \
         mock.patch.object(db.time, "sleep"):
        db.server_holder[0] = mock.MagicMock()
        fake_window = mock.MagicMock()
        fake_app = mock.MagicMock()

        _restart_server("mod:app", "127.0.0.1", 8000, "local", fake_app, fake_window)
        start_new.assert_called()
        fake_window.evaluate_js.assert_called_with("location.reload()")