# Why MikiUI?

MikiUI combines the best of Python backend development with modern web UX patterns.

## Python-First

Write routes, components, and state in pure Python. The framework handles HTML, CSS, and JS interop automatically:

```python
from mikiui import MikiApp, Div, H1, P, Button

app = MikiApp(title="My App")

@app.route("/")
def home():
    return Div(
        H1("Welcome!"),
        P("Built with Python."),
        Button("Get Started", class_="miki-btn-primary"),
    )
```

## Multiple Targets

Deploy the same codebase as:

- A **website** served by FastAPI + uvicorn
- A **desktop app** via pywebview
- A **static site** via `mikiui build --target web --mode separate`

## Beginner-Friendly, Expert-Ready

- **Beginners**: Use the built-in components and themes without touching HTML/CSS/JS
- **Experts**: Access the full FastAPI stack, custom components, plugin system, and WebSocket integration

## Secure by Default

- CSRF protection enabled by default
- CSP nonces on every response
- Security headers (HSTS, X-Frame-Options, etc.)
- Plugin sandboxing with AST vetting

## Real-Time Built In

WebSocket with rooms/channels, SSE, and auth integration out of the box.
