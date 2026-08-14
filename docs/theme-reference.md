# Theme System Quick Reference

## Quick Start

```python
from mikiui import MikiApp

app = MikiApp(title="My App")
app.set_theme("dark")  # Options: light, dark, dracula, solarized-dark, tailwind, bootstrap
```

## Available Themes

| Theme | Type | Description |
|-------|------|-------------|
| `light` | Color | Default light theme |
| `dark` | Color | Dark theme |
| `dracula` | Color | Purple/cyan accent palette |
| `solarized-dark` | Color | Warm muted palette |
| `tailwind` | Framework | Tailwind CSS from CDN |
| `bootstrap` | Framework | Bootstrap 5 from CDN |

## Custom Theme

```python
from mikiui import MikiApp, Theme

app = MikiApp()

my_theme = Theme(
    name="my-theme",
    framework="tailwind",  # or "bootstrap" or None
    cdn_url="https://cdn.example.com/tailwind.css",  # Optional CDN
    css_path="/_miki/runtime/local.css",  # Optional local file
    variables={"--miki-primary": "#0066cc"},  # CSS variable overrides
    extra_classes=["data-theme-dark"],  # Body classes
)

app.register_theme(my_theme)
app.set_theme("my-theme")
```

## Switching Themes

```python
# At any time
app.set_theme("dark")

# Or get current theme name
print(app.theme)  # "dark"

# Get theme configuration
config = app.theme_config()
# Returns: {"name": "dark", "framework": None, "variables": {...}, ...}
```

## Using with Plugins

```python
from mikiui.app import ThemePlugin, Theme

class MyCustomTheme(ThemePlugin):
    def theme(self):
        return Theme(
            name="my-theme",
            framework="tailwind",
            cdn_url="https://cdn.example.com/tailwind.css",
        )

app.use(MyCustomTheme())
```

## Framework-specific Usage

### Tailwind

```python
# CDN (dev)
app.set_theme("tailwind")

# Local file (dev)
tailwind = Theme(
    name="my-tailwind",
    framework="tailwind",
    css_path="/_miki/runtime/tailwind.css",
)
app.register_theme(tailwind)

# Build (prod)
# mikiui build --theme tailwind --daisyui
```

### Bootstrap

```python
# CDN (dev)
app.set_theme("bootstrap")

# Local files (dev)
bootstrap = Theme(
    name="my-bootstrap",
    framework="bootstrap",
    css_path="/_miki/runtime/bootstrap.min.css",
    js_url="/_miki/runtime/bootstrap.bundle.min.js",
)
app.register_theme(bootstrap)
```

### Static Files

Place CSS files in `mikiui/runtime/` to serve them automatically at `/_miki/runtime/`.

```
mikiui/
└── runtime/
    ├── bootstrap.min.css    # Served at /_miki/runtime/bootstrap.min.css
    └── my-theme.css         # Served at /_miki/runtime/my-theme.css
```

## CLI Commands

```bash
# Build with Tailwind
mikiui build --theme tailwind

# Build with Tailwind + DaisyUI
mikiui build --theme tailwind --daisyui

# Build with default CSS
mikiui build

# Build for desktop
mikiui build --target desktop
```

## Available Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `--miki-primary` | `#3b82f6` | Primary color |
| `--miki-secondary` | `#64748b` | Secondary color |
| `--miki-bg` | `#ffffff` | Background |
| `--miki-fg` | `#1e293b` | Text color |
| `--miki-radius` | `0.375rem` | Border radius |