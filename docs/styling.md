# MikiUI Styling Guide

This guide covers how to style MikiUI applications using the default CSS, Tailwind CSS, Bootstrap, or custom CSS files. It explains the differences between development and production modes, and how to use local CSS assets.

## Overview

MikiUI uses a layered theming approach:

1. **Base Layer**: `miki.css` - Always loaded, provides CSS custom properties (`--miki-*`) for colors, spacing, and component styles.
2. **Framework Layer** (optional): Tailwind CSS, Bootstrap, or plain CSS framework.
3. **Theme Layer** (optional): Color themes (light, dark, dracula, solarized-dark) that set CSS variable values.

All layers work together. The framework CSS provides the styling system (utility classes, components), while the color theme provides the actual color palette.

---

## Default Styling (Recommended for Beginners)

By default, MikiUI uses its own `miki.css` which:

- Works completely offline (no internet required)
- Uses CSS custom properties for easy theming
- Provides sensible default styles for all components
- Includes all `miki-*` prefixed component classes

### Getting Started

```python
from mikiui import MikiApp, Div, Button

app = MikiApp(title="My App")

@app.route("/")
def home():
    return Div(
        Button("Click me"),
        style={"padding": "1rem", "color": "red"}  # Optional styling
    )
```

### Default Themes

MikiUI ships with four built-in color themes:

| Name | Description |
|------|-------------|
| `light` | Clean light theme (default) |
| `dark` | Modern dark theme |
| `solarized-dark` | Muted, low-contrast warm dark |
| `dracula` | Vibrant purple/cyan/pink palette |

```python
app.set_theme("dark")  # or "light", "dracula", "solarized-dark"
```

---

## Tailwind CSS Integration

### Development Mode

There are two approaches for Tailwind in development:

#### Option A: CDN (Quick Prototyping)

```python
from mikiui import MikiApp, Theme

app = MikiApp(title="Tailwind App")

# Use built-in Tailwind theme (loads from CDN)
app.use_theme("tailwind")

@app.route("/")
def home():
    return Div("Hello Tailwind!", class_="flex items-center justify-center h-screen bg-gray-100")
```

#### Option B: Local CSS File

1. Place your Tailwind CSS file in `mikiui/runtime/`:
   ```
   mikiui/
   └── runtime/
       └── custom-tailwind.css   # Your compiled Tailwind output
   ```

2. Configure a custom theme:
   ```python
   from mikiui import MikiApp, Theme

   app = MikiApp(title="My App")

   custom_tailwind = Theme(
       name="custom-tailwind",
       framework="tailwind",
       css_path="/_miki/runtime/custom-tailwind.css",  # Served from runtime dir
   )
   app.register_theme(custom_tailwind)
   app.set_theme("custom-tailwind")
   ```

### Production Mode (Tailwind JIT Build)

For production, run the Tailwind JIT build:

```bash
# Build with Tailwind CSS output
mikiui build --target web --theme tailwind --daisyui

# Or with your own config
mikiui build --target web --theme tailwind --out dist_myproject
```

**What this does:**

1. Scans your app's components andwidgets for `miki-*` class usage
2. MergeS your app's imports with MikiUI's Tailwind config
3. Generates an optimized `dist/_miki/runtime/mikiui.css` with only used classes

**Prerequisites for Tailwind Build:**

```bash
# Install Tailwind CLI (or as a dev dependency in your project)
npm install -D tailwindcss @tailwindcss/forms

# Or use the Tailwind CLI directly
npm install -g tailwindcss
```

### Using Tailwind Classes

Add Tailwind utility classes via the `class_` parameter:

