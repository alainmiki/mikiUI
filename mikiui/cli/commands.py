"""MikiUI command-line interface (``new``, ``dev``, ``build``)."""

from __future__ import annotations

import importlib
import os
import sys

import typer

from .scaffolding import scaffold

cli = typer.Typer(help="MikiUI - Python-first UI framework CLI", no_args_is_help=True)


@cli.command()
def new(
    name: str = typer.Argument(..., help="Project directory name"),
    directory: str = typer.Option(None, "--dir", help="Parent directory"),
) -> None:
    """Scaffold a new MikiUI project."""
    path = scaffold(name, directory)
    typer.echo(f"Created MikiUI project at {path}")


@cli.command()
def dev(
    app: str = typer.Option("mikiui.examples.demo:app", "--app", help="module:attr of the MikiApp"),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    reload: bool = typer.Option(True, "--reload/--no-reload"),
) -> None:
    """Run the development server (FastAPI + uvicorn)."""
    import uvicorn

    module_name, _, attr = app.partition(":")
    try:
        mod = importlib.import_module(module_name)
        getattr(mod, attr or "app")
    except Exception as exc:  # pragma: no cover - user error surfaced to CLI
        typer.echo(f"Could not import app '{app}': {exc}", err=True)
        raise typer.Exit(code=1)

    from ..backend import create_app

    if not reload:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
        fastapi_app = create_app(miki_app)
        typer.echo(f"Serving MikiUI app from {app} at http://{host}:{port}")
        uvicorn.run(fastapi_app, host=host, port=port)
        return

    # With reload enabled, uvicorn needs a string path to an importable factory
    # so it can re-import the module on file changes.  We set the module/attr
    # on a shared singleton that reload_dev_app reads on each reload.
    from ..backend import create_app as _create_app

    import mikiui.cli._dev_support as support
    support.APP_SPEC = app
    support.CREATE_APP = _create_app
    typer.echo(f"Serving MikiUI app from {app} at http://{host}:{port}")
    uvicorn.run(
        "mikiui.cli._dev_support:app_factory",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


@cli.command()
def build(
    target: str = typer.Option("web", "--target", help="web | desktop"),
    mode: str = typer.Option("fullstack", "--mode", help="fullstack | separate"),
) -> None:
    """Build the app (web/desktop, fullstack/separate).

    The full build system (webpack/vite bundling, desktop packaging) is not yet
    implemented; this command validates options and reports the intended action.
    """
    if target not in ("web", "desktop"):
        typer.echo(f"Invalid target: {target}", err=True)
        raise typer.Exit(code=1)
    if mode not in ("fullstack", "separate"):
        typer.echo(f"Invalid mode: {mode}", err=True)
        raise typer.Exit(code=1)
    if target == "desktop":
        typer.echo("[build] target=desktop -> use `mikiui desktop` to launch a window")
        return
    typer.echo(f"[build] target={target} mode={mode} (build system pending)")


@cli.command()
def desktop(
    app: str = typer.Option("mikiui.examples.demo:app", "--app", help="module:attr of the MikiApp"),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    title: str = typer.Option(None, "--title", help="Window title (defaults to app.title)"),
    width: int = typer.Option(1024, "--width", help="Window width (native mode)"),
    height: int = typer.Option(720, "--height", help="Window height (native mode)"),
    runtime: str = typer.Option("local", "--runtime", help="JS runtime mode: cdn | local"),
    browser: bool = typer.Option(False, "--browser", help="Force system-browser fallback (skip pywebview)"),
) -> None:
    """Run the app as a native desktop window.

    By default MikiUI launches a pywebview window if pywebview is installed,
    giving a standalone desktop feel without browser chrome. If pywebview is not
    installed (or ``--browser`` is passed), the app opens in the system's
    default browser instead.
    """
    import importlib

    from ..build import run_desktop

    module_name, _, attr = app.partition(":")
    try:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
    except Exception as exc:  # pragma: no cover - user error surfaced to CLI
        typer.echo(f"Could not import app '{app}': {exc}", err=True)
        raise typer.Exit(code=1)
    run_desktop(
        miki_app,
        host=host,
        port=port,
        title=title,
        native=not browser,
        runtime=runtime,
        width=width,
        height=height,
    )

