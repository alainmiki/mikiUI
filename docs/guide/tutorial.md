# 16-Step Tutorial

This tutorial takes you from zero to a complete MikiUI application. Each step builds on the previous one, teaching you the framework by doing.

## What You'll Build

A simple task management app with:
- A home page listing tasks
- A page to add new tasks
- Theme switching
- Desktop and web deployment

## Prerequisites

- Python 3.14+
- pip
- Node.js 18+ (for Steps 12-13 only)

---

## Step 1: Install MikiUI

Install MikiUI from PyPI:

```bash
pip install mikiui
```

Verify the installation:

```bash
mikiui --help
```

You should see the MikiUI CLI help text.

## Step 2: Create Your Project

Create a new directory for your project:

```bash
mkdir taskapp
cd taskapp
```

Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

## Step 3: Create Your First App

Create `app.py`:

```python
from mikiui import MikiApp, Div, H1

app = MikiApp(title="TaskApp")

@app.route("/")
def home():
    return Div(
        H1("Welcome to TaskApp"),
        class_="container",
    )

if __name__ == "__main__":
    app.run()
```

Run it:

```bash
python app.py
```

Open `http://127.0.0.1:8000` in your browser. You should see "Welcome to TaskApp".

## Step 4: Add Components

Expand your home page with more components:

```python
from mikiui import MikiApp, Div, H1, P, Button

app = MikiApp(title="TaskApp")

@app.route("/")
def home():
    return Div(
        H1("Welcome to TaskApp"),
        P("A simple task manager built with MikiUI."),
        Button("Get Started", class_="miki-btn-primary"),
        class_="container",
    )

if __name__ == "__main__":
    app.run()
```

Key concepts:
- `Div` is a generic container (like `<div>`)
- `class_="miki-btn-primary"` adds CSS classes (use `class_` not `class` because `class` is a Python keyword)
- Components accept children as positional arguments

## Step 5: Add Styling with Plain CSS

Create `static/styles.css`:

```css
.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

.miki-btn-primary {
    background: #3b82f6;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
}

.miki-btn-primary:hover {
    background: #2563eb;
}
```

Tell MikiUI to load it:

```python
@app.route("/")
def home():
    app.add_head_link("/static/styles.css", rel="stylesheet")
    return Div(
        H1("Welcome to TaskApp"),
        P("A simple task manager built with MikiUI."),
        Button("Get Started", class_="miki-btn-primary"),
        class_="container",
    )
```

Or set it globally in `app.py` before defining routes:

```python
app = MikiApp(title="TaskApp")
app.add_head_link("/static/styles.css", rel="stylesheet")
```

## Step 6: Add a Theme

MikiUI includes built-in themes. Add the dark theme:

```python
app = MikiApp(title="TaskApp")
app.set_theme("dark")
```

Try other themes: `light`, `dracula`, `solarized-dark`.

## Step 7: Add a Second Route

Add a page to view tasks:

```python
tasks = ["Buy groceries", "Walk the dog", "Write code"]

@app.route("/")
def home():
    app.add_head_link("/static/styles.css", rel="stylesheet")
    return Div(
        H1("Welcome to TaskApp"),
        P("A simple task manager built with MikiUI."),
        Button("View Tasks", class_="miki-btn-primary", onclick="location.href='/tasks'"),
        class_="container",
    )

@app.route("/tasks")
def tasks_page():
    task_items = [Div(f"• {task}") for task in tasks]
    return Div(
        H1("My Tasks"),
        *task_items,
        Button("Add Task", class_="miki-btn-primary", onclick="location.href='/add'"),
        class_="container",
    )
```

## Step 8: Add Navigation

Create a reusable navigation bar:

```python
from mikiui import Div, Nav, A

def nav_bar(current_page: str) -> Div:
    links = [
        ("Home", "/"),
        ("Tasks", "/tasks"),
        ("Add", "/add"),
    ]
    nav_items = []
    for label, href in links:
        active = ' class_="active"' if href == current_page else ''
        nav_items.append(A(label, href=href, class_="nav-link" + active))
    return Nav(*nav_items, class_="navbar")
```

Use it in your routes:

```python
@app.route("/")
def home():
    app.add_head_link("/static/styles.css", rel="stylesheet")
    return Div(
        nav_bar("/"),
        H1("Welcome to TaskApp"),
        # ... rest of page
        class_="container",
    )
```

## Step 9: Add a Form

Create a page to add new tasks:

```python
from mikiui import Form, Input, Button, Label

@app.route("/add")
def add_task():
    return Div(
        nav_bar("/add"),
        H1("Add New Task"),
        Form(
            Label("Task name:", for_="task_name"),
            Input(type="text", id="task_name", name="task_name", placeholder="Enter task..."),
            Button("Add Task", type="submit", class_="miki-btn-primary"),
            action="/add",
            method="POST",
            class_="task-form",
        ),
        class_="container",
    )

@app.post("/add")
def add_task_post(ctx):
    from starlette.requests import Request
    form = await ctx.form()
    task_name = form.get("task_name", "").strip()
    if task_name:
        tasks.append(task_name)
    return Div(
        nav_bar("/add"),
        H1("Task Added!"),
        P(f"Added: {task_name}"),
        Button("Back to Tasks", class_="miki-btn-primary", onclick="location.href='/tasks'"),
        class_="container",
    )
```

