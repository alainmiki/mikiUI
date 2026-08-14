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

## What's Available

- **Components** — all HTML elements as Python classes (Button, Input, Form, Table, Dialog, Tabs, etc.)
- **Widgets** — high-level composite UI (DataGrid, MediaPlayer, DockablePanel, IDE Editor, etc.)
- **Themes** — 4 built-in themes (light, dark, solarized-dark, dracula) with custom theme support
- **Styling** — default `miki-*` classes + Tailwind CSS + DaisyUI integration
- **Plugins** — extend with custom themes, components, and widgets
- **Desktop** — native pywebview window or system browser fallback
- **Full-stack** — FastAPI backend with HTMX + Alpine.js runtime

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

## Commands

| Command | Description |
|---------|-------------|
| `mikiui new <name>` | Scaffold a new project |
| `mikiui dev` | Development server (auto-discovers `app.py`) |
| `mikiui desktop` | Native desktop window (pywebview) |
| `mikiui desktop --reload` | Desktop with auto-reload |
| `mikiui desktop --browser` | Force system browser |
| `mikiui build --target web` | Static web build |
| `mikiui build --target desktop` | Desktop package build |

## Documentation

- [Theming Guide](docs/themes.md)
- [App Discovery & Running](docs/app-discovery.md)
- [Plugin System](docs/plugins.md)
- [Component Styling](docs/styling.md)
- [Full Spec](context/plan.md)

## License

MIT
