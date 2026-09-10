# Themes

MikiUI includes a powerful theming system that controls colors, surfaces, and accents across all components and widgets.

## Quick Start

```python
from mikiui import MikiApp

app = MikiApp(title="My App")
app.set_theme("dark")
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

## Theme Variables

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

## Custom Themes

Create a custom theme by subclassing `Theme`:

```python
from mikiui.themes import Theme

class MyTheme(Theme):
    name = "my-theme"
    variables = {
        "--miki-bg": "#ffffff",
        "--miki-fg": "#1e2937",
        "--miki-accent": "#8b5cf6",
        # ... more variables
    }
```

Register it with your app:

```python
app.register_theme(MyTheme)
app.set_theme("my-theme")
```

## Theme Switching at Runtime

```python
@app.route("/theme/{theme_name}")
def change_theme(ctx, theme_name: str):
    ctx.app.set_theme(theme_name)
    return Div(f"Theme changed to {theme_name}")
```

## DaisyUI Integration

When using Tailwind + DaisyUI, MikiUI themes are automatically bridged to DaisyUI palettes:

```python
app.set_style_framework("tailwind", mode="cdn", daisyui=True)
app.set_theme("dark")  # Uses mikiui-dark DaisyUI theme
```

## See Also

- [Styling Guide](../guide/styling.md) — framework selection and CSS setup
- [Components Guide](../guide/components.md) — component styling
- [API Reference](../guide/api-reference.md) — theme API
