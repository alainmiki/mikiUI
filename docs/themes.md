# Theming Guide

MikiUI themes control the visual appearance of your application. There are
two independent concepts:

1. **Color themes** — light, dark, dracula, solarized-dark, etc. Control the
   actual color palette via CSS variables.
2. **CSS frameworks** — `plain` or `tailwind`. Control how styles are
   processed and delivered.

You mix and match them independently:

```python
app.set_theme("dark")                    # color theme
app.set_style_framework("tailwind")      # CSS framework
```

## Built-in Color Themes

| Name | Preview |
|------|---------|
| `light` | White backgrounds, dark text |
| `dark` | Dark backgrounds, light text, blue accents |
| `dracula` | Purple backgrounds, cyan/pink accents |
| `solarized-dark` | Warm dark backgrounds, muted colors |

Set a color theme with one line:

```python
from mikiui import MikiApp

app = MikiApp(title="My App")
app.set_theme("dark")
```

## How Themes Work

Each color theme is a CSS file in `mikiui/runtime/themes/` that sets CSS
custom properties (`--miki-bg`, `--miki-fg`, `--miki-accent`, etc.). The
base `miki.css` consumes these variables, so switching themes is instant.

When you set a theme, MikiUI:

1. Inlines the theme's CSS into `<style id="miki-theme">` in the page `<head>`
2. Sets `data-miki-theme="{name}"` on the `<body>` tag
3. If a framework theme is active, injects the framework CSS links

## CSS Frameworks

Framework selection controls how styles are delivered. It is separate from
the color theme.

| Framework | What it does |
|-----------|-------------|
| `plain` | Loads `miki.css` + color theme CSS (default) |
| `tailwind` | Loads Tailwind CSS (CDN in dev, compiled in prod) |

### Choosing a framework

The easiest way is during project creation:

```bash
mikiui new myapp
# Follow the interactive prompts
```

Or specify it directly:

```bash
mikiui new myapp --framework tailwind
mikiui new myapp --framework plain
```

Or in code:

```python
from mikiui import MikiApp

app = MikiApp()

# Plain CSS (default)
app.set_style_framework("plain")

# Tailwind — CDN mode
app.set_style_framework("tailwind", mode="cdn")

# Tailwind — local JIT mode
app.set_style_framework("tailwind", mode="local")

# Tailwind + DaisyUI
app.set_style_framework("tailwind", mode="cdn", daisyui=True)
```

### Tailwind + DaisyUI

DaisyUI extends Tailwind with pre-built component themes. Enable it with:

```bash
mikiui install tailwind daisyui
```

Or in code:

```python
app.set_style_framework("tailwind", mode="cdn", daisyui=True)
```

DaisyUI themes are automatically bridged to MikiUI color themes. When you
set `app.set_theme("dark")`, the `mikiui-dark` DaisyUI theme is applied.

## Custom Themes

### Custom Color Theme

Create a CSS file:

```css
/* static/my-brand.css */
:root {
  --miki-bg: #0f172a;
  --miki-fg: #f1f5f9;
  --miki-accent: #22d3ee;
  --miki-border: #1e293b;
}
```

Register it:

```python
from mikiui import MikiApp, Theme

app = MikiApp()

my_theme = Theme(
    name="my-brand",
    source="custom",
    css_path="/static/my-brand.css",
)
app.register_theme(my_theme)
app.set_theme("my-brand")
```

### Custom Framework Theme

Combine a framework with custom colors:

```python
from mikiui import MikiApp, Theme

app = MikiApp()

my_tailwind = Theme(
    name="my-tailwind",
    framework="tailwind",
    cdn_url="https://cdn.jsdelivr.net/npm/tailwindcss@4/dist/tailwind.min.css",
    variables={
        "--miki-accent": "#f472b6",
    },
)
app.register_theme(my_tailwind)
app.set_theme("my-tailwind")
```

## Theme System Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Page <head>                                            │
│                                                         │
│  Plain CSS mode:                                        │
│    1. miki.css (base styles)                            │
│    2. <style id="miki-theme">...</style> (color theme) │
│    3. Custom CSS links                                  │
│                                                         │
│  Tailwind mode:                                         │
│    1. Tailwind CSS (CDN or local)                       │
│    2. DaisyUI CSS (if enabled)                          │
│    3. data-theme="mikiui-{name}" on <body>             │
│                                                         │
│  Both modes:                                            │
│    4. HTMX + Alpine.js scripts                          │
└─────────────────────────────────────────────────────────┘
```

The order is important: framework CSS loads first, then base styles, then
the color theme, then your overrides.

## Switching Themes at Runtime

```python
# Change theme on the fly
app.set_theme("dracula")

# Get the current theme name
current = app.theme  # "dracula"

# Get full theme config
config = app.theme_config()
# {"name": "dracula", "framework": None, "variables": {...}}
```

## Using with Plugins

Plugins can register themes that are automatically available:

```python
from mikiui.app import Plugin, Theme
from mikiui.themes import register_theme

class DarkModePlugin(Plugin):
    def register(self, app):
        theme = Theme(
            name="plugin-dark",
            source="plugin",
            framework="tailwind",
            css_path="/_miki/runtime/plugin-dark.css",
        )
        register_theme(theme)

app = MikiApp()
app.use(DarkModePlugin())
app.set_theme("plugin-dark")
```

## File Structure

```
myapp/
  app.py                    # Your app
  static/
    custom.css              # Your custom styles
  mikiui/
    runtime/
      miki.css              # Base styles (always loaded)
      themes/
        light.css           # Color theme CSS
        dark.css
        dracula.css
        solarized-dark.css
      tailwind.css          # Compiled Tailwind (generated by build)
```

In development, files in `mikiui/runtime/` are served automatically at
`/_miki/runtime/`.
