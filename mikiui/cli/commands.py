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
    mobile: bool = typer.Option(
        False, "--mobile",
        help="Enable Capacitor live reload",
    ),
    mobile_target: str = typer.Option(
        "android", "--mobile-target",
        help="Mobile platform for live reload: android | ios",
    ),
) -> None:
    """Start the development server.

    Launches a FastAPI + uvicorn server with hot-reloading enabled by default.
    Auto-discovers ``app.py`` / ``main.py`` / ``server.py`` in the current
    directory if ``--app`` is not given.

    For Tailwind users: run ``mikiui tailwind dev`` in another terminal to
    watch and rebuild CSS on change.

    For mobile development, use ``--mobile`` to enable Capacitor live reload.
    This builds the mobile project and syncs changes to the native app.

    Examples:
      mikiui dev
      mikiui dev --app myapp:app
      mikiui dev --port 3000 --no-reload
      mikiui dev --browser
      mikiui dev --mobile --mobile-target android
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

    # Mobile live reload setup
    mobile_out_dir = None
    if mobile:
        mobile_out_dir = os.path.join(os.getcwd(), "dist_mobile")
        typer.echo(f"[cyan]Mobile live reload enabled[/cyan] (target: {mobile_target})")
        typer.echo(f"[dim]Mobile project: {mobile_out_dir}[/dim]")

        # Build mobile project initially
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
        from ..build.mobile_build import build_mobile
        try:
            report = build_mobile(miki_app, out_dir=mobile_out_dir, target_platform=mobile_target)
            if report.get("status") == "ok":
                typer.echo(f"[green]Mobile project built:[/green] {mobile_out_dir}")
        except Exception as exc:
            typer.echo(f"[yellow]Mobile build warning:[/yellow] {exc}", err=True)

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
    target: str = typer.Option("web", "--target", "-t", help="Build target: web | desktop | mobile"),
    mode: str = typer.Option("fullstack", "--mode", "-m", help="Build mode: fullstack | separate"),
    app: str = typer.Option(None, "--app", "-a", help="module:attr of the MikiApp (auto-discovered if omitted)"),
    out_dir: str = typer.Option("dist", "--out", "-o", help="Output directory"),
    theme: str = typer.Option(None, "--theme", help="Compile Tailwind CSS (tailwind)"),
    daisyui: bool = typer.Option(False, "--daisyui/--no-daisyui", help="Enable DaisyUI in the Tailwind build"),
    optimize_css: bool = typer.Option(True, "--optimize/--no-optimize", help="Minify built CSS"),
    watch: bool = typer.Option(False, "--watch", help="Watch mode (rebuild CSS on change) — for dev"),
    clean: bool = typer.Option(False, "--clean", help="Clean output directory before building"),
    backend: str = typer.Option("cloud", "--backend", "-b", help="Mobile backend: cloud | ondevice"),
    target_platform: str = typer.Option("both", "--target-platform", help="Mobile platform: android | ios | both"),
) -> None:
    """Build the app for production.

    Creates an optimized build in the output directory. For web targets,
    this produces static assets. For desktop targets, it generates a launch
    script for a native window. For mobile targets, it generates a Capacitor
    project ready for native compilation.

    Styling is fully automated:

      mikiui build --theme tailwind            # scan + compile Tailwind CSS
      mikiui build --theme tailwind --daisyui  # + DaisyUI component library
      mikiui build --target web                # plain web build (miki.css)
      mikiui build --target desktop            # desktop launcher
      mikiui build --target mobile             # Capacitor project

    Examples:
      mikiui build --target web
      mikiui build --target desktop
      mikiui build --target mobile
      mikiui build --target mobile --backend cloud --target-platform android
      mikiui build --target mobile --backend ondevice --target-platform android
      mikiui build --target web --mode separate --out dist/
      mikiui build --theme tailwind --daisyui
    """
    from ..build import build_desktop, build_web, optimize

    if target not in ("web", "desktop", "mobile"):
        typer.echo(f"[red]Invalid target:[/red] {target} (choose: web, desktop, mobile)", err=True)
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

    # Mobile target delegates to mobile_build
    if target == "mobile":
        from ..build.mobile_build import build_mobile
        try:
            report = build_mobile(
                miki_app,
                out_dir=out_dir,
                backend=backend,
                target_platform=target_platform,
            )
        except ValueError as exc:
            typer.echo(f"[red]Build error:[/red] {exc}", err=True)
            raise typer.Exit(code=1)
        except Exception as exc:
            typer.echo(f"[red]Build failed:[/red] {exc}", err=True)
            raise typer.Exit(code=1)

        typer.echo(f"[green]Build complete:[/green] {report.get('status', 'ok')}")
        typer.echo(f"  Output: {report.get('out_dir', out_dir)}")
        typer.echo(f"  Backend: {report.get('backend')}")
        typer.echo(f"  Platforms: {report.get('platforms')}")
        if report.get("security_warnings"):
            typer.echo("[yellow]Security warnings:[/yellow]")
            for warning in report["security_warnings"]:
                typer.echo(f"  - {warning}")
        typer.echo("")
        typer.echo("Next steps:")
        typer.echo(f"  cd {os.path.basename(out_dir)}")
        typer.echo("  npm install")
        typer.echo("  npx cap sync")
        if target_platform in ("android", "both"):
            typer.echo("  npx cap open android")
        if target_platform in ("ios", "both"):
            typer.echo("  npx cap open ios")
        return

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

    typer.echo(f"[cyan]Building[/cyan] {target} ({mode}) from '{spec}'...")

    # Clean output directory if requested
    if clean and os.path.isdir(out_dir):
        import shutil
        shutil.rmtree(out_dir)
        typer.echo(f"[dim]Cleaned {out_dir}/[/dim]")

    if target == "desktop":
        desktop_out = f"{out_dir}_desktop"
        report = build_desktop(miki_app, out_dir=desktop_out, app_spec=spec)
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


# --- Mobile sub-command group ------------------------------------------------

mobile_cli = typer.Typer(
    help="Mobile build commands (Capacitor-based native apps).",
    no_args_is_help=True,
)
cli.add_typer(mobile_cli, name="mobile")


@mobile_cli.command("build")
def mobile_build(
    target: str = typer.Option("both", "--target", "-t", help="Target platform: android | ios | both"),
    backend: str = typer.Option("cloud", "--backend", "-b", help="Backend mode: cloud | ondevice"),
    app: str = typer.Option(None, "--app", "-a", help="module:attr of the MikiApp"),
    out_dir: str = typer.Option("dist_mobile", "--out", "-o", help="Output directory"),
) -> None:
    """Build a mobile project using Capacitor.

    Generates a complete Capacitor project with native platform files,
    ready to be opened in Android Studio or Xcode.

    Examples:
      mikiui mobile build
      mikiui mobile build --target android --backend cloud
      mikiui mobile build --target android --backend ondevice
    """
    from ..build.mobile_build import build_mobile

    spec = _safe_resolve(app)
    module_name, _, attr = spec.partition(":")
    try:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
    except Exception as exc:
        typer.echo(f"[red]Could not import app '{spec}':[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    try:
        report = build_mobile(miki_app, out_dir=out_dir, backend=backend, target_platform=target)
    except ValueError as exc:
        typer.echo(f"[red]Build error:[/red] {exc}", err=True)
        raise typer.Exit(code=1)
    except Exception as exc:
        typer.echo(f"[red]Build failed:[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"[green]Mobile build complete:[/green] {report.get('status', 'ok')}")
    typer.echo(f"  Output: {report.get('out_dir', out_dir)}")
    typer.echo(f"  Backend: {report.get('backend')}")
    typer.echo(f"  Platforms: {report.get('platforms')}")
    typer.echo("")
    typer.echo("Next steps:")
    typer.echo(f"  cd {os.path.basename(out_dir)}")
    typer.echo("  npm install")
    typer.echo("  npx cap sync")
    if target in ("android", "both"):
        typer.echo("  npx cap open android  # opens in Android Studio")
    if target in ("ios", "both"):
        typer.echo("  npx cap open ios      # opens in Xcode")


@mobile_cli.command("info")
def mobile_info(
    app: str = typer.Option(None, "--app", "-a", help="module:attr of the MikiApp"),
) -> None:
    """Show current mobile configuration.

    Displays the mobile config from the app, including backend mode,
    target platform, plugins, and permissions.
    """
    spec = _safe_resolve(app)
    module_name, _, attr = spec.partition(":")
    try:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
    except Exception as exc:
        typer.echo(f"[red]Could not import app '{spec}':[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    mobile_config = getattr(miki_app, "mobile", None)
    if mobile_config is None:
        typer.echo("[yellow]No mobile config found.[/yellow] Using defaults.")
        from ..app.mobile import MobileConfig
        mobile_config = MobileConfig()

    typer.echo("[bold]Mobile Configuration[/bold]")
    typer.echo(f"  Backend: {mobile_config.backend}")
    typer.echo(f"  Platform: {mobile_config.target_platform}")
    typer.echo(f"  App ID: {mobile_config.app_id}")
    typer.echo(f"  App Name: {mobile_config.app_name or miki_app.title}")
    typer.echo(f"  API Base: {mobile_config.api_base or '(not set)'}")
    typer.echo(f"  WS Base: {mobile_config.ws_base or '(not set)'}")
    typer.echo(f"  Orientation: {mobile_config.orientation}")
    typer.echo(f"  Plugins: {', '.join(mobile_config.plugins) or '(none)'}")
    typer.echo(f"  Capabilities: {', '.join(mobile_config.capabilities) or '(none)'}")

    android_perms = mobile_config.get_android_permissions()
    if android_perms:
        typer.echo(f"  Android Permissions: {', '.join(android_perms)}")

    ios_keys = mobile_config.get_ios_privacy_keys()
    if ios_keys:
        typer.echo(f"  iOS Privacy Keys: {', '.join(ios_keys.keys())}")


@mobile_cli.command("plugins")
def mobile_plugins() -> None:
    """List available Capacitor plugins and their capability mappings."""
    from ..app.mobile import CAPABILITY_MAP

    typer.echo("[bold]Available Capacitor Plugins[/bold]")
    typer.echo("")
    for cap, info in sorted(CAPABILITY_MAP.items()):
        typer.echo(f"  [cyan]{cap}[/cyan]")
        typer.echo(f"    Plugin: {info.get('capacitor_plugin', 'N/A')}")
        if info.get("android_permission"):
            typer.echo(f"    Android: {info['android_permission']}")
        if info.get("ios_privacy_key"):
            typer.echo(f"    iOS: {info['ios_privacy_key']}")
        typer.echo("")


@mobile_cli.command("run")
def mobile_run(
    target: str = typer.Option("android", "--target", "-t", help="Target platform: android | ios"),
    app: str = typer.Option(None, "--app", "-a", help="module:attr of the MikiApp"),
    out_dir: str = typer.Option("dist_mobile", "--out", "-o", help="Output directory"),
    device: str = typer.Option(None, "--device", "-d", help="Device ID (default: first available"),
) -> None:
    """Build and run the mobile app on a connected device or emulator.

    Requires Android Studio (for Android) or Xcode (for iOS) to be installed.

    Examples:
      mikiui mobile run --target android
      mikiui mobile run --target ios --device "iPhone 15 Pro"
    """
    import subprocess

    spec = _safe_resolve(app)
    module_name, _, attr = spec.partition(":")
    try:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
    except Exception as exc:
        typer.echo(f"[red]Could not import app '{spec}':[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    # Build first
    from ..build.mobile_build import build_mobile

    try:
        report = build_mobile(miki_app, out_dir=out_dir, target_platform=target)
    except Exception as exc:
        typer.echo(f"[red]Build failed:[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    if report.get("security_warnings"):
        typer.echo("[yellow]Security warnings:[/yellow]")
        for warning in report["security_warnings"]:
            typer.echo(f"  - {warning}")

    # Run on device
    if target == "android":
        typer.echo("[cyan]Running on Android device/emulator...[/cyan]")
        try:
            subprocess.run(
                ["npx", "cap", "run", "android", "--target", device or ""],
                cwd=out_dir,
                check=True,
            )
        except FileNotFoundError:
            typer.echo("[red]npx not found. Run `npm install` in the project directory first.[/red]", err=True)
            raise typer.Exit(code=1)
        except subprocess.CalledProcessError as exc:
            typer.echo(f"[red]Run failed:[/red] {exc}", err=True)
            raise typer.Exit(code=1)
    elif target == "ios":
        typer.echo("[cyan]Running on iOS simulator/device...[/cyan]")
        try:
            subprocess.run(
                ["npx", "cap", "run", "ios", "--target", device or ""],
                cwd=out_dir,
                check=True,
            )
        except FileNotFoundError:
            typer.echo("[red]npx not found. Run `npm install` in the project directory first.[/red]", err=True)
            raise typer.Exit(code=1)
        except subprocess.CalledProcessError as exc:
            typer.echo(f"[red]Run failed:[/red] {exc}", err=True)
            raise typer.Exit(code=1)
    else:
        typer.echo(f"[red]Invalid target:[/red] {target}", err=True)
        raise typer.Exit(code=1)


@mobile_cli.command("open")
def mobile_open(
    target: str = typer.Option("android", "--target", "-t", help="Target platform: android | ios"),
    app: str = typer.Option(None, "--app", "-a", help="module:attr of the MikiApp"),
    out_dir: str = typer.Option("dist_mobile", "--out", "-o", help="Output directory"),
) -> None:
    """Open the mobile project in the native IDE.

    Opens Android Studio (for Android) or Xcode (for iOS).

    Examples:
      mikiui mobile open --target android
      mikiui mobile open --target ios
    """
    import subprocess

    spec = _safe_resolve(app)
    module_name, _, attr = spec.partition(":")
    try:
        mod = importlib.import_module(module_name)
        miki_app = getattr(mod, attr or "app")
    except Exception as exc:
        typer.echo(f"[red]Could not import app '{spec}':[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    # Build mobile project first
    from ..build.mobile_build import build_mobile

    try:
        build_mobile(miki_app, out_dir=out_dir, target_platform=target)
    except Exception as exc:
        typer.echo(f"[red]Build failed:[/red] {exc}", err=True)
        raise typer.Exit(code=1)

    # Open in IDE
    if target == "android":
        typer.echo("[cyan]Opening in Android Studio...[/cyan]")
        try:
            subprocess.run(["npx", "cap", "open", "android"], cwd=out_dir, check=True)
        except FileNotFoundError:
            typer.echo("[red]npx not found.[/red]", err=True)
            raise typer.Exit(code=1)
    elif target == "ios":
        typer.echo("[cyan]Opening in Xcode...[/cyan]")
        try:
            subprocess.run(["npx", "cap", "open", "ios"], cwd=out_dir, check=True)
        except FileNotFoundError:
            typer.echo("[red]npx not found.[/red]", err=True)
            raise typer.Exit(code=1)
    else:
        typer.echo(f"[red]Invalid target:[/red] {target}", err=True)
        raise typer.Exit(code=1)


@mobile_cli.command("setup")
def mobile_setup() -> None:
    """Interactive mobile setup wizard for beginners."""
    from ..app.mobile import CAPABILITY_MAP, MobileConfig

    typer.echo("[bold]MikiUI Mobile Setup Wizard[/bold]")
    typer.echo("=" * 40)
    typer.echo("")

    # Step 1: Backend mode
    typer.echo("[cyan]Step 1:[/cyan] Choose your backend mode")
    typer.echo("  [1] Cloud (recommended for beginners)")
    typer.echo("      Connects to a remote backend. Smaller app (~8-20MB).")
    typer.echo("  [2] On-device (Android only, advanced)")
    typer.echo("      Runs Python on device. Larger app (~33-40MB). Offline.")
    typer.echo("")
    backend_choice = typer.prompt("Choose (1 or 2)", default="1")
    backend = "cloud" if backend_choice == "1" else "ondevice"

    # Step 2: Target platform
    typer.echo("")
    typer.echo("[cyan]Step 2:[/cyan] Choose your target platform")
    if backend == "ondevice":
        typer.echo("  On-device mode only supports Android.")
        target_platform = "android"
    else:
        typer.echo("  [1] Both iOS and Android (recommended)")
        typer.echo("  [2] Android only")
        typer.echo("  [3] iOS only")
        platform_choice = typer.prompt("Choose (1, 2, or 3)", default="1")
        target_platform = {1: "both", 2: "android", 3: "ios"}.get(int(platform_choice), "both")

    # Step 3: App ID
    typer.echo("")
    typer.echo("[cyan]Step 3:[/cyan] Enter your app ID (e.g. com.example.myapp)")
    app_id = typer.prompt("App ID", default="com.example.myapp")

    # Step 4: App name
    typer.echo("")
    typer.echo("[cyan]Step 4:[/cyan] Enter your app name")
    app_name = typer.prompt("App name", default="My App")

    # Step 5: Plugins
    typer.echo("")
    typer.echo("[cyan]Step 5:[/cyan] Select plugins (comma-separated numbers)")
    plugin_options = list(CAPABILITY_MAP.keys())
    for i, cap in enumerate(plugin_options, 1):
        info = CAPABILITY_MAP[cap]
        typer.echo(f"  [{i}] {cap} ({info.get('capacitor_plugin', 'N/A')})")
    typer.echo("  [0] None (skip)")
    plugin_choice = typer.prompt("Choose plugins (e.g. 1,3,5 or 0)", default="0")

    plugins = []
    if plugin_choice != "0":
        try:
            indices = [int(x.strip()) - 1 for x in plugin_choice.split(",")]
            plugins = [plugin_options[i] for i in indices if 0 <= i < len(plugin_options)]
        except (ValueError, IndexError):
            typer.echo("[yellow]Invalid selection, skipping plugins.[/yellow]")

    # Step 6: API base URL (cloud mode only)
    api_base = None
    if backend == "cloud":
        typer.echo("")
        typer.echo("[cyan]Step 6:[/cyan] Backend API URL (leave empty if not deployed)")
        api_base = typer.prompt("API URL", default="") or None

    # Create config
    config = MobileConfig(
        backend=backend,
        target_platform=target_platform,
        app_id=app_id,
        app_name=app_name,
        plugins=plugins,
        api_base=api_base,
    )

    # Show summary
    typer.echo("")
    typer.echo("[bold]Configuration Summary:[/bold]")
    typer.echo(f"  Backend: {config.backend}")
    typer.echo(f"  Platform: {config.target_platform}")
    typer.echo(f"  App ID: {config.app_id}")
    typer.echo(f"  App Name: {config.app_name}")
    typer.echo(f"  Plugins: {', '.join(config.plugins) or 'None'}")
    typer.echo(f"  API Base: {config.api_base or '(not set)'}")
    typer.echo("")
    typer.echo("[bold]Add this to your app.py:[/bold]")
    typer.echo("")
    typer.echo("from mikiui import MikiApp, Div")
    typer.echo("from mikiui.app.mobile import MobileConfig")
    typer.echo("")
    typer.echo("app = MikiApp(")
    typer.echo(f'    title="{config.app_name}",')
    typer.echo("    mobile=MobileConfig(")
    typer.echo(f'        backend="{config.backend}",')
    typer.echo(f'        target_platform="{config.target_platform}",')
    typer.echo(f'        app_id="{config.app_id}",')
    typer.echo(f'        app_name="{config.app_name}",')
    if plugins:
        typer.echo(f"        plugins={plugins},")
    if api_base:
        typer.echo(f'        api_base="{config.api_base}",')
    typer.echo("    ),")
    typer.echo(")")
    typer.echo("")
    typer.echo("[green]Setup complete![/green] Run [bold]mikiui mobile build[/bold] to generate your mobile project.")


@mobile_cli.command("doctor")
def mobile_doctor() -> None:
    """Check your system for mobile build readiness."""
    import shutil
    import sys

    typer.echo("[bold]MikiUI Mobile Doctor[/bold]")
    typer.echo("Checking your system for mobile build readiness...")
    typer.echo("")

    all_ok = True

    # Check Python
    py_version = sys.version.split()[0]
    typer.echo(f"  [green]OK[/green] Python {py_version}")

    # Check Node.js
    node_path = shutil.which("node")
    if node_path:
        import subprocess
        try:
            node_version = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
            typer.echo(f"  [green]OK[/green] Node.js {node_version}")
        except Exception:
            typer.echo("  [green]OK[/green] Node.js (installed)")
    else:
        typer.echo("  [red]MISSING[/red] Node.js — https://nodejs.org/")
        all_ok = False

    # Check npm
    npm_path = shutil.which("npm")
    if npm_path:
        typer.echo("  [green]OK[/green] npm (installed)")
    else:
        typer.echo("  [red]MISSING[/red] npm — comes with Node.js")
        all_ok = False

    # Check Android Studio (optional)
    android_studio = shutil.which("studio") or shutil.which("android-studio")
    if android_studio:
        typer.echo("  [green]OK[/green] Android Studio (installed)")
    else:
        typer.echo("  [yellow]OPTIONAL[/yellow] Android Studio — https://developer.android.com/studio")

    # Check Xcode (optional, macOS only)
    if sys.platform == "darwin":
        xcode_path = shutil.which("xcodebuild")
        if xcode_path:
            typer.echo("  [green]OK[/green] Xcode (installed)")
        else:
            typer.echo("  [yellow]OPTIONAL[/yellow] Xcode — needed for iOS builds")

    # Check Java (for Android)
    java_path = shutil.which("java")
    if java_path:
        typer.echo("  [green]OK[/green] Java (installed)")
    else:
        typer.echo("  [yellow]OPTIONAL[/yellow] Java — needed for Android builds")

    # Check ANDROID_HOME
    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if android_home:
        typer.echo(f"  [green]OK[/green] ANDROID_HOME={android_home}")
    else:
        typer.echo("  [yellow]OPTIONAL[/yellow] ANDROID_HOME — set for Android builds")

    typer.echo("")
    if all_ok:
        typer.echo("[green]Your system is ready for mobile development![/green]")
        typer.echo("Run [bold]mikiui mobile setup[/bold] to configure your app.")
    else:
        typer.echo("[yellow]Some required tools are missing.[/yellow]")
        typer.echo("Install them and run this check again.")


@mobile_cli.command("publish")
def mobile_publish(
    platform: str = typer.Option(..., "--platform", "-p", help="Platform: android | ios"),
    release: bool = typer.Option(False, "--release/--debug", help="Build release version"),
    out_dir: str = typer.Option("dist_mobile", "--out", "-o", help="Output directory"),
) -> None:
    """Prepare app for publishing to app store.

    This command:
    1. Builds the mobile project
    2. Generates store listing metadata
    3. Creates screenshot templates
    4. Provides step-by-step publishing instructions

    Examples:
      mikiui mobile publish --platform android --release
      mikiui mobile publish --platform ios --release
    """
    import subprocess

    typer.echo(f"[bold]Publishing for {platform}...[/bold]")
    typer.echo("")

    # Step 1: Build
    typer.echo("[cyan]Step 1:[/cyan] Building mobile project...")
    result = subprocess.run(
        ["mikiui", "mobile", "build", "--target", platform, "--out", out_dir],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        typer.echo(f"[red]Build failed:[/red] {result.stderr}", err=True)
        raise typer.Exit(code=1)
    typer.echo("  [green]Build complete![/green]")

    # Step 2: Generate store metadata
    typer.echo("")
    typer.echo("[cyan]Step 2:[/cyan] Generating store metadata...")
    _generate_store_metadata(out_dir, platform)
    typer.echo("  [green]Store metadata generated![/green]")

    # Step 3: Generate screenshot templates
    typer.echo("")
    typer.echo("[cyan]Step 3:[/cyan] Generating screenshot templates...")
    _generate_screenshot_templates(out_dir, platform)
    typer.echo("  [green]Screenshot templates generated![/green]")

    # Step 4: Print instructions
    typer.echo("")
    typer.echo("[bold]Next Steps:[/bold]")
    typer.echo("")

    if platform == "android":
        typer.echo("1. Open the project in Android Studio:")
        typer.echo(f"   cd {out_dir} && npx cap open android")
        typer.echo("")
        typer.echo("2. Generate a signing key:")
        typer.echo("   keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key")
        typer.echo("")
        typer.echo("3. Build a signed bundle:")
        typer.echo("   Build → Generate Signed Bundle/APK → Android App Bundle")
        typer.echo("")
        typer.echo("4. Upload to Play Console:")
        typer.echo("   https://play.google.com/console")
        typer.echo("")
        typer.echo("5. Fill in store listing:")
        typer.echo(f"   See {out_dir}/store/android/ for templates")
    elif platform == "ios":
        typer.echo("1. Open the project in Xcode:")
        typer.echo(f"   cd {out_dir} && npx cap open ios")
        typer.echo("")
        typer.echo("2. Select your signing team:")
        typer.echo("   Project → Signing & Capabilities → Team")
        typer.echo("")
        typer.echo("3. Archive the app:")
        typer.echo("   Product → Archive")
        typer.echo("")
        typer.echo("4. Upload to App Store Connect:")
        typer.echo("   Window → Organizer → Distribute App")
        typer.echo("")
        typer.echo("5. Fill in store listing:")
        typer.echo(f"   See {out_dir}/store/ios/ for templates")

    typer.echo("")
    typer.echo("[green]Done![/green] Follow the steps above to publish your app.")


def _generate_store_metadata(out_dir: str, platform: str) -> None:
    """Generate store listing metadata templates."""
    import json

    store_dir = os.path.join(out_dir, "store", platform)
    os.makedirs(store_dir, exist_ok=True)

    # Common metadata
    metadata = {
        "app_title": "My App",
        "short_description": "A short description of your app (80 characters max)",
        "full_description": "A full description of your app (4000 characters max)",
        "category": "Productivity",
        "tags": ["python", "mikiui", "productivity"],
        "privacy_policy_url": "https://example.com/privacy",
        "support_url": "https://example.com/support",
        "marketing_url": "https://example.com",
        "content_rating": "Everyone",
    }

    if platform == "android":
        metadata.update({
            "package_name": "com.example.app",
            "content_rating_categories": ["Everyone"],
            "target_audience": ["Everyone"],
            "permissions": [
                {"permission": "CAMERA", "reason": "Take photos"},
                {"permission": "ACCESS_FINE_LOCATION", "reason": "Find nearby places"},
            ],
        })
    elif platform == "ios":
        metadata.update({
            "bundle_id": "com.example.app",
            "sku": "com.example.app",
            "primary_language": "en-US",
            "languages": ["en-US"],
        })

    with open(os.path.join(store_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Store listing template
    listing = f"""# Store Listing for {platform.title()}

