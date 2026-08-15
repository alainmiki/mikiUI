# Theme Reference

This reference covers all built-in themes, framework themes, CSS variables,
and how to create custom themes.

## Quick Start

```python
from mikiui import MikiApp

app = MikiApp(title="My App")
app.set_theme("dark")  # Options: light, dark, dracula, solarized-dark
```

## Built-in Color Themes

| Name | Description |
|------|-------------|
| `light` | Clean light theme (default) |
| `dark` | Modern dark theme with vibrant accents |
| `dracula` | Purple/cyan/pink dark palette |
| `solarized-dark` | Muted, warm, low-contrast dark |

### Theme Variables

Each theme is a CSS file that sets these custom properties:

| Variable | Default (light) | Description |
|----------|-----------------|-------------|
| `--miki-bg` | `#ffffff` | Page / component background |
| `--miki-fg` | `#1e293b` | Text color |
| `--miki-accent` | `#3b82f6` | Primary accent color |
| `--miki-accent-hover` | `#60a5fa` | Accent hover state |
| `--miki-border` | `#e2e8f0` | Border color |
| `--miki-radius` | `0.375rem` | Border radius |
| `--miki-font` | `system-ui` | Font family |
| `--miki-size` | `1rem` | Base font size |

## Framework Themes

Framework themes change how CSS is loaded and processed.

| Name | Framework | CDN | Local |
|------|-----------|-----|-------|
| `tailwind` | Tailwind CSS 3.4 | Yes | Yes |
| `bootstrap` | Bootstrap 5.3 | Yes | Yes |

### Using Framework Themes

The easiest way is during project creation:

```bash
mikiui new myapp --framework tailwind
mikiui new myapp --framework bootstrap
```

Or on an existing project:

```python
from mikiui import MikiApp

app = MikiApp()

# Tailwind (CDN in dev, local build in prod)
app.set_theme("tailwind")

# Bootstrap (CDN)
app.set_theme("bootstrap")
```

### Tailwind

In development, Tailwind CSS is loaded from the jsDelivr CDN so classes
work immediately without a build step.

In production, run:

```bash
mikiui build --target web --theme tailwind
```

This compiles only the classes you actually use into a single CSS file.

### DaisyUI

DaisyUI is a Tailwind plugin that provides pre-built component classes.
Enable it with:

```bash
mikiui install tailwind daisyui
mikiui build --target web --theme tailwind --daisyui
```

DaisyUI themes are automatically bridged to MikiUI themes. When you set a
MikiUI color theme, the matching DaisyUI palette is applied:

```python
app.set_theme("dark")  # Uses mikiui-dark DaisyUI theme
```

### Bootstrap

Bootstrap CSS and JS are loaded from the jsDelivr CDN by default. For
offline use, serve local files:

```python
from mikiui import MikiApp

app = MikiApp()

app.add_head_link("/static/bootstrap.min.css", rel="stylesheet")
app.add_head_script("/static/bootstrap.bundle.min.js")
app.set_theme("bootstrap")
```

## Custom Themes

### Custom Color Theme

Create a CSS file with `--miki-*` variables:

```css
/* static/my-theme.css */
:root {
  --miki-bg: #f8fafc;
  --miki-fg: #1e293b;
  --miki-accent: #dc2626;
  --miki-border: #e2e8f0;
}
```

Register and use it:

```python
from mikiui import MikiApp, Theme

app = MikiApp()

my_theme = Theme(
    name="my-theme",
    source="custom",
    css_path="/static/my-theme.css",
)
app.register_theme(my_theme)
app.set_theme("my-theme")
```

### Custom Framework Theme

Combine a framework with a custom color theme:

```python
from mikiui import MikiApp, Theme

app = MikiApp()

tailwind_theme = Theme(
    name="my-tailwind",
    framework="tailwind",
    cdn_url="https://cdn.jsdelivr.net/npm/tailwindcss@3/dist/tailwind.min.css",
    variables={
        "--miki-accent": "#dc2626",
    },
)
app.register_theme(tailwind_theme)
app.set_theme("my-tailwind")
```

## Plugin Themes

Plugins can provide themes:

```python
from mikiui.app import Plugin, Theme
from mikiui.themes import register_theme

class MyThemePlugin(Plugin):
    def register(self, app):
        theme = Theme(
            name="plugin-theme",
            source="plugin",
            framework="tailwind",
            css_path="/_miki/runtime/plugin-theme.css",
        )
        register_theme(theme)

app = MikiApp()
app.use(MyThemePlugin())
app.set_theme("plugin-theme")
```

## Theme Functions

```python
from mikiui.themes import list_themes, get_theme, register_theme

# List all registered themes
list_themes()  # ['light', 'dark', 'dracula', 'solarized-dark', 'tailwind', 'bootstrap']

# Get a theme object
theme = get_theme("dark")

# Register a custom theme
register_theme(Theme(name="my-theme", ...))
```

## Runtime CSS Injection

During development, MikiUI injects the correct CSS links into every page:

- **Tailwind dev:** CDN link (instant, no build required)
- **Tailwind prod:** local compiled CSS from `_miki/runtime/themes/tailwind.css`
- **Bootstrap dev:** CDN links for CSS + JS
- **Bootstrap prod:** CDN links (or local paths if configured)
- **Plain CSS:** user-provided `<link>` tags

## MikiApp Theme API

```python
from mikiui import MikiApp

app = MikiApp()

# Set active theme
app.set_theme("dark")

# Get current theme name
print(app.theme)  # "dark"

# Get theme configuration
config = app.theme_config()
# {"name": "dark", "framework": None, "variables": {...}, ...}

# Add extra head links
app.add_head_link("/static/custom.css", rel="stylesheet")

# Add extra head scripts
app.add_head_script("/static/custom.js")

# Add meta tags
app.set_head_meta("description", "My MikiUI app")
```

## Framework Selection Reference

| CLI command | Framework | Node.js required |
|-------------|-----------|-----------------|
| `mikiui new myapp` (choose 1) | Tailwind | Yes |
| `mikiui new myapp --framework tailwind` | Tailwind | Yes |
| `mikiui new myapp --framework daisyui` | Tailwind + DaisyUI | Yes |
| `mikiui new myapp --framework bootstrap` | Bootstrap | No |
| `mikiui new myapp --framework plain` | Plain CSS | No |
