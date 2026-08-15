# Styling Guide

MikiUI's styling system has three layers:

1. **Base layer** — `miki.css`, always loaded. Provides `--miki-*` CSS custom
   properties and `miki-*` component classes.
2. **Framework layer** — Tailwind CSS, Bootstrap, or plain CSS. Users pick
   one during `mikiui new` or via `mikiui install`.
3. **Color theme layer** — light, dark, dracula, solarized-dark. Controls the
   actual color palette via CSS variables.

This guide covers choosing a framework, setting up Tailwind or Bootstrap,
and using custom CSS.

## Table of Contents

- [Choosing a Framework](#choosing-a-framework)
- [Tailwind CSS](#tailwind-css)
  - [Setup](#setup)
  - [Development Workflow](#development-workflow)
  - [DaisyUI](#daisyui)
  - [Production Build](#production-build)
- [Bootstrap](#bootstrap)
  - [Setup](#setup-1)
  - [CDN vs Local Files](#cdn-vs-local-files)
  - [Custom CSS](#custom-css)
- [Plain CSS](#plain-css)
- [Custom CSS Files](#custom-css-files)
- [Switching Frameworks](#switching-frameworks)
- [Troubleshooting](#troubleshooting)

## Choosing a Framework

When you run `mikiui new myapp`, you will be prompted to choose a CSS
framework:

```
Select a CSS framework for your MikiUI project:

  1. tailwind   — Tailwind CSS — utility-first, JIT compilation (requires Node.js)
  2. bootstrap  — Bootstrap 5 — CDN or local files + custom CSS
  3. plain      — Plain CSS — no framework, just your own styles

Enter choice [1-3] (default: 1):
```

You can also skip the prompt with `--framework`:

```bash
mikiui new myapp --framework bootstrap
mikiui new myapp --framework plain
mikiui new myapp --framework daisyui   # Tailwind + DaisyUI
```

### Which framework should I choose?

| Framework | Best for | Requires Node.js |
|-----------|----------|-----------------|
| Tailwind | Utility-first styling, full control, JIT builds | Yes |
| Bootstrap | Quick prototypes, familiar component classes | No |
| Plain CSS | Full control, no dependencies | No |

## Tailwind CSS

### Setup

After creating a Tailwind project:

```bash
cd myapp
npm install
```

This installs `tailwindcss`, `postcss`, `autoprefixer`, and optionally
`daisyui`. If Node.js is not installed, `mikiui new` and `mikiui install`
will tell you exactly what to do.

### Development Workflow

**Terminal 1 — Python dev server:**

```bash
mikiui dev
```

This starts the FastAPI server at `http://127.0.0.1:8000` with hot-reload.

**Terminal 2 — Tailwind CSS watcher (optional but recommended):**

```bash
mikiui tailwind dev
```

This watches your Python files for `miki-*` and Tailwind class changes and
rebuilds `mikiui/runtime/themes/tailwind.css` automatically.

If you don't run `mikiui tailwind dev`, Tailwind classes will still work in
dev mode — MikiUI falls back to the Tailwind CDN so styles load immediately.

### DaisyUI

DaisyUI is a component library built on Tailwind CSS. To enable it:

```bash
mikiui install tailwind daisyui
```

Or if you already have Tailwind set up:

```bash
mikiui tailwind build --daisyui
```

DaisyUI themes are automatically bridged to MikiUI color themes. Set a
MikiUI theme and DaisyUI picks the matching palette:

```python
app.set_theme("dark")  # Uses mikiui-dark DaisyUI theme
```

### Production Build

```bash
mikiui build --target web --theme tailwind
```

This:

1. Scans your components and widgets for used classes
2. Runs Tailwind JIT to generate optimized CSS
3. Outputs to `dist/_miki/runtime/themes/tailwind.css`
4. Copies runtime assets (HTMX, Alpine.js, miki.css)

With DaisyUI:

```bash
mikiui build --target web --theme tailwind --daisyui
```

### Tailwind CLI Commands

MikiUI provides a `tailwind` subcommand group:

```bash
mikiui tailwind dev      # Watch and rebuild CSS on change
mikiui tailwind build    # One-shot production build
mikiui tailwind watch    # Alias for dev
```

### Tailwind Config Files

`mikiui new` creates `tailwind.config.js` and `postcss.config.js` for you.
You can regenerate them at any time:

```bash
mikiui install tailwind
```

### Using Tailwind Classes

Add Tailwind utility classes via the `class_` parameter:

```python
from mikiui import MikiApp, Div, Button

app = MikiApp()

@app.route("/")
def home():
    return Div(
        Button("Click me", class_="bg-blue-500 text-white px-4 py-2 rounded"),
        class_="flex items-center justify-center h-screen",
    )
```

## Bootstrap

### Setup

Bootstrap works without any setup — no Node.js, no build step. After
creating a Bootstrap project:

```bash
cd myapp
mikiui dev
```

Bootstrap CSS and JS are loaded from the jsDelivr CDN by default.

### CDN vs Local Files

**CDN (default):** works immediately, no files needed.

**Local files:** for offline use or custom builds:

1. Download Bootstrap from https://getbootstrap.com/
2. Place files in `static/`:

   ```
   static/
     bootstrap.min.css
     bootstrap.bundle.min.js
   ```

3. Reference them in `app.py`:

   ```python
   app.add_head_link("/static/bootstrap.min.css", rel="stylesheet")
   app.add_head_script("/static/bootstrap.bundle.min.js")
   ```

### Custom CSS

Add your own CSS files alongside Bootstrap:

```python
app.add_head_link("/static/custom.css", rel="stylesheet")
```

## Plain CSS

When you choose "plain" during `mikiui new`, no framework is loaded.
You are responsible for all styling.

Add CSS files in `static/` and reference them:

```python
app.add_head_link("/static/styles.css", rel="stylesheet")
```

## Custom CSS Files

All three frameworks support additional custom CSS files. This is useful for:

- Overriding framework defaults
- Adding animations
- Loading Google Fonts

```python
app.add_head_link("https://fonts.googleapis.com/css2?family=Inter", rel="stylesheet")
app.add_head_link("/static/overrides.css", rel="stylesheet")
```

Order matters: framework CSS loads first, then custom CSS. This means your
custom styles can override framework defaults.

## Switching Frameworks

To change the framework of an existing project:

```bash
# To Tailwind:
mikiui install tailwind
# Edit app.py: app.set_theme("tailwind")

# To Bootstrap:
mikiui install bootstrap
# Edit app.py: app.set_theme("bootstrap")

# To plain CSS:
# Edit app.py: app.set_theme("light")
# Remove tailwind.config.js and package.json if present
```

## Troubleshooting

### Node.js not found

```
[yellow]Node.js is required for Tailwind CSS.[/yellow]
```

Install Node.js from https://nodejs.org/ and re-run `mikiui install tailwind`.

### Tailwind classes not applying

1. Make sure you ran `mikiui install tailwind` and `npm install`
2. In dev mode, Tailwind falls back to CDN — classes should work immediately
3. In prod mode, run `mikiui build --target web --theme tailwind`
4. Check that class names are spelled correctly (Tailwind is case-sensitive)

### Bootstrap styles missing

1. Verify the CDN is reachable (check browser console for 404s)
2. For local files, verify paths in `app.py` match actual file locations
3. Ensure Bootstrap CSS loads before your custom CSS

### CSS changes not showing

1. Clear browser cache or use incognito mode
2. For Tailwind, make sure `mikiui tailwind dev` is running (or use CDN)
3. For production builds, rebuild with `mikiui build`
