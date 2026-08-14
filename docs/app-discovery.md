# MikiUI App Discovery & Running

## Auto-Discovery

When you run `mikiui dev` or `mikiui desktop` **without** `--app`, MikiUI
automatically finds your app by searching the current directory for a file
named `app.py`, `main.py`, or `server.py` that contains a `MikiApp` instance.

The search order is:
1. `app.py` — the recommended convention.
2. `main.py` — a common alternative.
3. `server.py` — another common name.
4. Any `*.py` file in the current directory root.

If no `MikiApp` is found, MikiUI falls back to the demo app.

## Explicit App Specification

You can always specify the app explicitly:

```bash
mikiui dev --app myapp:app
mikiui desktop --app myapp:app
```

The format is `module.path:attribute_name`. If the attribute is omitted,
MikiUI defaults to `app`.

## `app.run()` — The Simple Way

For the most beginner-friendly experience, add this to the bottom of your
`app.py`:

```python
if __name__ == "__main__":
    app.run()
```

Then just run:

```bash
python app.py
```

For desktop mode:

```python
if __name__ == "__main__":
    app.run(desktop=True)      # Native pywebview window
    # or
    app.run(desktop=True, reload=True)  # With auto-reload
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `mikiui dev` | Start the development server (FastAPI + uvicorn) with auto-reload. |
| `mikiui dev --no-reload` | Start without auto-reload (passes ASGI app directly). |
| `mikiui desktop` | Launch a native pywebview window (or system browser fallback). |
| `mikiui desktop --reload` | Desktop mode with auto-reload on file changes. |
| `mikiui desktop --browser` | Force the system browser instead of pywebview. |
| `mikiui build --target web` | Build a static web export. |
| `mikiui build --target desktop` | Package for desktop distribution (PyInstaller spec included). |
| `mikiui new myapp` | Scaffold a new project. |

## Desktop Mode

`mikiui desktop` defaults to a **native pywebview window** (no browser chrome)
if `pywebview` is installed. If it's not installed, it falls back to opening
the system browser.

Use `--browser` to force the browser fallback even if pywebview is installed.
