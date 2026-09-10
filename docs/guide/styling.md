# Styling

MikiUI supports two styling modes: plain CSS and Tailwind CSS. You can switch between them without changing your app logic.

## Plain CSS (default)

Plain CSS loads `miki.css` (base widget styles) plus the active color theme CSS. No Node.js, no build step.

```python
from mikiui import MikiApp

app = MikiApp()
app.set_style_framework("plain")
app.set_theme("dark")
```

### Adding Custom CSS

```python
app.add_head_link("/static/styles.css", rel="stylesheet")
```

Place custom CSS in the `static/` directory, which is auto-mounted at `/static`.

## Tailwind CSS

Tailwind CSS provides utility classes for rapid UI development.

### Setup

```bash
mikiui install tailwind
npm install
```

This creates `tailwind.config.js` and `postcss.config.js` in your project.

### CDN vs Local JIT

| Mode | How it works | When to use |
|------|--------------|-------------|
| `cdn` | Loads Tailwind from jsDelivr CDN | Development, quick prototypes |
| `local` | Serves locally built CSS from `/_miki/runtime/themes/tailwind.css` | Production, offline, mobile |

### Configuration

```python
# Plain CSS (default)
app.set_style_framework("plain")

# Tailwind — CDN mode (instant, no build)
app.set_style_framework("tailwind", mode="cdn")

# Tailwind — local JIT mode (production)
app.set_style_framework("tailwind", mode="local")

# Tailwind + DaisyUI
app.set_style_framework("tailwind", mode="cdn", daisyui=True)
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

### Development Workflow

**Terminal 1 — Python dev server:**
```bash
mikiui dev
```

**Terminal 2 — Tailwind CSS watcher (local mode only):**
```bash
mikiui tailwind dev
```

In CDN mode, no watcher is needed — styles load from the CDN immediately.

### Production Build

```bash
mikiui build --target web --theme dark --framework tailwind
```

Or with DaisyUI:

```bash
mikiui build --target web --theme dark --framework tailwind --daisyui
```

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

## See Also

- [Themes Guide](../guide/themes.md) — color theme system
- [Deployment Guide](../guide/deployment.md) — production build options
- [CLI Reference](../guide/cli-reference.md) — Tailwind CLI commands
