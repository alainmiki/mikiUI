"""MikiUI command-line interface (``new``, ``dev``, ``build``, ``desktop``)."""

from __future__ import annotations

import importlib
import os
import time
from pathlib import Path

import typer

from .app_discovery import AppDiscoveryError, resolve_app_spec
from .scaffolding import UI_FRAMEWORKS, _prompt_framework, scaffold

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
            "[bold cyan]MikiUI[/bold cyan] v0.0.1 — Python-first UI framework\n\n"
            "[dim]Commands:[/dim]\n"
            "  [cyan]mikiui new <name>[/cyan]    Scaffold a new project\n"
            "  [cyan]mikiui dev[/cyan]          Start dev server (auto-discovers app.py)\n"
            "  [cyan]mikiui desktop[/cyan]      Open as native desktop window\n"
            "  [cyan]mikiui build[/cyan]        Build for production\n"
            "  [cyan]mikiui tailwind[/cyan]     Tailwind CSS tooling (dev/build/watch)\n"
            "  [cyan]mikiui install[/cyan]      Install styling dependencies\n"
            "  [cyan]mikiui new --help[/cyan]   Show full help for any command\n",
            title="[bold green]MIKIUI[/bold green]",
            border_style="cyan",
        ))
    except ImportError:
        typer.echo("MikiUI v0.0.1 — Python-first UI framework")
        typer.echo("Commands: new, dev, desktop, build, tailwind, install")
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


def _safe_resolve(app: str | None) -> str:
    """Resolve app spec, showing a clean error if discovery fails."""
    try:
        return resolve_app_spec(app)
    except AppDiscoveryError as exc:
        typer.echo(f"[red]Error:[/red] {exc}", err=True)
        raise typer.Exit(code=1)


@cli.command()
def install(
    packages: list[str] = typer.Argument(
        None,
        help="Styling packages to install: tailwind, daisyui (default: tailwind daisyui)",
    ),
    dev: bool = typer.Option(False, "--dev", help="Install as dev dependencies"),
) -> None:
    """Install the local styling toolchain.

    For Tailwind users:
      mikiui install                 # tailwind + daisyui (writes config + npm install)
      mikiui install tailwind daisyui
      mikiui install tailwind --dev

    Writes ``package.json`` (if missing), ``tailwind.config.js`` +
    ``postcss.config.js``, and runs ``npm install`` when Node.js is available.
    """
    from ..styling.tailwind import install_deps, write_config, write_postcss_config

    valid = {"tailwind", "daisyui"}
    pkgs = [p for p in (packages or ["tailwind", "daisyui"]) if p in valid]
    if not pkgs:
        pkgs = ["tailwind", "daisyui"]

    use_tailwind = "tailwind" in pkgs
    use_daisyui = "daisyui" in pkgs
    project_dir = Path.cwd()

    if use_tailwind or use_daisyui:
        from ..styling.tailwind import install_deps, write_config, write_postcss_config

        write_config(
            str(project_dir / "tailwind.config.js"),
            theme="light",
            daisyui=use_daisyui,
        )
        write_postcss_config(str(project_dir / "postcss.config.js"))

        result = install_deps(project_dir=project_dir, daisyui=use_daisyui)
        if result.get("status") == "node_required":
            typer.echo(
                "[yellow]Node.js is required for Tailwind CSS.[/yellow]\n"
                "  Install it from https://nodejs.org/\n"
                "  Then re-run: mikiui install tailwind daisyui",
                err=True,
            )
            raise typer.Exit(code=1)
        typer.echo(result.get("message", ""))

    if not (use_tailwind or use_daisyui):
        typer.echo("Nothing to install. Choose from: tailwind, daisyui")

    typer.echo("[green]✓ Styling setup complete.[/green]")


