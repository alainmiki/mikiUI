# MikiUI

**Build beautiful web and desktop apps — entirely in Python.**

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

## Quick Links

| Get Started | Resources |
|-------------|-----------|
| [Installation](guide/installation.md) | [Changelog](changelog.md) |
| [Quick Start](guide/quick-start.md) | [Contributing](contributing.md) |
| [Getting Started Guide](guide/getting-started.md) | [GitHub](https://github.com/alainmiki/mikiUI) |

## Installation

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

## Your First App

```python
from mikiui import MikiApp, Div, H1, P, Button

app = MikiApp(title="Hello MikiUI")

@app.route("/")
def home():
    return Div(
        H1("Hello, MikiUI!"),
        P("A Python-first UI framework."),
        Button("Click me", class_="miki-btn-primary"),
        class_="flex flex-col items-center justify-center h-screen gap-4",
    )

if __name__ == "__main__":
    app.run()
```

Run it:

```bash
python app.py
```

Open `http://127.0.0.1:8000` in your browser.
