# MikiUI

A Python-first UI framework that renders UIs as standalone desktops or websites.

## Quick Start

```bash
pip install -e .
mikiui new myapp
cd myapp
mikiui dev           # development server
# or
mikiui desktop        # native desktop window
```

## Styling

MikiUI supports two styling frameworks. Choose one during project creation:

```bash
mikiui new myapp
# Follow the prompts to choose Tailwind or plain CSS
```

| Framework | Description | Node.js Required |
|-----------|-------------|-----------------|
| `tailwind` | Tailwind CSS + optional DaisyUI | Yes |
| `plain` | Plain CSS, no framework | No |

### Tailwind CSS

```bash
cd myapp
npm install          # Install Node.js dependencies
mikiui dev           # Start dev server
mikiui tailwind dev  # Watch & rebuild CSS (second terminal)
```

Production build:

```bash
mikiui build --target web --theme tailwind
```

Add DaisyUI:

```bash
mikiui install tailwind daisyui
```

### Plain CSS

```bash
cd myapp
mikiui dev           # No extra setup needed
```

## What's Available

- **Components** — all HTML elements as Python classes (Button, Input, Form, Table, Dialog, Tabs, etc.)
- **Widgets** — high-level composite UI (DataGrid, MediaPlayer, DockablePanel, IDE Editor, ThemeSwitcher, etc.)
- **Themes** — 4 built-in themes (light, dark, solarized-dark, dracula) with custom theme support
- **Styling** — Tailwind CSS or plain CSS
- **Plugins** — extend with custom themes, components, and widgets
- **Desktop** — native pywebview window or system browser fallback
- **Full-stack** — FastAPI backend with HTMX + Alpine.js runtime

## Commands

| Command | Description |
|---------|-------------|
| `mikiui new <name>` | Scaffold a new project (prompts for framework) |
| `mikiui dev` | Development server (auto-discovers `app.py`) |
| `mikiui desktop` | Native desktop window (pywebview) |
| `mikiui desktop --reload` | Desktop with auto-reload |
| `mikiui desktop --browser` | Force system browser |
| `mikiui build --target web` | Static web build |
| `mikiui build --target desktop` | Desktop package build |
| `mikiui tailwind dev` | Watch and rebuild Tailwind CSS |
| `mikiui tailwind build` | Production Tailwind build |
| `mikiui install tailwind` | Install Tailwind + npm deps |

## Running Your App

```python
# app.py
from mikiui import MikiApp, Div, H1, Button

app = MikiApp(title="My App")
app.set_theme("dark")

@app.route("/", title="Home")
def home():
    return Div(H1("Welcome to MikiUI!"), Button("Click me"))

if __name__ == "__main__":
    app.run()       # python app.py
    # or: app.run(desktop=True)  for native window
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Styling Guide](docs/styling.md)
- [Theme Reference](docs/theme-reference.md)
- [Theming Guide](docs/themes.md)
- [App Discovery & Running](docs/app-discovery.md)
- [Plugin System](docs/plugins.md)
- [Full Spec](context/plan.md)

## License

MIT
