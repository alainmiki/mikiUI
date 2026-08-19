# Getting Started with MikiUI

MikiUI is a Python-first UI framework that lets you build user interfaces as
standalone desktop apps or websites. It uses FastAPI for the backend, HTMX +
Alpine.js for the frontend runtime, and a Python component API that maps
directly to HTML elements.

## When to Use MikiUI

- You want to build UIs **in Python** without touching JavaScript for logic.
- You need **both web and desktop** deployment from the same codebase.
- You prefer **server-side rendering** with optimistic client-side updates.
- You want a **beginner-friendly API** that is still powerful enough for
  advanced use cases (plugins, custom components, widgets).

## Prerequisites

- **Python 3.14 or later**
- **pip** (included with Python)
- **Node.js 18+** (only if you choose Tailwind CSS)

## Installation

Install MikiUI from the project root in editable mode:

```bash
cd C:\Users\Coder Miki\Desktop\mikiUI
pip install -e .
```

For development dependencies (testing, linting, type-checking):

```bash
pip install -e .[dev]
```

Verify the installation:

```bash
mikiui --help
```

You should see the MikiUI banner with available commands.

## Your First App in 5 Minutes

Create a file named `app.py`:

```python
from mikiui import MikiApp, Div, H1, P, Button

app = MikiApp(title="Hello MikiUI")

@app.route("/")
def home():
    return Div(
        H1("Hello, MikiUI!"),
        P("A Python-first UI framework."),
        Button("Click me", class_="miki-btn-primary", onclick="alert('Hello!')"),
        class_="flex flex-col items-center justify-center h-screen gap-4",
    )

if __name__ == "__main__":
    app.run()
```

Run it:

```bash
python app.py
```

Open `http://127.0.0.1:8000` in your browser. You should see a centered heading,
paragraph, and button.

## CLI Quick Reference

MikiUI ships with a CLI for scaffolding, development, and building:

| Command | Purpose |
|---------|---------|
| `mikiui new myapp` | Scaffold a new project |
| `mikiui dev` | Start the dev server (hot-reload) |
| `mikiui desktop` | Open a native desktop window |
| `mikiui build --target web` | Build for web production |
| `mikiui build --target desktop` | Build for desktop distribution |
| `mikiui tailwind dev` | Watch and rebuild Tailwind CSS |
| `mikiui install tailwind` | Install Tailwind + config files |

## Project Structure

A typical MikiUI project looks like this:

```
myapp/
  app.py               # Your MikiUI application (routes + components)
  requirements.txt     # Python dependencies
  static/              # Custom CSS, images, fonts
  .mikiui.json         # Project configuration
  tailwind.config.js   # Tailwind config (if using Tailwind)
  postcss.config.js    # PostCSS config (if using Tailwind)
  package.json         # Node.js dependencies (if using Tailwind)
```

For **Bootstrap** or **plain CSS** projects, the Tailwind files are omitted.

### Framework Choice

When you run `mikiui new`, you choose a CSS framework:

| Framework | Description | Requires Node.js |
|-----------|-------------|-----------------|
| `tailwind` | Tailwind CSS utility classes | Yes |
| `bootstrap` | Bootstrap 5 components | No |
| `plain` | Custom CSS only | No |

## Running in Dev Mode

```bash
mikiui dev
```

This starts a FastAPI + uvicorn server with hot-reloading at
`http://127.0.0.1:8000`. Any change to `app.py` triggers a reload.

### Tailwind Projects

If you selected Tailwind, run the CSS watcher in a second terminal:

```bash
# Terminal 1
mikiui dev

# Terminal 2
mikiui tailwind dev
```

The watcher scans your Python files for Tailwind classes and rebuilds CSS
automatically. In dev mode without the watcher, MikiUI falls back to the
Tailwind CDN so styles load immediately.

## Running in Desktop Mode

```bash
mikiui desktop
```

This launches a native window using **pywebview** (if installed). If pywebview
is unavailable, it falls back to your system browser.

Useful flags:

```bash
mikiui desktop --reload      # Auto-refresh on file changes
mikiui desktop --browser     # Force browser fallback
mikiui desktop --width 1280 --height 800  # Window size
```

## Next Steps

- **Components**: Read [Component Reference](components.md) for all HTML
  element mappings.
- **Widgets**: Browse [Widget Catalog](widgets.md) for high-level composite
  UI patterns.
- **Styling**: See [Styling Guide](styling.md) for Tailwind, Bootstrap, and
  theme customization.
- **Plugins**: Learn about the plugin system in [Plugins Guide](plugins.md),
  including the security model (manifest validation, AST vetting, import
  allow-list) and the marketplace client.
- **Security**: Read [Security Guide](security.md) for plugin security
  configuration and the [Plugin Security](#plugin-security) section below.
- **API**: Consult [API Reference](api-reference.md) for full method signatures.
- **Deployment**: Read [Deployment Guide](deployment.md) for production setups.

## Plugin Security

MikiUI validates every plugin before it is loaded or registered. By default,
plugins from local directories or the marketplace are blocked unless you
explicitly trust them.

### Quick configuration

```python
from mikiui import MikiApp
from mikiui.app import PluginSecurityConfig

app = MikiApp(title="My App")

# Default: only builtin and entry-point plugins are allowed.
# To allow local/marketplace plugins:
app.set_plugin_security_config(
    PluginSecurityConfig(
        allow_untrusted=True,
        vet_ast=True,
        blocked_capabilities=["filesystem:write"],
    )
)
```

### What gets checked

1. **Manifest identity** — plugin name matches its manifest
2. **Capabilities** — declared capabilities are not globally blocked
3. **AST vetting** — source code is scanned for dangerous patterns
   (`subprocess`, `eval`, `os.system`, etc.)
4. **Import allow-list** — only safe modules may be imported

Plugins that fail any check raise `PluginSecurityViolation` and are **not
registered**.

### Marketplace install

```python
from mikiui.app import (
    DirectoryIndexSource,
    PluginMarketplace,
    PluginSecurityConfig,
)

source = DirectoryIndexSource("mikiui_plugins")
market = PluginMarketplace(source)

app = MikiApp(title="My App")
app.set_plugin_security_config(PluginSecurityConfig(allow_untrusted=True))

plugin = market.install("chart-widget", app)
```

See [Plugins Guide](plugins.md) and [Security Guide](security.md) for full
details.