```python
from mikiui import MikiApp, Div, Button, Flex, Grid

app = MikiApp()

@app.route("/")
def home():
    return Div(
        Flex(
            Div("Sidebar", class_="w-64 bg-gray-200 p-4"),
            Div(
                Button("Primary", class_="bg-blue-500 hover:bg-blue-700 text-white"),
                Grid([
                    Button("A"),
                    Button("B"),
                    Button("C"),
                ], class_="grid grid-cols-3 gap-4"),
                class_="flex-1 bg-white p-4",
            ),
            class_="flex h-screen",
        ),
        class_="min-h-screen bg-gray-100",
    )
```

### DaisyUI Integration

DaisyUI provides ready-made component themes that work with Tailwind:

```python
from mikiui import MikiApp, Theme

app = MikiApp(title="DaisyUI App")

# DaisyUI themes (includes mikiui-light, mikiui-dark, etc.)
daisyui_theme = Theme(
    name="my-daisyui",
    framework="tailwind",
    cdn_url="https://unpkg.com/tailwindcss@3/dist/tailwind.min.css",
    extra_classes=["data-theme=mikiui-dark"],  # DaisyUI theme attribute
)
app.register_theme(daisyui_theme)
app.set_theme("my-daisyui")
```

Or build with DaisyUI for production:

```bash
mikiui build --theme tailwind --daisyui
```

---

## Bootstrap Integration

### Development Mode

#### Option A: CDN (Quick Prototyping)

```python
from mikiui import MikiApp, Theme

app = MikiApp(title="Bootstrap App")

bootstrap_theme = Theme(
    name="bootstrap-cdn",
    framework="bootstrap",
    cdn_url="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
    js_url="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
)
app.register_theme(bootstrap_theme)
app.set_theme("bootstrap-cdn")
```

#### Option B: Local Bootstrap

1. Download Bootstrap CSS and JS to `mikiui/runtime/`:
   ```
   mikiui/
   └── runtime/
       ├── bootstrap.min.css
       └── bootstrap.bundle.min.js
   ```

2. Configure:
   ```python
   from mikiui import MikiApp, Theme

   app = MikiApp(title="Local Bootstrap")

   local_bootstrap = Theme(
       name="bootstrap-local",
       framework="bootstrap",
       css_path="/_miki/runtime/bootstrap.min.css",
       js_url="/_miki/runtime/bootstrap.bundle.min.js",
   )
   app.register_theme(local_bootstrap)
   app.set_theme("bootstrap-local")
   ```

### Using Bootstrap Classes

Add Bootstrap classes via the `class_` parameter:

```python
from mikiui import MikiApp, Div, Button, Form, Input

app = MikiApp()

@app.route("/")
def home():
    return Div(
        Form(
            Div(
                Input(type="text", class_="form-control", placeholder="Username"),
                Input(type="password", class_="form-control", placeholder="Password"),
                class_="mb-3",
            ),
            Button("Login", class_="btn btn-primary", type="submit"),
            class_="container mt-5",
        ),
        class_="bg-light",
    )
```

---

## Custom CSS Themes

### Creating a Custom Theme

Create a CSS file with `--miki-*` custom properties:

```css
/* my-theme.css */
:root {
  --miki-primary: #2563eb;
  --miki-secondary: #64748b;
  --miki-bg: #f8fafc;
  --miki-fg: #1e293b;
  --miki-border: #e2e8f0;
  --miki-radius: 0.5rem;
}
```

### Registering a Custom Theme

```python
from mikiui import MikiApp, Theme

app = MikiApp(title="Custom Theme App")

my_theme = Theme(
    name="my-brand",
    source="custom",
    css_path="/_miki/runtime/my-theme.css",
    extra_classes=["dark:bg-[#1e293b]"],  # Tailwind dark mode support
    variables={"--miki-accent": "#dc2626"},  # Override specific variables
)
app.register_theme(my_theme)
app.set_theme("my-brand")
```

### Theme Variables Reference

These CSS custom properties control component appearance:

