"""SplitView Demo — VS Code-like editor area.

Showcases ``mikiui.components.SplitView`` with:
- Horizontal / vertical / nested layouts
- Tab bars with close buttons and icons
- Draggable splitters
- Drag-and-drop tabs between groups
- Double-click to maximize/restore
- Keyboard navigation
- Theme switching (light, dark, dracula, solarized-dark)

Run with::

    mikiui dev --app mikiui.examples.splitview_demo:app
"""

from __future__ import annotations

from mikiui import H1, H2, MikiApp, P
from mikiui.components import Button, Div
from mikiui.components.splitview import EditorGroup, EditorTab, SplitView

app = MikiApp(title="MikiUI SplitView Demo", lang="en")
app.set_theme("dark")

# ---------------------------------------------------------------------------
# Sample content
# ---------------------------------------------------------------------------

PYTHON_CODE = """\
def fibonacci(n: int) -> list[int]:
    \"\"\"Return the first n Fibonacci numbers.\"\"\"
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result


if __name__ == "__main__":
    print(fibonacci(10))
"""

JS_CODE = """\
// Debounce utility
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
"""

TS_CODE = """\
interface User {
  id: number;
  name: string;
  email: string;
}

function findUser(id: number): User | undefined {
  return users.find((u) => u.id === id);
}
"""

RUST_CODE = """\
fn fibonacci(n: u32) -> Vec<u64> {
    let mut result = Vec::new();
    let (mut a, mut b) = (0u64, 1u64);
    for _ in 0..n {
        result.push(a);
        (a, b) = (b, a + b);
    }
    result
}
"""

MARKDOWN = """\
# Project README

Welcome to the **MikiUI** SplitView demo.

## Features
- VS Code-like split view with resizable panes
- Draggable tabs between editor groups
- Double-click splitters to maximize/restore
- Keyboard navigation on tabs and splitters
- Theme-aware styling

## Quick Start
```bash
mikiui dev --app mikiui.examples.splitview_demo:app
```
"""

JSON_DATA = """\
{
  "name": "mikiui-demo",
  "version": "1.0.0",
  "scripts": {
    "dev": "mikiui dev",
    "build": "mikiui build --target web"
  }
}
"""

CSS_CODE = """\
/* App styles */
:root {
  --primary: #3b82f6;
  --bg: #0f172a;
  --fg: #f1f5f9;
}

body {
  font-family: system-ui, sans-serif;
  background: var(--bg);
  color: var(--fg);
}
"""

HTML_CODE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>MikiUI App</title>
</head>
<body>
  <div id="app"></div>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _toolbar(content: str, icon: str = "📄") -> Div:
    return Div(
        f"{icon} {content}",
        class_="flex items-center gap-2 px-3 py-1.5 text-xs",
    )


def _editor(label: str, code: str, icon: str = "📄") -> Div:
    return Div(
        _toolbar(label, icon),
        Div(
            code,
            class_="flex-1 overflow-auto p-4 font-mono text-sm leading-relaxed",
        ),
        class_="flex flex-col h-full min-h-0",
    )


def _placeholder(text: str, icon: str = "📁") -> Div:
    return Div(
        Div(f"{icon} {text}", class_="text-sm"),
        class_="flex items-center justify-center h-full",
    )


# ---------------------------------------------------------------------------
# Theme switcher helper
# ---------------------------------------------------------------------------

THEMES = ["light", "dark", "dracula", "solarized-dark"]


