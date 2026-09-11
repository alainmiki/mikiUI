"""Tests for the desktop build/run flow (``mikiui desktop``)."""

from __future__ import annotations

import os
from unittest import mock

import pytest

from mikiui import Div, MikiApp
from mikiui.build.desktop_build import (
    _create_platform_bundle,
    _has_pywebview,
    _infer_app_spec,
    _wait_for_server,
    build_desktop,
    run_desktop,
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
        args, kwargs = native.call_args
        assert args[:8] == (app, "0.0.0.0", 9000, "My Title", 800, 600, "local", False)
        assert args[8] is not None  # icon defaults to runtime icon


def test_run_desktop_passes_icon_to_run_native():
    """run_desktop should forward the icon parameter to _run_native."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._run_native") as native:
        run_desktop(app, icon="/path/to/icon.ico")
        args, kwargs = native.call_args
        assert args[8] == os.path.abspath("/path/to/icon.ico")


def test_default_desktop_icon_returns_ico_on_windows():
    """_default_desktop_icon should return .ico path on Windows."""
    from mikiui.build.desktop_build import _default_desktop_icon
    with mock.patch("mikiui.build.desktop_build.platform.system", return_value="Windows"):
        icon_path = _default_desktop_icon()
        assert icon_path.endswith("mikiui-icon.ico")
        assert os.path.exists(icon_path)


def test_default_desktop_icon_returns_png_on_non_windows():
    """_default_desktop_icon should return .png path on macOS/Linux."""
    from mikiui.build.desktop_build import _default_desktop_icon
    with mock.patch("mikiui.build.desktop_build.platform.system", return_value="Linux"):
        icon_path = _default_desktop_icon()
        assert icon_path.endswith("mikiui-icon.png")
        assert os.path.exists(icon_path)


def test_default_desktop_icon_returns_png_on_macos():
    """_default_desktop_icon should return .png path on macOS (NSImage accepts PNG)."""
    from mikiui.build.desktop_build import _default_desktop_icon
    with mock.patch("mikiui.build.desktop_build.platform.system", return_value="Darwin"):
        icon_path = _default_desktop_icon()
        assert icon_path.endswith("mikiui-icon.png")
        assert os.path.exists(icon_path)


def test_run_desktop_falls_back_to_app_desktop_icon():
    """run_desktop should use miki_app.desktop_icon when icon is not provided."""
    app = make_app()
    app.desktop_icon = "/path/to/desktop_icon.ico"
    with mock.patch("mikiui.build.desktop_build._run_native") as native:
        run_desktop(app)
        args, kwargs = native.call_args
        assert args[8] == os.path.abspath("/path/to/desktop_icon.ico")


def test_run_desktop_reload_falls_back_to_app_desktop_icon():
    """run_desktop with reload=True should use miki_app.desktop_icon as icon fallback."""
    app = make_app()
    app.desktop_icon = "/path/to/desktop_icon.ico"
    import mikiui.build.desktop_build as db
    with mock.patch.object(db, "_run_native_reload") as reload_fn:
        run_desktop(app, reload=True)
        args, kwargs = reload_fn.call_args
        assert kwargs.get("icon") == os.path.abspath("/path/to/desktop_icon.ico")


def test_run_desktop_passes_kwargs_to_browser():
    """run_desktop should forward all parameters to the browser path."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._start_server"), mock.patch(
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
    from mikiui.cli import commands as cmd_mod

    runner = CliRunner()
    fake_app = make_app()

    import mikiui.app.app as app_module

    original_app = getattr(app_module, "app", None)
    app_module.app = fake_app
    try:
        with mock.patch.object(cmd_mod, "_safe_resolve", return_value="mikiui.app.app:app"), mock.patch(
            "mikiui.build.run_desktop"
        ) as mocked:
            result = runner.invoke(cli, ["desktop", "--browser"])
            assert result.exit_code == 0, result.stdout
            mocked.assert_called_once()
            args, kwargs = mocked.call_args
            assert kwargs["native"] is False
    finally:
        if original_app is None:
            delattr(app_module, "app")
        else:
            app_module.app = original_app


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
         mock.patch.object(db, "_webview", fake_webview):
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


def test_ensure_pyinstaller_installs_missing_package(tmp_path):
    """_ensure_pyinstaller should attempt pip install when PyInstaller is missing."""
    import mikiui.build.desktop_build as db

    fake_proc = mock.MagicMock()
    fake_proc.returncode = 0
    fake_proc.stderr = ""

    import builtins
    original_import = builtins.__import__
    call_count = {"pyinstaller": 0}

    def fake_import(name, *args, **kwargs):
        if name == "PyInstaller.__main__":
            call_count["pyinstaller"] += 1
            if call_count["pyinstaller"] == 1:
                raise ImportError("no PyInstaller")
            # Second call: return a fake module
            fake_mod = mock.MagicMock()
            return fake_mod
        return original_import(name, *args, **kwargs)

    with mock.patch.object(builtins, "__import__", side_effect=fake_import), \
         mock.patch("subprocess.run", return_value=fake_proc) as run_mock:
        result = db._ensure_pyinstaller()
        assert result == (True, None)
        run_mock.assert_called_once()


def test_build_desktop_report_includes_warning_and_bundle(tmp_path):
    """build_desktop should include warning and bundle fields in the report."""
    app = make_app()
    with mock.patch("mikiui.build.desktop_build._build_web_for_desktop"), \
         mock.patch("mikiui.build.desktop_build._infer_app_spec", return_value="mikiui.app.app:app"), \
         mock.patch("mikiui.build.desktop_build._write_pyinstaller_spec", return_value=(None, "PyInstaller missing")), \
         mock.patch("mikiui.build.desktop_build._create_platform_bundle", return_value=None), \
         mock.patch("mikiui.build.desktop_build.platform.system", return_value="Linux"):
        report = build_desktop(app, out_dir=str(tmp_path), app_spec="mikiui.app.app:app")
        assert "warning" in report
        assert "bundle" in report
        assert report["status"] == "partial"


def test_build_desktop_report_includes_bundle_on_success(tmp_path):
    """build_desktop should include bundle path when PyInstaller succeeds."""
    app = make_app()
    fake_spec = str(tmp_path / "mikiui_linux.spec")
    with mock.patch("mikiui.build.desktop_build._build_web_for_desktop"), \
         mock.patch("mikiui.build.desktop_build._infer_app_spec", return_value="mikiui.app.app:app"), \
         mock.patch("mikiui.build.desktop_build._write_pyinstaller_spec", return_value=(fake_spec, None)), \
         mock.patch("mikiui.build.desktop_build._create_platform_bundle", return_value=str(tmp_path / "mikiui_app")), \
         mock.patch("mikiui.build.desktop_build.platform.system", return_value="Linux"):
        report = build_desktop(app, out_dir=str(tmp_path), app_spec="mikiui.app.app:app")
        assert report["status"] == "ok"
        assert report["bundle"] is not None


def test_create_platform_bundle_returns_none_when_executable_missing(tmp_path):
    """_create_platform_bundle should return None if PyInstaller output is missing."""
    with mock.patch("mikiui.build.desktop_build.platform.system", return_value="Linux"):
        result = _create_platform_bundle(str(tmp_path), "Test", None)
        assert result is None


def test_create_platform_bundle_creates_macos_app(tmp_path):
    """_create_platform_bundle should create a .app bundle on macOS."""
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    # PyInstaller on macOS produces a .app bundle directory with the binary
    # inside Contents/MacOS/, so replicate that structure here.
    executable_name = "mikiui_app.app"
    executable = dist_dir / executable_name
    macos_dir = executable / "Contents" / "MacOS"
    macos_dir.mkdir(parents=True)
    (macos_dir / "mikiui_app").write_text("fake binary")
    web_dir = tmp_path / "web"
    web_dir.mkdir()
    (web_dir / "index.html").write_text("<html></html>")
    icon = tmp_path / "icon.icns"
    icon.write_text("fake icns")

    with mock.patch("mikiui.build.desktop_build.platform.system", return_value="Darwin"), \
         mock.patch("mikiui.build.desktop_build._platform_executable_name", return_value=executable_name):
        result = _create_platform_bundle(str(tmp_path), "MyApp", str(icon))

    assert result is not None
    assert result.endswith(".app")
    assert os.path.isdir(result)
    contents = os.path.join(result, "Contents")
    assert os.path.isdir(os.path.join(contents, "MacOS"))
    assert os.path.isdir(os.path.join(contents, "Resources"))
    assert os.path.isfile(os.path.join(contents, "Info.plist"))