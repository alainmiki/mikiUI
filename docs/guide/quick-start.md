# Quick Start

Create your first MikiUI app in under 5 minutes.

## Step 1: Create a new project

```bash
mikiui new myapp
cd myapp
```

## Step 2: Write your app

```python
from mikiui import MikiApp, Div, H1, P, Button

app = MikiApp(title="My App")

@app.route("/", title="Home")
def home():
    return Div(
        H1("Welcome to MikiUI!"),
        P("Build web and desktop apps in Python."),
        Button("Get Started", class_="miki-btn-primary"),
        class_="flex flex-col items-center justify-center h-screen gap-4",
    )

if __name__ == "__main__":
    app.run()           # web server
    # app.run(desktop=True)  # native window
```

## Step 3: Run it

```bash
mikiui dev            # development server with hot-reload
# or
python app.py         # direct execution
```

Open `http://127.0.0.1:8000` in your browser.

## What You Can Build

| Target | Command | Description |
|--------|---------|-------------|
| **Website** | `mikiui dev` | FastAPI + HTMX dev server |
| **Desktop App** | `mikiui desktop` | Native pywebview window |
| **Static Site** | `mikiui build --target web --mode separate` | Pre-rendered HTML for any host |
| **Fullstack App** | `mikiui build --target web --mode fullstack` | Static HTML + ASGI server script |
| **Desktop Package** | `mikiui build --target desktop` | PyInstaller-based native executable |
| **API Backend** | `create_app(app)` | FastAPI with OpenAPI docs |

## Next Steps

- **Components**: Read [Components Guide](../guide/components.md) for all HTML element mappings.
- **Widgets**: Browse [Widgets Guide](../guide/widgets.md) for high-level composite UI patterns.
- **Styling**: See [Styling Guide](../guide/styling.md) for Tailwind and theme customization.
- **Routing**: See [Routing Guide](../guide/routing.md) for route groups, params, and middleware.
- **Plugins**: Learn about the plugin system in [Plugins Guide](../guide/plugins.md).
- **Security**: Read [Security Guide](../guide/security.md) for CSRF, auth, headers, and plugin security.
- **Deployment**: Read [Deployment Guide](../guide/deployment.md) for production setups.