## App Title
{metadata['app_title']}

## Short Description (80 characters)
{metadata['short_description']}

## Full Description (4000 characters)
{metadata['full_description']}

## Keywords
{', '.join(metadata['tags'])}

## Category
{metadata['category']}

## Privacy Policy
{metadata['privacy_policy_url']}

## Support URL
{metadata['support_url']}

## Content Rating
{metadata['content_rating']}
"""

    with open(os.path.join(store_dir, "listing.md"), "w", encoding="utf-8") as f:
        f.write(listing)


def _generate_screenshot_templates(out_dir: str, platform: str) -> None:
    """Generate screenshot size requirements and templates."""
    store_dir = os.path.join(out_dir, "store", platform)
    os.makedirs(store_dir, exist_ok=True)

    if platform == "android":
        sizes = [
            {"name": "phone", "width": 1080, "height": 1920, "required": True},
            {"name": "7inch_tablet", "width": 1024, "height": 1600, "required": True},
            {"name": "10inch_tablet", "width": 1200, "height": 1920, "required": True},
            {"name": "feature_graphic", "width": 1024, "height": 500, "required": True},
        ]
    elif platform == "ios":
        sizes = [
            {"name": "6.7_inch", "width": 1290, "height": 2796, "required": True},
            {"name": "6.5_inch", "width": 1284, "height": 2778, "required": True},
            {"name": "5.5_inch", "width": 1242, "height": 2208, "required": True},
            {"name": "ipad_pro_12.9", "width": 2048, "height": 2732, "required": True},
            {"name": "ipad_pro_11", "width": 1668, "height": 2388, "required": True},
        ]

    # Generate requirements file
    requirements = f"# Screenshot Requirements for {platform.title()}\n\n"
    requirements += "Required screenshots:\n\n"

    for size in sizes:
        req = "REQUIRED" if size["required"] else "Optional"
        requirements += f"- {size['name']}: {size['width']}x{size['height']} ({req})\n"

    requirements += "\n## Tips\n"
    requirements += "- Use real device screenshots when possible\n"
    requirements += "- Show your app's main features\n"
    requirements += "- Add text overlays to highlight key functionality\n"
    requirements += "- Use bright, eye-catching colors\n"

    with open(os.path.join(store_dir, "screenshot_requirements.md"), "w", encoding="utf-8") as f:
        f.write(requirements)

    # Generate placeholder HTML for screenshots
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Screenshot Template</title>
    <style>
        body { margin: 0; display: flex; flex-direction: column; align-items: center; padding: 20px; background: #f0f0f0; }
        .screenshot { margin: 20px; border: 2px dashed #ccc; display: flex; align-items: center; justify-content: center; color: #999; font-family: sans-serif; }
    </style>
</head>
<body>
    <h1>Screenshot Templates</h1>
"""

    for size in sizes:
        html += f'    <div class="screenshot" style="width:{size["width"]}px;height:{size["height"]}px;">\n'
        html += f'        {size["name"]} - {size["width"]}x{size["height"]}\n'
        html += f'    </div>\n'

    html += """</body>
</html>"""

    with open(os.path.join(store_dir, "screenshot_template.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    cli()
