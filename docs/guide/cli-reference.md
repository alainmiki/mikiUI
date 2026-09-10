# CLI Reference

MikiUI ships with a CLI for scaffolding, development, and building.

## Global Options

```bash
mikiui --help
mikiui --version
```

## Commands

### `mikiui new <name>`

Scaffold a new MikiUI project.

```bash
mikiui new myapp
cd myapp
```

Creates:
- `app.py` — starter app with example routes
- `requirements.txt` — Python dependencies
- `static/` — custom CSS and assets
- `tailwind.config.js` + `postcss.config.js` (if Tailwind selected)
- `package.json` (if Tailwind selected)

### `mikiui dev`

Start the development server with hot-reload.

```bash
mikiui dev
mikiui dev --app myapp:app
mikiui dev --port 8080
```

Options:
- `--app` — app spec (`module:attr`), default: auto-discovery
- `--port` — port number, default: `8000`
- `--reload` — enable auto-reload (default in dev mode)

### `mikiui desktop`

Open a native desktop window using pywebview.

```bash
mikiui desktop
mikiui desktop --reload
mikiui desktop --browser
mikiui desktop --width 1280 --height 800
```

Options:
- `--reload` — auto-refresh on file changes
- `--browser` — force browser fallback instead of native window
- `--width` — window width in pixels
- `--height` — window height in pixels

### `mikiui build`

Build the app for production.

```bash
# Web build (fullstack by default)
mikiui build --target web

# Static site only
mikiui build --target web --mode separate

# Desktop package
mikiui build --target desktop

# Single-file desktop executable
mikiui build --target desktop --onefile

# With Tailwind CSS
mikiui build --target web --framework tailwind --daisyui

# Clean build
mikiui build --target web --clean
```

Options:
- `--target` — `web` or `desktop`
- `--mode` — `fullstack` or `separate` (web only)
- `--out` — output directory
- `--framework` — `plain` or `tailwind`
- `--style-mode` — `cdn` or `local` (Tailwind only)
- `--daisyui` — enable DaisyUI (Tailwind only)
- `--theme` — color theme name
- `--icon` — path to icon file (`.ico`, `.icns`, `.png`)
- `--onefile` — single-file executable (desktop only)
- `--clean` — remove output directory before building
- `--optimize` — minify assets
- `--no-optimize` — skip minification

### `mikiui tailwind dev`

Watch and rebuild Tailwind CSS on changes.

```bash
mikiui tailwind dev
```

Scans Python files for `miki-*` and Tailwind class changes and rebuilds CSS automatically.

### `mikiui tailwind build`

One-shot production Tailwind build.

```bash
mikiui tailwind build
```

### `mikiui install tailwind`

Install Tailwind CSS and dependencies.

```bash
mikiui install tailwind
mikiui install tailwind daisyui
```

Creates:
- `tailwind.config.js`
- `postcss.config.js`
- Updates `package.json`

Options:
- `--no-deps` — skip `npm install`

## Examples

```bash
# Development workflow
mikiui dev                    # Terminal 1: Python server
mikiui tailwind dev           # Terminal 2: Tailwind watcher

# Production web build
mikiui build --target web --mode fullstack --framework tailwind --daisyui

# Desktop app
mikiui build --target desktop --icon app.ico

# Static site for GitHub Pages
mikiui build --target web --mode separate --out dist/
```
