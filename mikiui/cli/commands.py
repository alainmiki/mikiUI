"""MikiUI command-line interface (``new``, ``dev``, ``build``, ``desktop``)."""

from __future__ import annotations

import importlib
import os

import typer

from .app_discovery import resolve_app_spec
from .scaffolding import UI_FRAMEWORKS, scaffold

cli = typer.Typer(
    help="[bold]MikiUI[/bold] — Python-first UI framework.\n\n"
    "Render UIs as standalone desktops or websites from Python component trees.\n"
    "See https://kilo.ai/docs/mikiui for full documentation.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    rich_help_panel="MikiUI Commands",
)


def _print_banner() -> None:
    """Print a MikiUI banner when the CLI is invoked with no command."""
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        console.print(Panel(
            "[bold cyan]MikiUI[/bold cyan] v0.1.0 — Python-first UI framework\n\n"
            "[dim]Commands:[/dim]\n"
            "  [cyan]mikiui new <name>[/cyan]    Scaffold a new project\n"
            "  [cyan]mikiui dev[/cyan]          Start dev server (auto-discovers app.py)\n"
            "  [cyan]mikiui desktop[/cyan]      Open as native desktop window\n"
            "  [cyan]mikiui build[/cyan]        Build for production\n"
            "  [cyan]mikiui new --help[/cyan]   Show full help for any command\n",
            title="[bold green]MIKIUI[/bold green]",
            border_style="cyan",
        ))
    except ImportError:
        typer.echo("MikiUI v0.1.0 — Python-first UI framework")
        typer.echo("Commands: new, dev, desktop, build")
        typer.echo("Run 'mikiui <command> --help' for help.")


def _print_ready(message: str) -> None:
    """Print a styled 'ready' message using Rich if available."""
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        console.print(Panel(message, title="[bold green]MikiUI[/bold green]", border_style="green"))
    except ImportError:
        typer.echo(message)


@cli.command()
def new(
    name: str = typer.Argument(
        None,  # interactive if not provided
        help="Project directory name",
    ),
    directory: str = typer.Option(
        None, "--dir", "-d", help="Parent directory (defaults to current directory)"
    ),
    framework: str = typer.Option(
        "tailwind",
        "--framework", "-f",
        help=f"CSS framework: {', '.join(UI_FRAMEWORKS)}",
    ),
) -> None:
    """Scaffold a new MikiUI project.

    Creates a new directory with a starter app.py, README.md, and
    framework-specific config files.

    Examples:
      mikiui new myapp
      mikiui new myapp --framework bootstrap
      mikiui new myapp --framework plain --dir /tmp
    """
    # Interactive mode: prompt for missing arguments.
    if name is None:
        name = typer.prompt("Project name", default="myapp")
        name = name.strip() or "myapp"
    if framework not in UI_FRAMEWORKS:
        typer.echo(f"[red]Invalid framework:[/red] {framework}", err=True)
        typer.echo(f"Choose from: {', '.join(UI_FRAMEWORKS)}", err=True)
        raise typer.Exit(code=1)

    try:
        path = scaffold(name, directory, framework=framework)
    except FileExistsError as exc:
        typer.echo(f"[red]Error:[/red] {exc}", err=True)
        raise typer.Exit(code=1)
    except ValueError as exc:
        typer.echo(f"[red]Error:[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    _print_ready(
        f"[bold green]✓[/bold green] Created MikiUI project [bold]{path}[/bold]\n"
        f"Framework: [cyan]{framework}[/cyan]\n"
        f"\nNext steps:\n"
        f"  cd {name}\n"
        f"  mikiui dev        # start dev server\n"
        f"  mikiui desktop     # native desktop window\n"
    )


