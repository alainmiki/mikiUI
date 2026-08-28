"""Desktop build/run support for MikiUI (native pywebview + browser fallback).

The public entry point is :func:`run_desktop`, used by ``mikiui desktop`` and
``app.run(desktop=True)``.  It prefers a native pywebview window; when pywebview
is unavailable (or ``native=False`` is passed) it falls back to opening the
system browser against a local FastAPI server.

Build-time packaging lives in :func:`build_desktop`, which produces a
distributable directory or PyInstaller spec for desktop deployment.
"""

from __future__ import annotations

import importlib
import os
import platform
import sys
import tempfile
import threading
import time
import urllib.request
import webbrowser
from typing import Any

try:  # pragma: no cover - optional dependency
    import webview as _webview
except Exception:  # pragma: no cover
    _webview = None  # type: ignore[assignment]


def _has_pywebview() -> bool:
    """Return True if the ``webview`` (pywebview) package is importable."""
    return "webview" in sys.modules


def _import_webview() -> Any | None:
    """Import the ``webview`` module, returning ``None`` if unavailable."""
    return sys.modules.get("webview")


def _infer_app_spec(app: Any) -> str:
    """Return a ``"module:attr"`` spec for *app* by inspecting its module.

    Checks common attribute names (``app``, ``application``, ``miki_app``)
    across all loaded modules to find where *app* was defined as a global.
    """
    # First try the app's __module__ (works for classes defined in same module)
    mod_name = getattr(app, "__module__", "")
    if mod_name:
        mod = sys.modules.get(mod_name)
        if mod:
            for attr in ("app", "application", "miki_app"):
                if getattr(mod, attr, None) is app:
                    return f"{mod.__name__}:{attr}"

    # Search all loaded modules for the app instance
    for mod_name, mod in list(sys.modules.items()):
        if mod is None:
            continue
        for attr in ("app", "application", "miki_app"):
            try:
                if getattr(mod, attr, None) is app:
                    return f"{mod_name}:{attr}"
            except Exception:
                continue
        # Also scan for any attribute matching
        try:
            for name, val in vars(mod).items():
                if val is app and not name.startswith("_"):
                    return f"{mod_name}:{name}"
        except Exception:
            continue

    return f"{mod_name or 'app'}:app"


def _start_server(miki_app: Any, host: str, port: int, runtime: str = "local") -> Any:
    """Start a FastAPI/uvicorn server in a background thread. Returns holder."""
    import socket

    import uvicorn

    from ..backend import create_app

    fastapi_app = create_app(miki_app, runtime=runtime)
    config = uvicorn.Config(
        fastapi_app,
        host=host,
        port=port,
        log_level="warning",
        timeout_graceful_shutdown=2,
    )
    # Create a socket with SO_REUSEADDR to allow quick rebinding after restart
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(128)
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()
    return {"server": server, "thread": thread, "config": config, "port": port, "socket": sock}


def _stop_server(holder: Any, timeout: float = 5.0) -> None:
    """Stop a server previously started by :func:`_start_server`.

    Signals the uvicorn server to exit (sets ``should_exit``) and waits up
    to *timeout* seconds for the server thread to fully exit so the port is
    released before the caller tries to start a new server.
    """
    if not holder:
        return
    server = holder.get("server")
    thread = holder.get("thread")
    sock = holder.get("socket")
    if server:
        if not getattr(server, "should_exit", False):
            server.should_exit = True
    if thread and thread.is_alive():
        thread.join(timeout=timeout)
    # Close our pre-bound socket (uvicorn may have already closed it)
    if sock is not None:
        try:
            sock.close()
        except Exception:
            pass


