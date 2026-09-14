<div align="center">

# MikiUI

**Build beautiful web and desktop apps — entirely in Python.**

[![PyPI version](https://img.shields.io/pypi/v/mikiui)](https://pypi.org/project/mikiui/)
[![Python](https://img.shields.io/pypi/pyversions/mikiui)](https://pypi.org/project/mikiui/)
[![License](https://img.shields.io/pypi/l/mikiui)](LICENSE)

[Installation](#installation) · [Quick Start](#quick-start) · [Documentation](#documentation) · [Examples](#examples)

</div>

---

MikiUI is a Python-first UI framework that lets you build **web applications and native desktop windows** from a single codebase. No JavaScript required for logic — just Python classes that map to HTML, with a modern component API, built-in security, and real-time capabilities.

> **Mobile (PWA)** support is planned for v1. The web output is already responsive and mobile-friendly; native mobile wrappers (Capacitor) and native bridges are on the v1 roadmap.

## Why MikiUI?

- **One codebase, multiple targets** — deploy as a website, a native desktop app (pywebview), or a static site
- **Python-first** — write routes, components, and state in pure Python; the framework handles HTML, CSS, and JS interop
- **60+ components and widgets** — from buttons and forms to data grids, IDE editors, chat UIs, and MDI workspaces
- **Real-time built in** — WebSocket with rooms/channels, SSE, and auth integration
- **Secure by default** — CSRF protection, security headers, CSP nonces, and plugin sandboxing
- **API-ready** — auto-generated OpenAPI docs, type-coerced path params, and route groups
- **Theming** — 4 built-in themes (light, dark, solarized, dracula) with custom theme support
- **Plugin ecosystem** — extend with custom components, widgets, themes, and backend routes

## Installation

### From PyPI (recommended)

```bash
pip install mikiui
```

### With Tailwind CSS support

```bash
pip install mikiui[tailwind]
npm install  # installs Tailwind + DaisyUI
```

### For desktop apps

```bash
pip install mikiui[desktop]
```

### Verify

```bash
mikiui --help
```

---

## Quick Start

### 1. Create a new project

```bash
mikiui new myapp
cd myapp
```

### 2. Write your app

```python
# app.py
from mikiui import MikiApp, Div, H1, P, Button

app = MikiApp(title="My App")

@app.route("/", title="Home")
def home():
    return Div(
        H1("Welcome to MikiUI!"),
        P("Build web and desktop apps in Python."),
        Button("Get Started", class_="miki-btn-primary"),
        class="flex flex-col items-center justify-center h-screen gap-4",
    )

if __name__ == "__main__":
    app.run()           # web server
    # app.run(desktop=True)  # native window
```

### 3. Run it

```bash
mikiui dev            # development server with hot-reload
# or
python app.py         # direct execution
```

Open `http://127.0.0.1:8000` in your browser.

---

## What You Can Build

| Target | Command | Description |
|--------|---------|-------------|
| **Website** | `mikiui dev` | FastAPI + HTMX dev server |
| **Desktop App** | `mikiui desktop` | Native pywebview window |
| **Static Site** | `mikiui build --target web --mode separate` | Pre-rendered HTML for any host |
| **Fullstack App** | `mikiui build --target web --mode fullstack` | Static HTML + ASGI server script |
| **Desktop Package** | `mikiui build --target desktop` | PyInstaller-based native executable |
| **API Backend** | `create_app(app)` | FastAPI with OpenAPI docs |

---

## Features

### Components & Widgets
All HTML elements as Python classes (`Button`, `Input`, `Form`, `Table`, `Dialog`, `Tabs`) plus high-level widgets (`DataGrid`, `MediaPlayer`, `DockablePanel`, `IDEEditor`, `ChatUI`, `KanbanBoard`, `Calendar`, `Carousel`, and more).

### Routing
Type-coerced path params, route groups, pattern-matched lookup, and per-route auth:

```python
@app.route("/users/{user_id:int}", summary="Get user", tags=["users"])
def get_user(ctx, user_id: int):
    return Div(f"User {user_id}")
```

### Real-Time
WebSocket with rooms, channels, and auth integration:

```python
manager = ConnectionManager()
manager.join_room(ws, "chat-room")
await manager.broadcast_to_room("chat-room", {"message": "Hello!"})
```

### Security
CSRF by default, security headers, CSP nonces, rate limiting, and plugin sandboxing.

### API Documentation
Auto-generated OpenAPI schema with Swagger UI and ReDoc at `/docs` and `/redoc`.

### Theming
4 built-in themes with custom theme support. Switch at runtime:

```python
app.set_theme("dark")
```

### Styling
Tailwind CSS (with optional DaisyUI) or plain CSS — switch without changing app logic.

---

## Commands

| Command | Description |
|---------|-------------|
| `mikiui new <name>` | Scaffold a new project |
| `mikiui dev` | Development server with hot-reload |
| `mikiui desktop` | Native desktop window |
| `mikiui build --target web` | Static web build (fullstack by default) |
| `mikiui build --target web --mode separate` | Static site only |
| `mikiui build --target desktop` | Desktop package (auto-installs PyInstaller) |
| `mikiui build --target desktop --onefile` | Single-file desktop executable |
| `mikiui tailwind dev` | Watch & rebuild Tailwind CSS |
| `mikiui install tailwind` | Install Tailwind + npm deps |

---

## Examples

### API with docs
```python
from mikiui import MikiApp
from mikiui.backend import create_app
from mikiui_app_plugins import APIPlugin, SessionPlugin

app = MikiApp(title="My API")
session = SessionPlugin(secret_key="change-me")
app.use(session)
app.use(APIPlugin(title="My API", version="1.0.0", session_plugin=session))

@app.get("/api/items", summary="List items", tags=["items"])
def list_items(ctx):
    return [{"id": 1, "name": "Widget"}]

@app.post("/api/items", summary="Create item", tags=["items"])
def create_item(ctx):
    return {"id": 2, "name": "New Item"}, 201

fastapi_app = create_app(app)
# OpenAPI docs at /docs, ReDoc at /redoc
```

### WebSocket chat with rooms
```python
from mikiui.backend.websocket import ConnectionManager, mount_websocket

manager = ConnectionManager(max_connections_per_user=5)

async def chat_handler(ws, manager):
    user_id = ws.state.mikiui_user_id
    manager.join_room(ws, "general")
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast_to_room("general", {"user": user_id, "text": data})
    except WebSocketDisconnect:
        manager.disconnect(ws)
```

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](https://alainmiki.github.io/mikiUI/guide/getting-started) | Installation, first app, CLI reference |
| [API Reference](https://alainmiki.github.io/mikiUI/guide/api-reference) | Full method signatures and examples |
| [Widget Catalog](https://alainmiki.github.io/mikiUI/guide/widgets) | All 60+ widgets with examples |
| [Router Guide](https://alainmiki.github.io/mikiUI/guide/routing) | Routing, groups, middleware |
| [Security Guide](https://alainmiki.github.io/mikiUI/guide/security) | CSRF, auth, headers, plugin security |
| [Styling Guide](https://alainmiki.github.io/mikiUI/guide/styling) | Tailwind, plain CSS, themes |
| [Plugin System](https://alainmiki.github.io/mikiUI/guide/plugins) | Creating and publishing plugins |
| [Deployment](https://alainmiki.github.io/mikiUI/guide/deployment) | Production setup, static export |
| [Themes](https://alainmiki.github.io/mikiUI/guide/themes) | Built-in and custom themes |
| [Changelog](https://alainmiki.github.io/mikiUI/changelog) | Version history |

---

## Development Setup (Contributors)

To set up the project for development:

```bash
git clone https://github.com/alainmiki/mikiUI.git
cd mikiUI
pip install -e ".[dev,build,desktop,tailwind]"
pip install pytest-playwright
playwright install --with-deps chromium
```

Run tests:

```bash
python -m pytest tests/ --ignore=tests/e2e    # unit + integration
python -m pytest tests/e2e/                    # browser e2e (needs Chromium)
```

Build and validate:

```bash
python -m build
mikiui build --target web
mikiui build --target desktop
```

---

## Roadmap

| Version | Focus |
|---------|-------|
| v1.0 | Mobile wrappers (Capacitor), PWA, native bridges |
| v2.0 | Plugin marketplace, database/Redis integration |

---

## Requirements

- **Python 3.14+**
- **Node.js 18+** (only for Tailwind CSS)
- **pywebview** (only for desktop mode, auto-installed with `[desktop]`)

## License

[MIT](LICENSE)