@cli.command()
def dev(
    app: str = typer.Option(None, "--app", "-a", help="module:attr of the MikiApp (auto-discovered if omitted)"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable auto-reload (default: on)"),
) -> None:
    """Start the development server.

    Launches a FastAPI + uvicorn server with hot-reloading enabled by default.
    Auto-discovers ``app.py`` / ``main.py`` / ``server.py`` in the current
    directory if ``--app`` is not given.

    Examples:
      mikiui dev
      mikiui dev --app myapp:app
      mikiui dev --port 3000 --no-reload
    """
    import uvicorn

    spec = resolve_app_spec(app)
    module_name, _, attr = spec.partition(":")
    try:
        mod = importlib.import_module(module_name)
        getattr(mod, attr or "app")
    except Exception as exc:  # pragma: no cover - user error surfaced to CLI
        typer.echo(f"[red]Could not import app '{spec}':[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    from ..backend import create_app

    if not reload:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
        fastapi_app = create_app(miki_app)
        typer.echo(f"[cyan]Serving[/cyan] MikiUI app from '{spec}' at http://{host}:{port}")
        uvicorn.run(fastapi_app, host=host, port=port)
        return

    os.environ["MIKIUI_APP_SPEC"] = spec
    typer.echo(f"[cyan]Serving[/cyan] MikiUI app from '{spec}' at http://{host}:{port}")
    typer.echo("[dim]Press Ctrl-C to stop.[/dim]")
    uvicorn.run(
        "mikiui.cli._dev_support:app_factory",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


@cli.command()
def build(
    target: str = typer.Option("web", "--target", "-t", help="Build target: web | desktop"),
    mode: str = typer.Option("fullstack", "--mode", "-m", help="Build mode: fullstack | separate"),
    app: str = typer.Option(None, "--app", "-a", help="module:attr of the MikiApp (auto-discovered if omitted)"),
    out_dir: str = typer.Option("dist", "--out", "-o", help="Output directory"),
) -> None:
    """Build the app for production.

    Creates an optimized build in the output directory. For web targets,
    this produces static assets. For desktop targets, it generates a
    PyInstaller specification and a launch script.

    Note: CSS framework assets (Tailwind, Bootstrap, DaisyUI) are bundled
    from the CDN by default; for offline use, set the theme runtime to ``local``.

    Examples:
      mikiui build --target web
      mikiui build --target desktop
      mikiui build --target web --mode separate --out dist/
    """
    from ..build import build_desktop, build_web, optimize

    if target not in ("web", "desktop"):
        typer.echo(f"[red]Invalid target:[/red] {target} (choose: web, desktop)", err=True)
        raise typer.Exit(code=1)
    if mode not in ("fullstack", "separate"):
        typer.echo(f"[red]Invalid mode:[/red] {mode} (choose: fullstack, separate)", err=True)
        raise typer.Exit(code=1)

    spec = resolve_app_spec(app)
    module_name, _, attr = spec.partition(":")
    try:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
    except Exception as exc:  # pragma: no cover - user error surfaced to CLI
        typer.echo(f"[red]Could not import app '{spec}':[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"[cyan]Building[/cyan] {target} ({mode}) from '{spec}'...")

    if target == "desktop":
        report = build_desktop(miki_app, out_dir=f"{out_dir}_desktop", app_spec=spec)
    else:
        report = build_web(miki_app, mode=mode, out_dir=out_dir)
        asset_paths = [
            os.path.join(out_dir, "_miki", "runtime", a)
            for a in (
                "htmx.min.js",
                "alpine.min.js",
                "htmx_runtime.js",
                "alpine_runtime.js",
                "miki_ui.js",
                "miki.css",
            )
        ]
        optimize(asset_paths, level="balanced")

    typer.echo(f"[green]✓ Build complete:[/green] {report.get('status', 'ok')}")
    typer.echo(f"  Output: {report.get('out_dir', out_dir)}")


@cli.command()
def desktop(
    app: str = typer.Option(None, "--app", "-a", help="module:attr of the MikiApp (auto-discovered if omitted)"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    title: str = typer.Option(None, "--title", help="Window title (defaults to app.title)"),
    width: int = typer.Option(1024, "--width", help="Window width (native mode)"),
    height: int = typer.Option(720, "--height", help="Window height (native mode)"),
    runtime: str = typer.Option("local", "--runtime", help="JS runtime mode: cdn | local (offline)"),
    browser: bool = typer.Option(False, "--browser", help="Force system-browser fallback (skip pywebview)"),
    reload: bool = typer.Option(False, "--reload/--no-reload", help="Auto-refresh on file changes (dev mode)"),
) -> None:
    """Run the app as a native desktop window.

    By default MikiUI launches a pywebview window (if installed) for a true
    standalone desktop feel — no browser chrome or address bar. If pywebview
    is not installed, or ``--browser`` is passed, the app opens in the
    system's default browser instead.

    Auto-discovers ``app.py`` / ``main.py`` / ``server.py`` in the current
    directory if ``--app`` is not given.

    Use ``--reload`` during development to auto-refresh the window when source
    files change. Requires the ``watchfiles`` package (installed automatically
    with ``mikiui[dev]``).

    Examples:
      mikiui desktop
      mikiui desktop --app myapp:app
      mikiui desktop --reload --title "My App"
      mikiui desktop --browser --port 3000
    """
    from ..build import run_desktop

    spec = resolve_app_spec(app)
    module_name, _, attr = spec.partition(":")
    try:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
    except Exception as exc:  # pragma: no cover - user error surfaced to CLI
        typer.echo(f"[red]Could not import app '{spec}':[/red] {exc}", err=True)
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
        reload=reload,
        app_spec=spec,
    )


@cli.callback(invoke_without_command=False)
def main() -> None:
    """MikiUI CLI — entry point for new, dev, build, and desktop commands.

    When run without a subcommand, prints a banner with available commands.
    """


if __name__ == "__main__":
    cli()