## Step 10: Handle Form Data

Access form data using `await ctx.form()`:

```python
@app.post("/add")
async def add_task_post(ctx):
    form = await ctx.form()
    task_name = form.get("task_name", "").strip()
    if not task_name:
        return Div(
            nav_bar("/add"),
            H1("Error"),
            P("Task name cannot be empty."),
            Button("Try Again", class_="miki-btn-primary", onclick="location.href='/add'"),
            class_="container",
        )
    tasks.append(task_name)
    return Div(
        nav_bar("/add"),
        H1("Task Added!"),
        P(f"Added: {task_name}"),
        Button("Back to Tasks", class_="miki-btn-primary", onclick="location.href='/tasks'"),
        class_="container",
    )
```

Key concepts:
- Use `async def` for routes that need to read form data
- `ctx.form()` returns a dict-like object with form fields
- Always validate user input

## Step 11: Add Path Parameters

Add a route to mark tasks as complete:

```python
@app.route("/complete/{index:int}")
def complete_task(ctx, index: int):
    if 0 <= index < len(tasks):
        completed = tasks.pop(index)
        return Div(
            nav_bar("/tasks"),
            H1("Task Completed!"),
            P(f"Completed: {completed}"),
            Button("Back to Tasks", class_="miki-btn-primary", onclick="location.href='/tasks'"),
            class_="container",
        )
    return Div(
        nav_bar("/tasks"),
        H1("Error"),
        P("Task not found."),
        Button("Back to Tasks", class_="miki-btn-primary", onclick="location.href='/tasks'"),
        class_="container",
    )
```

Key concepts:
- `{index:int}` type-coerces the path parameter to `int`
- Path params are passed as keyword arguments to the handler
- Always validate indices and handle edge cases

## Step 12: Switch to Tailwind CSS

Install Tailwind:

```bash
mikiui install tailwind
npm install
```

Update `app.py` to use Tailwind:

```python
app = MikiApp(title="TaskApp")
app.set_theme("dark")
app.set_style_framework("tailwind", mode="cdn")
```

Start the Tailwind watcher in a second terminal:

```bash
mikiui tailwind dev
```

Replace custom CSS classes with Tailwind utilities:

```python
@app.route("/")
def home():
    return Div(
        nav_bar("/"),
        H1("Welcome to TaskApp"),
        P("A simple task manager built with MikiUI."),
        Button("View Tasks", class_="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"),
        class_="container mx-auto p-4",
    )
```

## Step 13: Add DaisyUI

Enable DaisyUI for pre-built components:

```python
app = MikiApp(title="TaskApp")
app.set_theme("dark")
app.set_style_framework("tailwind", mode="cdn", daisyui=True)
```

Update your UI to use DaisyUI classes:

```python
@app.route("/")
def home():
    return Div(
        nav_bar("/"),
        H1("Welcome to TaskApp"),
        P("A simple task manager built with MikiUI."),
        Button("View Tasks", class_="btn btn-primary"),
        class_="container mx-auto p-4",
    )
```

DaisyUI provides classes like:
- `btn btn-primary` — buttons
- `card` — card containers
- `input input-bordered` — form inputs
- `navbar` — navigation bars
- `alert` — alert messages

## Step 14: Build for Web

Create a production web build:

```bash
mikiui build --target web --mode fullstack --framework tailwind --daisyui
```

This creates a `dist/` directory with:
- Pre-rendered HTML for all routes
- Compiled Tailwind CSS
- Runtime assets (HTMX, Alpine.js)
- `sitemap.xml`, `robots.txt`, `404.html`
- `server.py` for standalone serving

Serve the build:

```bash
cd dist
python server.py
```

## Step 15: Build for Desktop

Create a desktop executable:

```bash
mikiui build --target desktop --onefile
```

This:
1. Builds the web assets
2. Auto-installs PyInstaller if needed
3. Creates a native executable
4. Wraps it in a platform-specific bundle (`.app` on macOS, `.exe` on Windows)

The output is in `dist_desktop/`. Run the executable to launch your app as a native desktop window.

## Step 16: Deploy

### Deploy Web

Upload the `dist/` directory to any static host:

```bash
# GitHub Pages
git add dist/
git commit -m "Deploy to GitHub Pages"
git push origin main
```

### Deploy Desktop

Distribute the executable from `dist_desktop/`:
- **Windows**: Share `dist_desktop/dist/mikiui_app.exe`
- **macOS**: Share `dist_desktop/TaskApp.app`
- **Linux**: Share `dist_desktop/dist/mikiui_app`

Users can run the executable without installing Python or any dependencies.

---

## Next Steps

- Add more routes and components — see [Components Guide](../guide/components.md)
- Use widgets for complex UI — see [Widgets Guide](../guide/widgets.md)
- Secure your app — see [Security Guide](../guide/security.md)
- Add plugins — see [Plugins Guide](../guide/plugins.md)
- Deploy to production — see [Deployment Guide](../guide/deployment.md)
