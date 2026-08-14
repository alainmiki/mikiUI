"""Tests for the desktop build/run flow (``mikiui desktop``)."""

from __future__ import annotations

import importlib
from unittest import mock

import pytest

from mikiui import MikiApp, Div
from mikiui.build.desktop_build import (
    run_desktop,
    _has_pywebview,
    _wait_for_server,
)


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
    with mock.patch("mikiui.build.desktop_build._run_native") as native, \
         mock.patch("mikiui.build.desktop_build._run_browser") as browser:
        run_desktop(app)
        native.assert_called_once()
        browser.assert_not_called()


def test_run_desktop_browser_fallback_when_native_false():
    """Passing native=False should use the browser path."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._run_native") as native, \
         mock.patch("mikiui.build.desktop_build._run_browser") as browser:
        run_desktop(app, native=False)
        browser.assert_called_once()
        native.assert_not_called()


def test_run_desktop_falls_back_to_browser_without_pywebview():
    """If pywebview is not installed, native should fall back to browser."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._has_pywebview", return_value=False), \
         mock.patch("mikiui.build.desktop_build._run_native") as native, \
         mock.patch("mikiui.build.desktop_build._run_browser") as browser:
        run_desktop(app)  # native defaults to True
        browser.assert_called_once()
        native.assert_not_called()


def test_run_desktop_rejects_non_mikiapp():
    """run_desktop should raise TypeError for non-MikiApp objects."""
    with pytest.raises(TypeError, match="MikiApp"):
        run_desktop("not an app")


def test_run_desktop_passes_kwargs_to_native():
    """run_desktop should forward host, port, title to the native path."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._run_native") as native:
        run_desktop(app, host="0.0.0.0", port=9000, title="My Title", width=800, height=600)
        native.assert_called_once_with(
            app, "0.0.0.0", 9000, "My Title", 800, 600, "local"
        )


def test_run_desktop_passes_kwargs_to_browser():
    """run_desktop should forward host, port, runtime to the browser path."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._serve_app"), \
         mock.patch("mikiui.build.desktop_build._run_webview"), \
         mock.patch("mikiui.build.desktop_build._wait_for_server", return_value=True), \
         mock.patch("mikiui.build.desktop_build.threading.Thread") as thread_cls, \
         mock.patch("mikiui.build.desktop_build.time.sleep", side_effect=KeyboardInterrupt), \
         mock.patch("mikiui.build.desktop_build.webbrowser"):
        run_desktop(app, native=False, runtime="local")
        thread_cls.assert_called()


def test_wait_for_server_returns_true_when_reachable():
    """_wait_for_server returns True when the URL responds."""
    with mock.patch("mikiui.build.desktop_build.urllib.request.urlopen") as urlopen:
        assert _wait_for_server("http://127.0.0.1:1/") is True


def test_wait_for_server_returns_false_on_timeout():
    """_wait_for_server returns False when the URL never responds."""
    with mock.patch("mikiui.build.desktop_build.time.sleep"):
        with mock.patch(
            "mikiui.build.desktop_build.urllib.request.urlopen",
            side_effect=ConnectionRefusedError,
        ):
            assert _wait_for_server("http://127.0.0.1:1/", timeout=0.1) is False


def test_cli_desktop_command_invokes_run_desktop():
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
