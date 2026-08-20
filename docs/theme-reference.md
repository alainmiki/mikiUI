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
    cdn_url="https://cdn.jsdelivr.net/npm/tailwindcss@4/dist/tailwind.min.css",
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
list_themes()  # ['light', 'dark', 'dracula', 'solarized-dark', ...]

# Get a theme object
theme = get_theme("dark")

# Register a custom theme
register_theme(Theme(name="my-theme", ...))
```

## Runtime CSS Injection

During development, MikiUI injects the correct CSS links into every page:

- **Plain CSS:** `miki.css` + color theme CSS
- **Tailwind CDN:** Tailwind CSS from jsDelivr CDN
- **Tailwind local:** `/_miki/runtime/themes/tailwind.css`
- **DaisyUI:** DaisyUI CSS from jsDelivr CDN

## MikiApp Theme API

```python
from mikiui import MikiApp

app = MikiApp()

# Set active color theme
app.set_theme("dark")

# Set CSS framework
app.set_style_framework("tailwind", mode="cdn", daisyui=True)

# Get current theme name
print(app.theme)  # "dark"

# Get current framework
print(app.style_framework)  # "tailwind"

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
| `mikiui new myapp --framework plain` | Plain CSS | No |