@cli.command()
def new(
    name: str = typer.Argument(
        None,
        help="Project directory name",
    ),
    directory: str = typer.Option(
        None, "--dir", "-d", help="Parent directory (defaults to current directory)"
    ),
    framework: str = typer.Option(
        None,
        "--framework", "-f",
        help=f"CSS framework: {', '.join(UI_FRAMEWORKS)} (default: tailwind)",
    ),
) -> None:
    """Scaffold a new MikiUI project.

    Creates a new directory with a starter app.py, README.md, and
    framework-specific config files.

    If *framework* is not provided, you will be prompted to choose one.

    Examples:
      mikiui new myapp
      mikiui new myapp --framework plain --dir /tmp
    """
    if framework is None:
        framework = _prompt_framework()

    fw = framework
    if fw not in UI_FRAMEWORKS:
        typer.echo(f"[red]Invalid framework:[/red] {fw}", err=True)
        typer.echo(f"Choose from: {', '.join(UI_FRAMEWORKS)}", err=True)
        raise typer.Exit(code=1)

    if name is None:
        name = typer.prompt("Project name", default="myapp")
        name = name.strip() or "myapp"

    try:
        path = scaffold(name, directory, framework=fw)
    except FileExistsError as exc:
        typer.echo(f"[red]Error:[/red] {exc}", err=True)
        raise typer.Exit(code=1)
    except ValueError as exc:
        typer.echo(f"[red]Error:[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    _print_ready(
        f"[bold green]✓[/bold green] Created MikiUI project [bold]{path}[/bold]\n"
        f"Framework: [cyan]{fw}[/cyan]\n\n"
        f"Next steps:\n"
        f"  cd {name}\n"
        f"  mikiui dev           # start dev server\n"
        f"  mikiui desktop       # native desktop window\n"
        + (
            "  mikiui install       # install Node.js deps (Tailwind)\n"
            "  mikiui tailwind dev  # watch & rebuild CSS (in another terminal)\n"
            if fw == "tailwind"
            else (
                "  mikiui install tailwind daisyui  # enable DaisyUI\n"
                "  mikiui tailwind dev               # watch CSS (in another terminal)\n"
                if fw == "daisyui"
                else ""
            )
        )
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

    For Tailwind users: run ``mikiui tailwind dev`` in another terminal to
    watch and rebuild CSS on change.

    Examples:
      mikiui dev
      mikiui dev --app myapp:app
      mikiui dev --port 3000 --no-reload
    """
    import uvicorn

    spec = _safe_resolve(app)
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
    theme: str = typer.Option(None, "--theme", help="Styling theme to build: tailwind (scans + compiles CSS)"),
    daisyui: bool = typer.Option(False, "--daisyui/--no-daisyui", help="Enable DaisyUI in the Tailwind build"),
    optimize_css: bool = typer.Option(True, "--optimize/--no-optimize", help="Minify built CSS"),
    watch: bool = typer.Option(False, "--watch", help="Watch mode (rebuild CSS on change) — for dev"),
) -> None:
    """Build the app for production.

    Creates an optimized build in the output directory. For web targets,
    this produces static assets. For desktop targets, it generates a launch
    script for a native window.

    Styling is fully automated — no manual config needed:

      mikiui build --theme tailwind            # scan + compile Tailwind CSS
      mikiui build --theme tailwind --daisyui  # + DaisyUI component library
      mikiui build --target web                # plain web build (miki.css)
      mikiui build --target desktop            # desktop launcher

    Note: CSS framework assets (Tailwind, DaisyUI) are bundled
    from the CDN by default; for offline use, set the theme runtime to ``local``.

    Examples:
      mikiui build --target web
      mikiui build --target desktop
      mikiui build --target web --mode separate --out dist/
      mikiui build --theme tailwind --daisyui
    """
    from ..build import build_desktop, build_web, optimize

    if target not in ("web", "desktop"):
        typer.echo(f"[red]Invalid target:[/red] {target} (choose: web, desktop)", err=True)
        raise typer.Exit(code=1)
    if mode not in ("fullstack", "separate"):
        typer.echo(f"[red]Invalid mode:[/red] {mode} (choose: fullstack, separate)", err=True)
        raise typer.Exit(code=1)

    spec = _safe_resolve(app)
    module_name, _, attr = spec.partition(":")
    try:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
    except Exception as exc:  # pragma: no cover - user error surfaced to CLI
        typer.echo(f"[red]Could not import app '{spec}':[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    # Tailwind/DaisyUI styling build (happens before/with the web build).
    app_framework = getattr(miki_app, "style_framework", "plain")
    app_style_mode = getattr(miki_app, "style_mode", "cdn")
    app_daisyui = getattr(miki_app, "style_daisyui", False)
    effective_daisyui = daisyui or app_daisyui

    if app_framework == "tailwind":
        from ..build.tailwind import build_css, register_built_theme

        typer.echo("[cyan]Building Tailwind CSS[/cyan] (scanning components/widgets)...")
        css_path = build_css(
            theme=getattr(miki_app, "theme", "light"),
            daisyui=effective_daisyui,
            out=os.path.join(out_dir, "_miki", "runtime", "themes", "tailwind.css"),
            optimize=optimize_css,
            watch=watch,
        )
        register_built_theme("built-tailwind", css_path, daisyui=effective_daisyui)
        typer.echo(f"[green]✓ Tailwind CSS built:[/green] {css_path}")
        if watch:
            typer.echo("[dim]Watching for changes (Ctrl-C to stop)...[/dim]")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            return

    typer.echo(f"[cyan]Building[/cyan] {target} ({mode}) from '{spec}'...")

    if target == "desktop":
        report = build_desktop(miki_app, out_dir=f"{out_dir}_desktop", app_spec=spec)
    else:
        report = build_web(
            miki_app,
            mode=mode,
            out_dir=out_dir,
            theme=theme,
            framework=app_framework,
            style_mode=app_style_mode,
            daisyui=effective_daisyui,
        )
        asset_paths = [
            os.path.join(out_dir, "_miki", "runtime", a)
            for a in (
                "htmx.min.js",
                "alpine.min.js",
                "htmx_runtime.js",
                "alpine_runtime.js",
                "miki_ui.js",
                "history_router.js",
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
    files change. Requires the ``watchfiles`` package.

    Examples:
      mikiui desktop
      mikiui desktop --app myapp:app
      mikiui desktop --reload --title "My App"
      mikiui desktop --browser --port 3000
    """
    from ..build import run_desktop

    spec = _safe_resolve(app)
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


@cli.command()
def dev_css(
    daisyui: bool = typer.Option(False, "--daisyui/--no-daisyui", help="Enable DaisyUI in the build"),
    theme: str = typer.Option("light", "--theme", help="Active color theme for DaisyUI bridging"),
) -> None:
    """Start the Tailwind CSS watcher for development (alias of ``tailwind dev``).

    Scans your components/widgets and rebuilds CSS on every change.  Pair this
    with ``mikiui dev`` (in another terminal) for a full hot-reload experience.
    """
    from ..build.tailwind import build_css

    typer.echo("[cyan]Tailwind dev watcher started[/cyan] (Ctrl-C to stop)")
    try:
        build_css(theme=theme, daisyui=daisyui, watch=True, optimize=False)
    except KeyboardInterrupt:
        typer.echo("[dim]Stopped.[/dim]")


# --- Tailwind sub-command group ------------------------------------------------

tailwind_cli = typer.Typer(help="Tailwind CSS build tooling (dev server + production build).", no_args_is_help=True)
cli.add_typer(tailwind_cli, name="tailwind")


@tailwind_cli.command("dev")
def tailwind_dev(
    daisyui: bool = typer.Option(False, "--daisyui/--no-daisyui", help="Enable DaisyUI in the build"),
    theme: str = typer.Option("light", "--theme", help="Active color theme for DaisyUI bridging"),
) -> None:
    """Start the Tailwind CSS dev server (file watcher).

    Scans ``mikiui/components``, ``mikiui/widgets``, and your project files,
    then recompiles CSS whenever a class changes.  Use alongside ``mikiui dev``.

    Examples:
      mikiui tailwind dev
      mikiui tailwind dev --daisyui
    """
    from ..build.tailwind import build_css

    typer.echo("[cyan]Tailwind dev watcher started[/cyan] (Ctrl-C to stop)")
    try:
        build_css(theme=theme, daisyui=daisyui, watch=True, optimize=False)
    except KeyboardInterrupt:
        typer.echo("[dim]Stopped.[/dim]")


@tailwind_cli.command("build")
def tailwind_build(
    daisyui: bool = typer.Option(False, "--daisyui/--no-daisyui", help="Enable DaisyUI in the build"),
    theme: str = typer.Option("light", "--theme", help="Active color theme for DaisyUI bridging"),
    optimize: bool = typer.Option(True, "--optimize/--no-optimize", help="Minify the output CSS"),
    out: str = typer.Option(
        os.path.join("mikiui", "runtime", "themes", "tailwind.css"),
        "--out", "-o",
        help="Output CSS path",
    ),
) -> None:
    """Compile an optimized Tailwind (optionally DaisyUI) stylesheet.

    This is the production Tailwind build.  It scans your components/widgets,
    generates the config, and writes the minimized CSS — no manual copy-pasting.

    Examples:
      mikiui tailwind build
      mikiui tailwind build --daisyui
      mikiui tailwind build --out dist/site.css --optimize
    """
    from ..build.tailwind import build_css, register_built_theme

    typer.echo("[cyan]Building Tailwind CSS[/cyan] (scanning components/widgets)...")
    css_path = build_css(theme=theme, daisyui=daisyui, out=out, optimize=optimize)
    register_built_theme("built-tailwind", css_path, daisyui=daisyui)
    typer.echo(f"[green]✓ Tailwind CSS built:[/green] {css_path}")


@tailwind_cli.command("watch")
def tailwind_watch(
    daisyui: bool = typer.Option(False, "--daisyui/--no-daisyui", help="Enable DaisyUI in the build"),
    theme: str = typer.Option("light", "--theme", help="Active color theme for DaisyUI bridging"),
) -> None:
    """Alias for ``mikiui tailwind dev`` — watch and rebuild CSS on change."""
    from ..build.tailwind import build_css

    typer.echo("[cyan]Tailwind watch started[/cyan] (Ctrl-C to stop)")
    try:
        build_css(theme=theme, daisyui=daisyui, watch=True, optimize=False)
    except KeyboardInterrupt:
        typer.echo("[dim]Stopped.[/dim]")


@cli.callback(invoke_without_command=False)
def main() -> None:
    """MikiUI CLI — entry point for new, dev, build, and desktop commands.

    When run without a subcommand, prints a banner with available commands.
    """


if __name__ == "__main__":
    cli()
