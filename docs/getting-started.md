# Getting Started with MikiUI

This guide walks you through installing MikiUI, creating your first project,
choosing a styling framework, and running your app in development or production.

## Prerequisites

- **Python 3.14 or later**
- **pip** (usually included with Python)
- **Node.js 18+** (only required if you choose Tailwind CSS)

## Installation

Install MikiUI from the project root:

```bash
cd /path/to/mikiUI
pip install -e .
```

Verify the installation:

```bash
mikiui --help
```

You should see the MikiUI banner with available commands.

## Create Your First Project

Run `mikiui new` and follow the prompts:

```bash
mikiui new myapp
```

You will be asked:

1. **Project name** — defaults to `myapp`
2. **CSS framework** — choose one:

   | Option | Description |
   |--------|-------------|
   | `1. tailwind` | Tailwind CSS + optional DaisyUI (requires Node.js) |
   | `2. bootstrap` | Bootstrap 5 — CDN or local files + custom CSS |
   | `3. plain` | Plain CSS — no framework, just your own styles |

### What gets created

```
myapp/
  app.py              # Your MikiUI application
  README.md           # Framework-specific instructions
  requirements.txt    # Python dependencies
  static/             # Custom CSS directory
  .mikiui.json        # Project config (framework, theme)
```

For Tailwind projects, two additional files are created:

```
  tailwind.config.js  # Tailwind configuration
  postcss.config.js   # PostCSS configuration (required by Tailwind)
```

### Framework-specific setup

#### Tailwind CSS

Tailwind requires Node.js. If you don't have it installed:

1. Download Node.js from https://nodejs.org/
2. Re-run `mikiui new myapp --framework tailwind`

Once Node.js is available, install dependencies:

```bash
cd myapp
npm install
```

This installs `tailwindcss`, `postcss`, and `autoprefixer` (and `daisyui` if
you selected it).

To add DaisyUI later:

```bash
mikiui install tailwind daisyui
```

#### Bootstrap

Bootstrap works out of the box — no Node.js required. By default, Bootstrap
CSS and JS are loaded from the jsDelivr CDN.

To use local Bootstrap files:

1. Download `bootstrap.min.css` and `bootstrap.bundle.min.js`
2. Place them in `static/`
3. Add to your `app.py`:

   ```python
   app.add_head_link("/static/bootstrap.min.css", rel="stylesheet")
   app.add_head_script("/static/bootstrap.bundle.min.js")
   ```

#### Plain CSS

No setup required. Add your own CSS files in `static/` and reference them:

```python
app.add_head_link("/static/styles.css", rel="stylesheet")
```

## Run Your App

### Development server

```bash
mikiui dev
```

This starts a FastAPI server with hot-reloading at `http://127.0.0.1:8000`.

**Tailwind users:** run `mikiui tailwind dev` in a second terminal to watch
and rebuild CSS on every change.

```bash
# Terminal 1
mikiui dev

# Terminal 2
mikiui tailwind dev
```

### Desktop window

```bash
mikiui desktop
```

This opens a native window (requires `pywebview`). If `pywebview` is not
installed, it falls back to your system browser.

## Build for Production

### Web build

```bash
mikiui build --target web
```

This copies runtime assets (HTMX, Alpine.js, miki.css) to `dist/`.

For Tailwind projects, add `--theme tailwind` to compile CSS:

```bash
mikiui build --target web --theme tailwind
```

With DaisyUI:

```bash
mikiui build --target web --theme tailwind --daisyui
```

### Desktop build

```bash
mikiui build --target desktop
```

This produces a `dist_desktop/` directory with a web build plus a
`launch.py` script. Package it with PyInstaller or similar tools.

## Styling Workflow Summary

```
mikiui new myapp
  → Choose framework (tailwind / bootstrap / plain)
  → Config files written automatically

cd myapp

# Tailwind path:
npm install              # Install Node.js deps
mikiui dev               # Start server
mikiui tailwind dev      # Watch CSS (second terminal)

# Bootstrap / plain path:
mikiui dev               # Start server (no extra steps)

# Production:
mikiui build --target web --theme tailwind   # Tailwind
mikiui build --target web                     # Bootstrap / plain
```

## Switching Frameworks

To change the styling framework of an existing project:

```bash
# Switch to Tailwind:
mikiui install tailwind
# Then edit app.py: app.set_theme("tailwind")

# Switch to Bootstrap:
mikiui install bootstrap
# Then edit app.py: app.set_theme("bootstrap")
```

## Next Steps

- Read the [Styling Guide](styling.md) for framework-specific details
- Browse [Component Reference](components.md) for available widgets
- See [Theme Reference](theme-reference.md) for color themes and variables
