"""MikiUI command-line interface (``new``, ``dev``, ``build``, ``desktop``)."""

from __future__ import annotations

import importlib
import os
import re
import time
from pathlib import Path

import typer

from .app_discovery import AppDiscoveryError, resolve_app_spec
from .scaffolding import UI_FRAMEWORKS, _prompt_framework, scaffold

cli = typer.Typer(
    help="[bold]MikiUI[/bold] — Python-first UI framework.\n\n"
    "Build web, desktop, and mobile apps entirely in Python.\n"
    "See https://github.com/alainmiki/mikiUI for documentation.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        try:
            from importlib.metadata import version as _pkg_version
            typer.echo(f"MikiUI v{_pkg_version('mikiui')}")
        except Exception:
            from mikiui import __version__
            typer.echo(f"MikiUI v{__version__}")
        raise typer.Exit()


@cli.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """MikiUI CLI — build web, desktop, and mobile apps in Python."""


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


def _validate_project_name(name: str) -> str:
    """Validate a project name for filesystem safety."""
    name = name.strip()
    if not name:
        raise ValueError("Project name cannot be empty")
    # Check for invalid filesystem characters
    if re.search(r'[<>:"/\\|?*\x00-\x1f]', name):
        raise ValueError(
            f"Invalid project name: {name!r}. "
            "Avoid: < > : \" / \\ | ? * and control characters."
        )
    if name.startswith(".") or name.startswith("-"):
        raise ValueError("Project name cannot start with '.' or '-'")
    # Reserved Windows names
    reserved = {"con", "prn", "aux", "nul", "com1", "lpt1"}
    if name.lower() in reserved:
        raise ValueError(f"'{name}' is a reserved system name")
    return name


@cli.command()
def install(
    packages: list[str] = typer.Argument(
        None,
        help="Styling packages to install: tailwind, daisyui (default: tailwind daisyui)",
    ),
) -> None:
    """Install the local styling toolchain.

    For Tailwind users:
      mikiui install                 # tailwind + daisyui (writes config + npm install)
      mikiui install tailwind daisyui
      mikiui install tailwind

    Writes ``tailwind.config.js`` + ``postcss.config.js`` and runs ``npm install``
    when Node.js is available.
    """
    from ..styling.tailwind import install_deps, write_config, write_postcss_config

    valid = {"tailwind", "daisyui"}
    requested = packages or ["tailwind", "daisyui"]
    pkgs = [p for p in requested if p in valid]
    invalid = [p for p in requested if p not in valid]

    if invalid:
        typer.echo(
            f"[yellow]Warning:[/yellow] Unknown package(s): {', '.join(invalid)}. "
            f"Valid options: {', '.join(sorted(valid))}",
            err=True,
        )

    if not pkgs:
        pkgs = ["tailwind", "daisyui"]

    use_tailwind = "tailwind" in pkgs
    use_daisyui = "daisyui" in pkgs
    project_dir = Path.cwd()

    if use_tailwind or use_daisyui:
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

    typer.echo("[green]Setup complete.[/green]")


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

    Creates a new directory with a starter app.py, README.md, .gitignore, and
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

    try:
        name = _validate_project_name(name)
    except ValueError as exc:
        typer.echo(f"[red]Error:[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    try:
        path = scaffold(name, directory, framework=fw)
    except FileExistsError as exc:
        typer.echo(f"[red]Error:[/red] {exc}", err=True)
        raise typer.Exit(code=1)
    except ValueError as exc:
        typer.echo(f"[red]Error:[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    # Build next-steps message
    steps = [
        f"[bold green]Created[/bold green] MikiUI project [bold]{path}[/bold]",
        f"Framework: [cyan]{fw}[/cyan]",
        "",
        "Next steps:",
        f"  cd {name}",
    ]
    if fw in ("tailwind", "daisyui"):
        steps.extend([
            "  mikiui install       # install Node.js deps",
            "  mikiui dev           # start dev server",
            "  mikiui tailwind dev  # watch CSS (second terminal)",
        ])
    else:
        steps.extend([
            "  mikiui dev           # start dev server",
        ])
    steps.append("  mikiui desktop       # native desktop window")

    _print_ready("\n".join(steps))


@cli.command()
def dev(
    app: str = typer.Option(None, "--app", "-a", help="module:attr of the MikiApp (auto-discovered if omitted)"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable auto-reload (default: on)"),
    browser: bool = typer.Option(False, "--browser", help="Open browser automatically"),
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
      mikiui dev --browser
    """
    import uvicorn

    spec = _safe_resolve(app)
    module_name, _, attr = spec.partition(":")

    # Validate the app can be imported
    try:
        mod = importlib.import_module(module_name)
        getattr(mod, attr or "app")
    except Exception as exc:
        typer.echo(f"[red]Could not import app '{spec}':[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    from ..backend import create_app

    url = f"http://{host}:{port}"
    typer.echo(f"[cyan]Serving[/cyan] MikiUI app from '{spec}' at {url}")
    typer.echo("[dim]Press Ctrl-C to stop.[/dim]")

    if browser:
        import threading
        threading.Timer(1.5, lambda: __import__("webbrowser", fromlist=["open"]).open(url)).start()

    if not reload:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
        fastapi_app = create_app(miki_app)
        uvicorn.run(fastapi_app, host=host, port=port)
        return

    os.environ["MIKIUI_APP_SPEC"] = spec
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
    theme: str = typer.Option(None, "--theme", help="Compile Tailwind CSS (tailwind)"),
    daisyui: bool = typer.Option(False, "--daisyui/--no-daisyui", help="Enable DaisyUI in the Tailwind build"),
    optimize_css: bool = typer.Option(True, "--optimize/--no-optimize", help="Minify built CSS"),
    watch: bool = typer.Option(False, "--watch", help="Watch mode (rebuild CSS on change) — for dev"),
    clean: bool = typer.Option(False, "--clean", help="Clean output directory before building"),
) -> None:
    """Build the app for production.

    Creates an optimized build in the output directory. For web targets,
    this produces static assets. For desktop targets, it generates a launch
    script for a native window.

    Styling is fully automated:

      mikiui build --theme tailwind            # scan + compile Tailwind CSS
      mikiui build --theme tailwind --daisyui  # + DaisyUI component library
      mikiui build --target web                # plain web build (miki.css)
      mikiui build --target desktop            # desktop launcher

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
    except Exception as exc:
        typer.echo(f"[red]Could not import app '{spec}':[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    # Tailwind/DaisyUI styling build
    app_framework = getattr(miki_app, "style_framework", "plain")
    app_style_mode = getattr(miki_app, "style_mode", "cdn")
    app_daisyui = getattr(miki_app, "style_daisyui", False)
    effective_daisyui = daisyui or app_daisyui

    if app_framework == "tailwind" or theme == "tailwind":
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
        typer.echo(f"[green]Tailwind CSS built:[/green] {css_path}")
        if watch:
            typer.echo("[dim]Watching for changes (Ctrl-C to stop)...[/dim]")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                typer.echo("[dim]Stopped.[/dim]")
            return
        skip_tailwind = True
    else:
        skip_tailwind = False

    typer.echo(f"[cyan]Building[/cyan] {target} ({mode}) from '{spec}'...")

    # Clean output directory if requested
    if clean and os.path.isdir(out_dir):
        import shutil
        shutil.rmtree(out_dir)
        typer.echo(f"[dim]Cleaned {out_dir}/[/dim]")

    if target == "desktop":
        desktop_out = f"{out_dir}_desktop"
        report = build_desktop(miki_app, out_dir=desktop_out, app_spec=spec)
        warning = report.get("warning")
        if warning:
            typer.echo(f"[yellow]Warning:[/yellow] {warning}")
        bundle = report.get("bundle")
        if bundle:
            typer.echo(f"  Bundle: {bundle}")
    else:
        report = build_web(
            miki_app,
            mode=mode,
            out_dir=out_dir,
            theme=theme,
            framework=app_framework,
            style_mode=app_style_mode,
            daisyui=effective_daisyui,
            skip_tailwind=skip_tailwind,
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

    typer.echo(f"[green]Build complete:[/green] {report.get('status', 'ok')}")
    typer.echo(f"  Output: {report.get('out_dir', out_dir)}")


@cli.command()
def desktop(
    app: str = typer.Option(None, "--app", "-a", help="module:attr of the MikiApp (auto-discovered if omitted)"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    title: str = typer.Option(None, "--title", help="Window title (defaults to app.title)"),
    width: int = typer.Option(1024, "--width", help="Window width"),
    height: int = typer.Option(720, "--height", help="Window height"),
    runtime: str = typer.Option("local", "--runtime", help="JS runtime: cdn | local"),
    browser: bool = typer.Option(False, "--browser", help="Force system-browser fallback"),
    reload: bool = typer.Option(False, "--reload/--no-reload", help="Auto-refresh on file changes"),
) -> None:
    """Run the app as a native desktop window.

    By default MikiUI launches a pywebview window (if installed) for a true
    standalone desktop feel. If pywebview is not installed, or ``--browser``
    is passed, the app opens in the system's default browser instead.

    Auto-discovers ``app.py`` / ``main.py`` / ``server.py`` in the current
    directory if ``--app`` is not given.

    Examples:
      mikiui desktop
      mikiui desktop --app myapp:app
      mikiui desktop --reload --title "My App"
      mikiui desktop --browser --port 3000
    """
    from ..build import run_desktop

    if runtime not in ("cdn", "local"):
        typer.echo(f"[red]Invalid runtime:[/red] {runtime} (choose: cdn, local)", err=True)
        raise typer.Exit(code=1)
    if width < 100 or height < 100:
        typer.echo(f"[red]Invalid window size:[/red] {width}x{height} (minimum: 100x100)", err=True)
        raise typer.Exit(code=1)

    spec = _safe_resolve(app)
    module_name, _, attr = spec.partition(":")
    try:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
    except Exception as exc:
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


# --- Tailwind sub-command group ------------------------------------------------

tailwind_cli = typer.Typer(
    help="Tailwind CSS build tooling (dev server + production build).",
    no_args_is_help=True,
)
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
        "tailwind.css",
        "--out", "-o",
        help="Output CSS path (default: tailwind.css in current directory)",
    ),
) -> None:
    """Compile an optimized Tailwind (optionally DaisyUI) stylesheet.

    This is the production Tailwind build.  It scans your components/widgets,
    generates the config, and writes the minimized CSS.

    Examples:
      mikiui tailwind build
      mikiui tailwind build --daisyui
      mikiui tailwind build --out dist/site.css --optimize
    """
    from ..build.tailwind import build_css, register_built_theme

    # Ensure parent directory exists
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    typer.echo("[cyan]Building Tailwind CSS[/cyan] (scanning components/widgets)...")
    css_path = build_css(theme=theme, daisyui=daisyui, out=out, optimize=optimize)
    register_built_theme("built-tailwind", css_path, daisyui=daisyui)
    typer.echo(f"[green]Tailwind CSS built:[/green] {css_path}")


if __name__ == "__main__":
    cli()