def _wait_for_server(url: str, timeout: float = 10.0) -> bool:
    """Poll *url* until it responds or *timeout* seconds elapse."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1.0)
            return True
        except Exception:
            time.sleep(0.2)
    return False


def _run_webview(url: str, title: str, width: int, height: int) -> Any | None:
    """Open a pywebview window at *url*. Returns the window or None."""
    _wv = _import_webview()
    if _wv is None:
        return None
    window = _wv.create_window(title, url, width=width, height=height)
    return window


def _webview_blocking(
    window: Any, url: str, title: str, width: int, height: int, icon: str | None = None
) -> Any | None:
    """Start the pywebview event loop (blocking until window closes)."""
    _wv = _import_webview()
    if _wv is None:
        return None
    try:
        _wv.start(icon=icon)
    except Exception:
        return None
    return window


def _serve_app(miki_app: Any, host: str, port: int, runtime: str) -> None:
    """Blocking: run the FastAPI app directly (browser fallback entry)."""
    import uvicorn

    from ..backend import create_app

    uvicorn.run(create_app(miki_app, runtime=runtime), host=host, port=port)


# Used by tests to inspect server lifecycle without real sockets.
server_holder: list[Any] = []


def _default_desktop_icon() -> str:
    """Return the path to the built-in desktop icon.

    Uses ``.ico`` on Windows and ``.png`` on other platforms, since
    pywebview's WinForms renderer requires ICO format while GTK/Qt
    accept PNG.
    """
    runtime_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "runtime")
    if platform.system().lower() == "windows":
        icon_file = "mikiui-icon.ico"
    else:
        icon_file = "mikiui-icon.png"
    return os.path.join(runtime_dir, icon_file)


def _run_native(
    app: Any,
    host: str,
    port: int,
    title: str | None,
    width: int,
    height: int,
    runtime: str,
    reload: bool,
    icon: str | None,
    app_spec: str | None,
) -> None:
    """Native desktop path: spawn server, open pywebview, block until closed."""
    holder = _start_server(app, host, port, runtime=runtime)
    url = f"http://{host}:{port}/"
    if not _wait_for_server(url):
        _stop_server(holder)
        raise RuntimeError("MikiUI desktop server failed to start")

    if reload:
        resolved_title = title or str(getattr(app, "title", "MikiUI"))
        resolved_spec = app_spec or _infer_app_spec(app)
        _run_native_reload(app, host, port, resolved_title, width, height, runtime, resolved_spec, icon=icon)
        return

    resolved_title = title or str(getattr(app, "title", "MikiUI"))
    window = _run_webview(url, resolved_title, width, height)
    _webview_blocking(window, url, resolved_title, width, height, icon=icon)
    _stop_server(holder)


def _run_browser(
    app: Any,
    host: str,
    port: int,
    title: str | None,
    width: int,
    height: int,
    runtime: str,
    reload: bool,
    icon: str | None,
    app_spec: str | None,
) -> None:
    """Browser fallback path: serve the app and open the system browser.

    When ``reload`` is True and ``app_spec`` is provided, watches the project
    directory and restarts the server on file changes, then reloads the browser
    tab automatically.
    """
    import webbrowser

    url = f"http://{host}:{port}/"
    holder = _start_server(app, host, port, runtime=runtime)
    if _wait_for_server(url):
        webbrowser.open(url)

    if reload and app_spec:
        try:
            from watchfiles import watch

            root = os.getcwd()
            for _changes in watch(root, stop_event=None, watch_filter=None):
                _restart_server(app_spec, host, port, runtime, app, None)
        except Exception:  # pragma: no cover
            # watchfiles not available - fall back to simple mode
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        finally:
            _stop_server(holder)
    else:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:  # pragma: no cover
            pass
        finally:
            _stop_server(holder)


def _restart_server(app_spec: str, host: str, port: int, runtime: str, app: Any, window: Any) -> None:
    """Stop old server, start a new one, reload the window (used by --reload).

    Stops the old server, waits for the port to be released, then starts a
    new server with the current *app* instance.  Re-imports the app from
    ``app_spec`` if possible so that code changes are picked up.
    """
    old = server_holder[0] if server_holder else None
    _stop_server(old, timeout=5.0)
    # Brief delay to ensure the OS has released the socket on all platforms
    time.sleep(0.3)
    # Try to re-import the app from spec for code-reload scenarios
    module_name, _, attr = app_spec.partition(":")
    try:
        mod = importlib.import_module(module_name)
        mod = importlib.reload(mod)
        miki_app = getattr(mod, attr or "app")
    except Exception:
        miki_app = app
    holder = _start_server(miki_app, host, port, runtime=runtime)
    if server_holder:
        server_holder[0] = holder
    else:
        server_holder.append(holder)
    # Wait for the new server to be ready before reloading the window
    _wait_for_server(f"http://{host}:{port}/", timeout=10.0)
    if window is not None:
        try:
            window.evaluate_js("location.reload()")
        except Exception:
            pass


def _run_native_reload(
    app: Any,
    host: str,
    port: int,
    title: str,
    width: int,
    height: int,
    runtime: str,
    app_spec: str,
    icon: str | None = None,
) -> None:
    """Native mode with a file watcher that restarts the server on change.

    Starts the server, opens a pywebview window, and spawns a watcher thread
    that restarts the server when source files change.  The watcher runs in a
    background thread so file changes are caught while the window is open.
    ``webview.start()`` blocks until the window is closed or a KeyboardInterrupt
    is received.
    """
    holder = _start_server(app, host, port, runtime=runtime)
    url = f"http://{host}:{port}/"
    if not _wait_for_server(url):
        _stop_server(holder)
        return

    window = _run_webview(url, title or "MikiUI", width, height)

    if window is None and _has_pywebview():
        # pywebview failed to create window - fall back to blocking browser mode
        _run_browser(app, host, port, title, width, height, runtime, False, icon, app_spec)
        return

    # Store initial holder so _restart_server can find it
    if server_holder:
        server_holder[0] = holder
    else:
        server_holder.append(holder)

    # Spawn watcher thread BEFORE blocking so file changes are caught
    watcher_stop = threading.Event()
    watcher = threading.Thread(
        target=_watch_and_restart,
        args=(app_spec, host, port, runtime, app, window, watcher_stop),
        daemon=True,
    )
    watcher.start()

    try:
        # Block until the window is closed
        _webview_blocking(window, url, title, width, height, icon=icon)
    finally:
        # Signal watcher to stop and clean up server
        watcher_stop.set()
        # Stop the current server (may have been replaced by _restart_server)
        current = server_holder[0] if server_holder else None
        if current is not holder:
            _stop_server(current)
        _stop_server(holder)


def _watch_and_restart(
    app_spec: str,
    host: str,
    port: int,
    runtime: str,
    app: Any,
    window: Any,
    stop_event: threading.Event | None = None,
) -> None:
    """Watch project files and restart the server when they change.

    Parameters
    ----------
    app_spec : str
        Module:attr spec to re-import the app on each restart.
    stop_event : threading.Event | None
        If provided, watches for this event to stop watching.
    """
    try:
        from watchfiles import watch
    except Exception:  # pragma: no cover - optional dependency
        return
    root = os.getcwd()

    # watchfiles watch() can accept a stop_event for graceful shutdown
    try:
        for _changes in watch(root, stop_event=stop_event, watch_filter=None):
            _restart_server(app_spec, host, port, runtime, app, window)
    except Exception:
        pass


def run_desktop(
    miki_app: Any,
    host: str = "127.0.0.1",
    port: int = 8000,
    title: str | None = None,
    width: int = 1024,
    height: int = 720,
    runtime: str = "local",
    native: bool = True,
    reload: bool = False,
    app_spec: str | None = None,
    icon: str | None = None,
) -> None:
    """Run the app as a desktop window (native pywebview, browser fallback).

    Parameters
    ----------
    miki_app:
        A :class:`~mikiui.app.MikiApp` instance.
    host, port:
        Where to bind the backing FastAPI server.
    title:
        Window title (defaults to ``miki_app.title``).
    width, height:
        Native window size.
    runtime:
        JS runtime mode (``"local"`` for offline).
    native:
        If ``True`` (default), use pywebview when available; otherwise browser.
    reload:
        Auto-restart the server on file changes (dev mode).
    app_spec:
        ``"module:attr"`` spec used by ``--reload`` to re-import the app.
    icon:
        Window/desktop icon path.
    """
    from ..app import MikiApp

    if miki_app is None and app_spec:
        module_name, _, attr = app_spec.partition(":")
        try:
            mod = importlib.import_module(module_name)
            miki_app = getattr(mod, attr or "app")
        except Exception as exc:
            raise RuntimeError(f"Could not load desktop app from spec {app_spec!r}: {exc}") from exc

    if not isinstance(miki_app, MikiApp):
        raise TypeError(f"run_desktop expects a MikiApp instance, got {type(miki_app).__name__}")

    if icon is None:
        icon = getattr(miki_app, "desktop_icon", None)

    if icon is None:
        icon = _default_desktop_icon()

    if icon:
        icon = os.path.abspath(icon)

    if app_spec is None:
        app_spec = _infer_app_spec(miki_app) if reload else None

    if native and _has_pywebview():
        if reload:
            resolved_title = title or str(miki_app.title)
            resolved_spec = app_spec or _infer_app_spec(miki_app)
            _run_native_reload(miki_app, host, port, resolved_title, width, height, runtime, resolved_spec, icon=icon)
        else:
            _run_native(miki_app, host, port, title, width, height, runtime, reload, icon, app_spec)
    else:
        _run_browser(miki_app, host, port, title, width, height, runtime, reload, icon, app_spec)


def _platform_executable_name(base: str) -> str:
    """Return a platform-appropriate executable name for *base*."""
    system = platform.system().lower()
    if system == "windows":
        return f"{base}.exe"
    if system == "darwin":
        return f"{base}.app"
    return base


def build_desktop(
    miki_app: Any,
    out_dir: str = "dist_desktop",
    app_spec: str | None = None,
    *,
    icon: str | None = None,
    onefile: bool = False,
) -> dict[str, Any]:
    """Build the app for desktop deployment.

    Produces a distributable directory (or PyInstaller spec) containing:
    - The web build (static front-end + ASGI server script).
    - A portable launcher script.
    - A PyInstaller spec file for native packaging on each platform.

    Parameters
    ----------
    miki_app:
        The :class:`~mikiui.app.MikiApp` to package.
    out_dir:
        Output directory.
    app_spec:
        ``"module:attr"`` spec for the app (used in the launcher).
    icon:
        Path to an icon file (``.ico`` on Windows, ``.icns`` on macOS,
        ``.png`` on Linux).
    onefile:
        If ``True``, configure the PyInstaller spec for a single-file
        executable (slower startup, easier distribution).

    Returns
    -------
    dict
        A report with keys: ``status``, ``out_dir``, ``platform``,
        ``web_build_dir``, ``launcher``, ``spec``, ``executable_name``.
    """
    out = os.path.abspath(out_dir)
    os.makedirs(out, exist_ok=True)

    # 1. Produce the web build inside the desktop bundle.
    web_build_dir = os.path.join(out, "web")
    web_report = _build_web_for_desktop(miki_app, out_dir=web_build_dir, app_spec=app_spec)

    # 2. Write the portable launcher script.
    spec = app_spec or _infer_app_spec(miki_app)
    mod_name, _, attr = spec.partition(":")
    launcher_name = _platform_executable_name("launch")
    launcher_path = os.path.join(out, launcher_name)

    if platform.system().lower() == "windows":
        launcher_script = (
            "@echo off\r\n"
            '"""Launch the MikiUI desktop app."""\r\n'
            "python -c "
            '"import sys; sys.path.insert(0, \\".\\"); '
            f"from mikiui.build.desktop_build import run_desktop; "
            f"run_desktop(None, host=\\'127.0.0.1\\', port=8000, title=\\'{miki_app.title}\\', app_spec={spec!r})"
            '"\r\n'
            "pause\r\n"
        )
    elif platform.system().lower() == "darwin":
        launcher_script = (
            "#!/bin/bash\n"
            '"""Launch the MikiUI desktop app."""\n'
            'python -c "import sys; sys.path.insert(0, \\".\\"); '
            f"from mikiui.build.desktop_build import run_desktop; "
            f"run_desktop(None, host=\\'127.0.0.1\\', port=8000, title=\\'{miki_app.title}\\', app_spec={spec!r})"
            '"\n'
        )
    else:
        launcher_script = (
            "#!/usr/bin/env bash\n"
            '"""Launch the MikiUI desktop app."""\n'
            'python -c "import sys; sys.path.insert(0, \\".\\"); '
            f"from mikiui.build.desktop_build import run_desktop; "
            f"run_desktop(None, host=\\'127.0.0.1\\', port=8000, title=\\'{miki_app.title}\\', app_spec={spec!r})"
            '"\n'
        )

    with open(launcher_path, "w", encoding="utf-8") as fh:
        fh.write(launcher_script)
    if platform.system().lower() != "windows":
        os.chmod(launcher_path, 0o755)

    # 3. Generate a PyInstaller spec file.
    spec_path = _write_pyinstaller_spec(
        out,
        spec=spec,
        web_build_dir=web_build_dir,
        icon=icon,
        onefile=onefile,
    )

    # 4. Write platform-specific metadata.
    meta = {
        "windows": {"executable": "launch.exe", "bundle_id": f"com.mikiui.{miki_app.title.lower().replace(' ', '')}"},
        "darwin": {"executable": "launch.app", "bundle_id": f"com.mikiui.{miki_app.title.lower().replace(' ', '')}"},
        "linux": {"executable": "launch", "desktop_file": "mikiui.desktop"},
    }
    system = platform.system().lower()
    executable_name = meta.get(system, meta["linux"])["executable"]

    return {
        "status": "ok",
        "out_dir": out,
        "platform": system,
        "web_build_dir": web_build_dir,
        "launcher": launcher_path,
        "spec": spec_path,
        "executable_name": executable_name,
        "app_spec": spec,
    }


def _build_web_for_desktop(miki_app: Any, *, out_dir: str, app_spec: str | None) -> dict[str, Any]:
    """Build the web portion of a desktop bundle.

    Delegates to :func:`mikiui.build.web_build.build_web` and returns its
    report.  This indirection lets us swap the web build implementation
    without touching the desktop build logic.
    """
    from ..build.web_build import build_web as _build_web

    framework = getattr(miki_app, "style_framework", "plain")
    style_mode = getattr(miki_app, "style_mode", "cdn")
    daisyui = getattr(miki_app, "style_daisyui", False)

    return _build_web(
        miki_app,
        mode="fullstack",
        out_dir=out_dir,
        framework=framework,
        style_mode=style_mode,
        daisyui=daisyui,
    )


def _write_pyinstaller_spec(
    out_dir: str,
    *,
    spec: str,
    web_build_dir: str,
    icon: str | None,
    onefile: bool,
) -> str | None:
    """Write a ``.spec`` file for PyInstaller.

    Returns the spec path, or ``None`` if PyInstaller is unavailable.
    """
    try:
        import PyInstaller.__main__  # noqa: F401
    except Exception:
        return None

    mod_name, _, attr = spec.partition(":")
    entry_script = os.path.join(out_dir, "_pyinstaller_entry.py")
    entry_code = (
        "#!/usr/bin/env python\n"
        '"""Entry script generated by MikiUI desktop build."""\n'
        "from mikiui.build.desktop_build import run_desktop\n"
        "import sys\n"
        f"sys.argv[0] = {entry_script!r}\n"
        f"run_desktop(None, host='127.0.0.1', port=8000, title='MikiUI App', app_spec={spec!r})\n"
    )
    with open(entry_script, "w", encoding="utf-8") as fh:
        fh.write(entry_code)

    spec_name = f"mikiui_{platform.system().lower()}.spec"
    spec_path = os.path.join(out_dir, spec_name)

    args = [
        entry_script,
        f"--name={_platform_executable_name('mikiui_app')}",
        f"--specpath={out_dir}",
        f"--distpath={os.path.join(out_dir, 'dist')}",
        f"--workpath={os.path.join(out_dir, 'build')}",
        f"--contents-directory={web_build_dir}",
    ]
    if onefile:
        args.append("--onefile")
    else:
        args.append("--onedir")
    if icon:
        args.append(f"--icon={icon}")
    args.extend([
        "--windowed",
        "--clean",
        "--noconfirm",
        f"--add-data={web_build_dir}{os.pathsep}_miki_web",
    ])

    try:
        import PyInstaller.__main__
        PyInstaller.__main__.run(args)
    except Exception:
        return None

    return spec_path