| Variable | Default | Description |
|----------|---------|-------------|
| `--miki-primary` | `#3b82f6` | Primary color |
| `--miki-secondary` | `#64748b` | Secondary color |
| `--miki-bg` | `#ffffff` | Background color |
| `--miki-fg` | `#1e293b` | Foreground/text color |
| `--miki-border` | `#e2e8f0` | Border color |
| `--miki-radius` | `0.375rem` | Border radius |
| `--miki-font` | `system-ui` | Font family |
| `--miki-size` | `1rem` | Base font size |

---

## Plugin-Based Themes

Themes can be provided by plugins, making it easy to distribute theme packages:

```python
from mikiui.app import Plugin, Theme
from mikiui.themes import register_theme

class MyThemePlugin(Plugin):
    """A plugin that provides a custom theme."""
    
    def register(self, app):
        theme = Theme(
            name="plugin-theme",
            source="plugin",
            css_path="/_miki/runtime/plugin-theme.css",
            extra_classes=["data-theme-plugin"],
        )
        app.register_theme(theme)
```

Users install your plugin and use it:

```bash
pip install my-theme-plugin
```

```python
from my_theme_plugin import MyThemePlugin

app = MikiApp()
app.use(MyThemePlugin())  # Theme is auto-registered and activated
app.set_theme("plugin-theme")  # Or just use app.theme directly
```

---

## Development Mode File Structure

To use local CSS in development mode, place files in the runtime directory:

```
mikiui/
└── runtime/
    ├── miki.css              # Base MikiUI styles (always loaded)
    ├── miki_ui.js            # Custom JS utilities
    ├── htmx.min.js           # HTMX library
    ├── alpine.min.js         # Alpine.js library
    ├── bootstrap.min.css     # ← Your local Bootstrap CSS
    ├── bootstrap.bundle.min.js  # ← Your local Bootstrap JS
    └── themes/
        ├── light.css
        ├── dark.css
        ├── dracula.css
        └── solarized-dark.css
```

These files are automatically served at `/_miki/runtime/` via StaticFiles.

---

## Production Mode

### Building for Web

```bash
# Default (offline, uses miki.css)
mikiui build --target web --mode fullstack

# With Tailwind (runs Tailwind JIT)
mikiui build --target web --mode fullstack --theme tailwind --daisyui

# Separate (front-end only)
mikiui build --target web --mode separate
```

### Building for Desktop

```bash
# Native window (pywebview)
mikiui desktop

# Browser fallback
mikiui desktop --browser

# With auto-reload (development)
mikiui desktop --reload

# Build for distribution
mikiui build --target desktop
```

---

## Advanced: Combining Frameworks and Color Themes

You can layer a framework (Tailwind/Bootstrap) with a color theme:

```python
from mikiui import MikiApp, Theme

app = MikiApp(title="Hybrid Theme")

# Tailwind framework + Dracula color theme
hybrid_theme = Theme(
    name="tail-dracula",
    framework="tailwind",
    cdn_url="https://unpkg.com/tailwindcss@3/dist/tailwind.min.css",
    css_path="/_miki/runtime/themes/dracula.css",  # Color theme
    variables={"--miki-primary": "#f472b6"},  # Customize colors
)
app.register_theme(hybrid_theme)
app.set_theme("tail-dracula")
```

---

## Troubleshooting

### Tailwind classes not working

1. Ensure Tailwind is configured: `mikiui build --theme tailwind`
2. Check that the class is actually used in your app (Tailwind JIT purges unused classes)
3. For development with CDN, test classes in the browser

### Bootstrap styles not applying

1. Verify `bootstrap.bundle.min.js` is loaded (for interactive components)
2. Check `data-bs-*` attributes for JavaScript components
3. Ensure Bootstrap CSS loads before `miki.css`

### Local CSS not loading

1. File must be in `mikiui/runtime/` directory
2. Use `/_miki/runtime/filename.css` in `css_path`
3. Verify the file is actually there

### Theme changes not visible

1. Clear browser cache (or use incognito mode)
2. Check the `<head>` for the new CSS link or inline styles
3. Verify `data-miki-theme` attribute on `<body>`