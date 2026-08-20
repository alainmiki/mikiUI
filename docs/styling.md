# Theme Reference

This reference covers all built-in themes, CSS variables, framework selection,
and how to create custom themes.

## Quick Start

```python
from mikiui import MikiApp

app = MikiApp(title="My App")
app.set_theme("dark")                     # color theme
app.set_style_framework("tailwind")       # CSS framework
```

## Built-in Color Themes

| Name | Description |
|------|-------------|
| `light` | Clean light theme (default) |
| `dark` | Modern dark theme with vibrant accents |
| `dracula` | Purple/cyan/pink dark palette |
| `solarized-dark` | Muted, warm, low-contrast dark |
| `cupcake` | Soft pink/purple pastel |
| `synthwave` | Neon pink/purple retro |
| `corporate` | Professional blue/gray |
| `emerald` | Green-focused palette |
| `bumblebee` | Yellow/black high-contrast |
| `retro` | Vintage warm tones |
| `aqua` | Cyan/teal aquatic |
| `cyberpunk` | Neon yellow/black |
| `forest` | Deep greens and browns |
| `garden` | Fresh green/floral |
| `halloween` | Orange/black spooky |
| `pastel` | Soft muted colors |
| `valentine` | Red/pink romantic |

### Theme Variables

Each theme is a CSS file that sets these custom properties:

| Variable | Default (light) | Description |
|----------|-----------------|-------------|
| `--miki-bg` | `#ffffff` | Page / component background |
| `--miki-fg` | `#1e2937` | Text color |
| `--miki-accent` | `#3b82f6` | Primary accent color |
| `--miki-accent-hover` | `#2563eb` | Accent hover state |
| `--miki-border` | `#d1d5db` | Border color |
| `--miki-border-hover` | `#9ca3af` | Border hover state |
| `--miki-surface` | `#f9fafb` | Surface / card background |
| `--miki-surface-hover` | `#f3f4f6` | Surface hover state |
| `--miki-surface-active` | `#e5e7eb` | Surface active state |
| `--miki-input-bg` | `#ffffff` | Input background |
| `--miki-input-border` | `#d1d5db` | Input border |
| `--miki-input-focus` | `#3b82f6` | Input focus ring |
| `--miki-text-muted` | `#6b7280` | Muted text |
| `--miki-text-secondary` | `#374151` | Secondary text |
| `--miki-shadow` | `0 1px 3px rgba(0,0,0,0.1)` | Default shadow |
| `--miki-shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Large shadow |
| `--miki-shadow-xl` | `0 20px 25px rgba(0,0,0,0.1)` | Extra large shadow |
| `--miki-radius` | `0.5rem` | Default border radius |
| `--miki-radius-lg` | `0.75rem` | Large border radius |
| `--miki-transition` | `0.15s ease` | Default transition |
| `--miki-success` | `#22c55e` | Success color |
| `--miki-warning` | `#facc15` | Warning color |
| `--miki-error` | `#ef4444` | Error color |
| `--miki-dock-width` | `300px` | Default dock width |
| `--miki-dock-height` | `300px` | Default dock height |
| `--miki-float-width` | `40vw` | Default float width |
| `--miki-float-height` | `50vh` | Default float height |

## CSS Frameworks

Framework selection controls how styles are delivered. It is separate from
the color theme.

| Framework | Description | Node.js Required |
|-----------|-------------|-----------------|
| `plain` | Plain CSS — loads `miki.css` + color theme CSS | No |
| `tailwind` | Tailwind CSS — CDN or local JIT build | Yes |

### Setting the Framework

```python
from mikiui import MikiApp

app = MikiApp()

# Plain CSS (default)
app.set_style_framework("plain")
app.set_theme("dark")

# Tailwind — CDN mode (instant, no build)
app.set_style_framework("tailwind", mode="cdn")
app.set_theme("dark")

# Tailwind — local JIT mode (production)
app.set_style_framework("tailwind", mode="local")
app.set_theme("dark")

# Tailwind + DaisyUI
app.set_style_framework("tailwind", mode="cdn", daisyui=True)
app.set_theme("dracula")
```

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

To add Tailwind to an existing project:

```bash
mikiui install tailwind
```

### CDN vs Local JIT

| Mode | How it works | When to use |
|------|--------------|-------------|
| `cdn` | Loads Tailwind from jsDelivr CDN | Development, quick prototypes |
| `local` | Serves locally built CSS from `/_miki/runtime/themes/tailwind.css` | Production, offline, mobile |

### DaisyUI

DaisyUI is a component library built on Tailwind CSS. To enable it:

```python
app.set_style_framework("tailwind", mode="cdn", daisyui=True)
```

Or from the CLI:

```bash
mikiui install tailwind daisyui
```

DaisyUI themes are automatically bridged to MikiUI color themes. When you set a
MikiUI color theme, the matching DaisyUI palette is applied:

```python
app.set_theme("dark")  # Uses mikiui-dark DaisyUI theme
```

### Development Workflow

**Terminal 1 — Python dev server:**

```bash
mikiui dev
```

This starts the FastAPI server at `http://127.0.0.1:8000` with hot-reload.

**Terminal 2 — Tailwind CSS watcher (local mode only):**

```bash
mikiui tailwind dev
```

This watches your Python files for `miki-*` and Tailwind class changes and
rebuilds `mikiui/runtime/themes/tailwind.css` automatically.

In CDN mode, no watcher is needed — styles load from the CDN immediately.

### Production Build

```bash
mikiui build --target web --theme dark --framework tailwind
```

Or with DaisyUI:

```bash
mikiui build --target web --theme dark --framework tailwind --daisyui
```

This:

1. Runs Tailwind JIT to generate optimized CSS
2. Renders all routes to static HTML
3. Copies runtime assets (HTMX, Alpine.js)
4. Generates CSP nonces and manifest

### Tailwind CLI Commands

MikiUI provides a `tailwind` subcommand group:

```bash
mikiui tailwind dev      # Watch and rebuild CSS on change (local mode)
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

---

## Plain CSS

Plain CSS is the default. It loads `miki.css` (the base stylesheet) plus the
active color theme CSS. No Node.js, no build step.

```python
from mikiui import MikiApp

app = MikiApp()
app.set_style_framework("plain")
app.set_theme("dark")
```

### Adding custom CSS

```python
app.add_head_link("/static/styles.css", rel="stylesheet")
```

---

## Switching Frameworks

To change the framework of an existing project:

```python
# In app.py:

# To Tailwind CDN:
app.set_style_framework("tailwind", mode="cdn")

# To Tailwind + DaisyUI:
app.set_style_framework("tailwind", mode="cdn", daisyui=True)

# To plain CSS:
app.set_style_framework("plain")
```

Or via CLI:

```bash
mikiui install tailwind    # sets up Tailwind + npm deps
```

---

## Troubleshooting

### Node.js not found

```
Node.js is required for Tailwind CSS.
```

Install Node.js from https://nodejs.org/ and re-run `mikiui install tailwind`.

### Tailwind classes not applying

1. Make sure you ran `mikiui install tailwind` and `npm install`
2. In CDN mode, classes should work immediately
3. In local mode, run `mikiui tailwind dev` or `mikiui build --framework tailwind`
4. Check that class names are spelled correctly (Tailwind is case-sensitive)

### CSS changes not showing

1. Clear browser cache or use incognito mode
2. For Tailwind local mode, make sure `mikiui tailwind dev` is running
3. For production builds, rebuild with `mikiui build --framework tailwind`
