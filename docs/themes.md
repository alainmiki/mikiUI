# MikiUI Theming Guide

MikiUI ships with **four built-in themes** and a flexible system for creating custom ones. This guide covers theme switching, custom themes, and integration with Tailwind/Bootstrap.

## Built-in Themes

| Name | Description |
|------|-------------|
| `light` | Clean light theme (default) |
| `dark` | Modern dark theme with vibrant accents |
| `solarized-dark` | Muted, low-contrast warm dark |
| `dracula` | Vibrant purple/cyan/pink palette |

## Setting a Theme

```python
from mikiui import MikiApp, Div, Button

app = MikiApp(title="My App")
app.set_theme("dark")  # or "light", "dracula", "solarized-dark"

@app.route("/")
def home():
    return Div(Button("Hello!"))
```

## How Themes Work

Each theme is a CSS file in `mikiui/runtime/themes/` that sets CSS custom properties (`--miki-bg`, `--miki-fg`, `--miki-accent`, etc.). The base `miki.css` consumes these variables, so switching themes is a one-line change.

The active theme's CSS is **inlined** into the `<head>` of every page via `<style id="miki-theme">`, and the `<body>` gets a `data-miki-theme` attribute:

```html
<body data-miki-theme="dark">
```

## Framework Themes (Tailwind/Bootstrap)

In addition to color themes, MikiUI supports **framework themes** that change the CSS processing method:

| Name | Framework | CDN URL | Local Path |
|------|-----------|---------|------------|
| `tailwind` | Tailwind CSS | CDN available | Serve your own |
| `bootstrap` | Bootstrap 5 | CDN available | Serve your own |

### Using a Framework Theme in Development

```python
from mikiui import MikiApp, Theme

app = MikiApp(title="Bootstrap App")

# Method 1: Use built-in CDN
app.set_theme("bootstrap")  # Loads Bootstrap from CDN

# Method 2: Use local files
local_bootstrap = Theme(
    name="bootstrap-local",
    framework="bootstrap",
    css_path="/_miki/runtime/bootstrap.min.css",
    js_url="/_miki/runtime/bootstrap.bundle.min.js",
)
app.register_theme(local_bootstrap)
app.set_theme("bootstrap-local")
```

### Using a Framework Theme in Production

```bash
# Build with Tailwind
mikiui build --theme tailwind --daisyui

# Build with Bootstrap (CDN loaded, offline miki.css copied)
mikiui build --theme bootstrap
```

## Custom Themes

### Creating a Custom Color Theme

Create a CSS file with `--miki-*` custom properties:

```css
/* mikiui/runtime/themes/my-theme.css */
:root {
  --miki-primary: #2563eb;
  --miki-bg: #f8fafc;
  --miki-fg: #1e293b;
}
```

Register it:

```python
from mikiui import MikiApp, Theme

app = MikiApp(title="Custom Theme")

my_theme = Theme(
    name="my-theme",
    source="custom",
    css_path="/_miki/runtime/themes/my-theme.css",
)
app.register_theme(my_theme)
app.set_theme("my-theme")
```

### Creating a Framework Theme

```python
from mikiui import MikiApp, Theme

app = MikiApp(title="My App")

tailwind_theme = Theme(
    name="my-tailwind",
    framework="tailwind",
    cdn_url="https://unpkg.com/tailwindcss@3/dist/tailwind.min.css",
    tailwind_config={
        "extend": {
            "colors": {
                "brand": "#2563eb",
            }
        }
    },
)
app.register_theme(tailwind_theme)
app.set_theme("my-tailwind")
```

### Using Local CSS Files

Place files in `mikiui/runtime/` to serve them automatically:

```
mikiui/
└── runtime/
    ├── bootstrap.min.css
    ├── tailwind.css       # Your compiled Tailwind
    └── themes/
        └── my-theme.css   # Your custom color theme
```

## Plugin-Based Themes

Themes can be provided by plugins:

```python
from mikiui.app import Plugin, Theme
from mikiui.themes import register_theme

class MyThemePlugin(Plugin):
    def register(self, app):
        theme = Theme(
            name="plugin-theme",
            source="plugin",
            css_path="/_miki/runtime/plugin-theme.css",
        )
        register_theme(theme)

# Use it
app = MikiApp()
app.use(MyThemePlugin())
app.set_theme("plugin-theme")
```

## Switching Between Framework and Color Themes

You can combine a framework theme with a color theme:

```python
from mikiui import MikiApp, Theme

app = MikiApp()

# Tailwind framework + light color theme
hybrid = Theme(
    name="tailwind-light",
    framework="tailwind",
    cdn_url="https://unpkg.com/tailwindcss@3/dist/tailwind.min.css",
    css_path="/_miki/runtime/themes/light.css",  # Color theme
)
app.register_theme(hybrid)
app.set_theme("tailwind-light")
```

## Tailwind CSS + DaisyUI Integration

For detailed information on Tailwind and DaisyUI integration, see [styling.md](styling.md).

Quick example:

```python
from mikiui.build.tailwind import tailwind_config, write_tailwind_config

# Generate tailwind.config.js with MikiUI + DaisyUI
write_tailwind_config(
    "tailwind.config.js",
    theme="dark",
    daisyui=True,
)

# Then build
# mikiui build --theme tailwind --daisyui
```

DaisyUI themes are automatically bridged: MikiUI themes become `mikiui-{name}` in DaisyUI.

```html
<div data-theme="mikiui-dark">
  <!-- DaisyUI components -->
  <button class="btn">DaisyUI Button</button>
</div>
```

## List Available Themes

```python
from mikiui.themes import list_themes
print(list_themes())
# ['light', 'dark', 'dracula', 'solarized-dark', 'tailwind', 'bootstrap']
```

## More Information

For comprehensive styling guidance including Tailwind class usage, Bootstrap integration, and custom CSS, see [styling.md](styling.md).