def _theme_switcher() -> Div:
    return Div(
        *[
            Button(
                theme.title(),
                hx_post=f"/set-theme/{theme}",
                hx_target="#theme-indicator",
                hx_swap="innerHTML",
                variant="ghost" if theme != "dark" else "primary",
                class_="text-xs",
            )
            for theme in THEMES
        ],
        class_="flex gap-2",
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def home() -> Div:
    """Landing page with navigation cards."""
    return Div(
        Div(
            H1("MikiUI SplitView", class_="text-3xl font-bold mb-2"),
            P(
                "A VS Code-like editor area with resizable panes, draggable tabs, and theme support.",
                class_="text-muted mb-2",
            ),
            Div(
                _theme_switcher(),
                id="theme-indicator",
                class_="mb-6 p-3 rounded-lg border",
            ),
            Div(
                _demo_card(
                    "Basic Split",
                    "Two editor groups side-by-side with a draggable splitter.",
                    "/basic",
                ),
                _demo_card(
                    "Vertical Split",
                    "Three editor groups stacked vertically.",
                    "/vertical",
                ),
                _demo_card(
                    "Nested Splits",
                    "Complex layout with nested horizontal and vertical splits.",
                    "/nested",
                ),
                _demo_card(
                    "2×2 Grid",
                    "Four editor groups in a grid layout.",
                    "/grid",
                ),
                _demo_card(
                    "Tab Actions",
                    "Switch, close, and drag tabs between groups.",
                    "/tabs",
                ),
                class_="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
            ),
            class_="max-w-6xl mx-auto p-8",
        ),
        class_="min-h-screen",
    )


def _demo_card(title: str, desc: str, href: str) -> Div:
    return Div(
        Div(H2(title, class_="text-lg font-semibold mb-1"), P(desc, class_="text-sm text-muted mb-3")),
        Button("Open Demo", hx_get=href, hx_push_url="true", variant="primary"),
        class_="p-4 rounded-lg border hover:border-accent transition-colors",
    )


@app.route("/basic")
def basic_split() -> Div:
    """Simple horizontal split with two editor groups."""
    left = EditorGroup(
        [
            EditorTab("main.py", _editor("main.py", PYTHON_CODE, "🐍"), icon="🐍"),
            EditorTab("utils.py", _editor("utils.py", JS_CODE, "📜"), icon="📜"),
            EditorTab("config.json", _editor("config.json", JSON_DATA, "📋"), icon="📋"),
        ],
        active=0,
    )
    right = EditorGroup(
        [
            EditorTab("styles.css", _editor("styles.css", CSS_CODE, "🎨"), icon="🎨"),
            EditorTab("index.html", _editor("index.html", HTML_CODE, "🌐"), icon="🌐"),
        ],
        active=0,
    )

    return Div(
        _page_header("Basic Horizontal Split", "Two editor groups separated by a draggable splitter."),
        Div(
            SplitView(
                left,
                right,
                orientation="horizontal",
                min_size=120,
            ),
            class_="h-[500px] border rounded-lg overflow-hidden",
        ),
        _back_button(),
        class_="min-h-screen",
    )


@app.route("/vertical")
def vertical_split() -> Div:
    """Three editor groups arranged vertically."""
    top = EditorGroup(
        [EditorTab("header.py", _editor("header.py", PYTHON_CODE, "🐍"))],
        active=0,
    )
    middle = EditorGroup(
        [
            EditorTab("app.ts", _editor("app.ts", TS_CODE, "📘")),
            EditorTab("styles.css", _editor("styles.css", CSS_CODE, "🎨")),
        ],
        active=0,
    )
    bottom = EditorGroup(
        [EditorTab("main.rs", _editor("main.rs", RUST_CODE, "🦀"))],
        active=0,
    )

    return Div(
        _page_header("Vertical Split", "Three editor groups stacked vertically. Drag the horizontal splitters."),
        Div(
            SplitView(
                SplitView(top, middle, orientation="horizontal", min_size=120),
                bottom,
                orientation="vertical",
                min_size=100,
            ),
            class_="h-[600px] border rounded-lg overflow-hidden",
        ),
        _back_button(),
        class_="min-h-screen",
    )


@app.route("/nested")
def nested_split() -> Div:
    """Complex nested layout."""
    top_left = EditorGroup(
        [EditorTab("main.py", _editor("main.py", PYTHON_CODE, "🐍"))],
        active=0,
    )
    top_right = EditorGroup(
        [EditorTab("utils.py", _editor("utils.py", JS_CODE, "📜"))],
        active=0,
    )
    bottom = EditorGroup(
        [
            EditorTab("readme.md", _editor("readme.md", MARKDOWN, "📝")),
            EditorTab("config.json", _editor("config.json", JSON_DATA, "📋")),
        ],
        active=0,
    )

    return Div(
        _page_header("Nested Splits", "A complex layout mixing horizontal and vertical splits."),
        Div(
            SplitView(
                SplitView(
                    top_left,
                    top_right,
                    orientation="vertical",
                    min_size=100,
                ),
                bottom,
                orientation="horizontal",
                min_size=150,
            ),
            class_="h-[600px] border rounded-lg overflow-hidden",
        ),
        _back_button(),
        class_="min-h-screen",
    )


@app.route("/grid")
def grid_2x2() -> Div:
    """Four editor groups in a 2×2 grid."""
    groups = [
        EditorGroup([EditorTab("main.py", _editor("main.py", PYTHON_CODE, "🐍"))], active=0),
        EditorGroup([EditorTab("app.ts", _editor("app.ts", TS_CODE, "📘"))], active=0),
        EditorGroup([EditorTab("styles.css", _editor("styles.css", CSS_CODE, "🎨"))], active=0),
        EditorGroup([EditorTab("readme.md", _editor("readme.md", MARKDOWN, "📝"))], active=0),
    ]

    return Div(
        _page_header("2×2 Editor Grid", "Four editor groups arranged in a grid. Pass 4 children to SplitView."),
        Div(
            SplitView(*groups, orientation="horizontal", min_size=100),
            class_="h-[600px] border rounded-lg overflow-hidden",
        ),
        _back_button(),
        class_="min-h-screen",
    )


@app.route("/tabs")
def tab_actions() -> Div:
    """Demonstrate tab switching, closing, and drag-drop."""
    left = EditorGroup(
        [
            EditorTab("main.py", _editor("main.py", PYTHON_CODE, "🐍")),
            EditorTab("utils.py", _editor("utils.py", JS_CODE, "📜")),
            EditorTab("config.json", _editor("config.json", JSON_DATA, "📋")),
            EditorTab("styles.css", _editor("styles.css", CSS_CODE, "🎨")),
        ],
        active=1,
    )
    right = EditorGroup(
        [
            EditorTab("readme.md", _editor("readme.md", MARKDOWN, "📝")),
            EditorTab("index.html", _editor("index.html", HTML_CODE, "🌐")),
        ],
        active=0,
    )

    return Div(
        _page_header(
            "Tab Actions",
            "Click tabs to switch, use the × button to close, or drag tabs between groups.",
        ),
        Div(
            SplitView(
                left,
                right,
                orientation="horizontal",
                min_size=120,
            ),
            class_="h-[500px] border rounded-lg overflow-hidden",
        ),
        Div(
            P("Tip: Double-click a splitter to maximize that pane. Press Arrow keys on a focused splitter to resize.", class_="text-sm text-muted"),
            class_="p-4",
        ),
        _back_button(),
        class_="min-h-screen",
    )


@app.post("/set-theme/{theme_name}")
def set_theme(theme_name: str) -> str:
    """Switch the app theme."""
    app.set_theme(theme_name)
    return f'<span class="text-sm font-medium">Theme: <strong>{theme_name}</strong></span>'


# ---------------------------------------------------------------------------
# Shared layout helpers
# ---------------------------------------------------------------------------


def _page_header(title: str, description: str) -> Div:
    return Div(
        H1(title, class_="text-xl font-bold p-4"),
        P(description, class_="text-muted px-4 pb-2"),
        class_="border-b",
    )


def _back_button() -> Div:
    return Div(
        Button("← Back to Home", hx_get="/", hx_push_url="true", variant="ghost", class_="m-4"),
        class_="flex",
    )


if __name__ == "__main__":
    app.run(desktop=True)
