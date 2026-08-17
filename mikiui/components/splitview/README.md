# SplitView Component

VS Code-like editor area with multiple resizable groups, tab bars, and drag-and-drop support.

## Installation

The component is part of `mikiui.components`:

```python
from mikiui.components import SplitView, EditorGroup, EditorTab
```

## Quick Start

```python
from mikiui.components import SplitView, EditorGroup, EditorTab
from mikiui.components.html import Div

app = MikiApp()

@app.route("/")
def editor():
    return SplitView(
        EditorGroup([
            EditorTab("main.py", Div("print('hello')")),
            EditorTab("readme.md", Div("# README")),
        ], active=0),
        EditorGroup([
            EditorTab("utils.py", Div("def helper(): pass")),
        ], active=0),
        orientation="horizontal",
    )
```

## Features

- **Multiple editor groups** in horizontal or vertical layouts
- **Tab bars** with close buttons and active state
- **Draggable splitters** with resize handles
- **Drag-and-drop** tabs between groups
- **Double-click** splitter to maximize/restore
- **Keyboard navigation** (arrow keys on tabs and splitters)
- **2×2 grid** layout with 4 children
- **ARIA-compliant** roles and properties
- **Theme support** (inherits app theme)
- **Self-contained** CSS and JS in `static/` directory

## API Reference

### `EditorTab(label, content, closable=True, icon=None)`

Represents a single tab in an editor group.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str` | required | Tab label (e.g. filename) |
| `content` | `Any` | required | Tab content (component tree) |
| `closable` | `bool` | `True` | Show close button |
| `icon` | `str \| None` | `None` | Optional icon emoji |

### `EditorGroup(tabs, active=0, group_id=None, **attrs)`

A single editor group with a tab bar and content panels.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tabs` | `list[EditorTab \| tuple]` | required | List of tabs |
| `active` | `int` | `0` | Initially active tab index |
| `group_id` | `str \| None` | `None` | Unique group ID (auto-generated) |
| `**attrs` | `dict` | - | Additional HTML attributes |

Tabs can be `EditorTab` instances or `(label, content)` tuples (or `(label, content, icon)`).

### `SplitView(*groups, orientation="horizontal", min_size=150, separator_width=4, **attrs)`

Arranges editor groups in a recursive grid layout with draggable splitters.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*groups` | `EditorGroup \| SplitView` | required | 1, 2, or 4 groups |
| `orientation` | `str` | `"horizontal"` | `"horizontal"` or `"vertical"` |
| `min_size` | `int` | `150` | Minimum pane size in pixels |
| `separator_width` | `int` | `4` | Splitter width/height in pixels |
| `**attrs` | `dict` | - | Additional HTML attributes |

**Child count behavior:**
- 1 child: single editor group
- 2 children: split horizontally or vertically
- 4 children: automatic 2×2 grid

## Layout Examples

### Horizontal Split

```python
SplitView(
    EditorGroup([EditorTab("left.py", left_content)]),
    EditorGroup([EditorTab("right.py", right_content)]),
    orientation="horizontal",
)
```

### Vertical Split

```python
SplitView(
    EditorGroup([EditorTab("top.py", top_content)]),
    EditorGroup([EditorTab("bottom.py", bottom_content)]),
    orientation="vertical",
)
```

### 2×2 Grid

```python
SplitView(
    EditorGroup([EditorTab("top-left.py", tl)]),
    EditorGroup([EditorTab("top-right.py", tr)]),
    EditorGroup([EditorTab("bottom-left.py", bl)]),
    EditorGroup([EditorTab("bottom-right.py", br)]),
    orientation="horizontal",  # auto-arranged into 2×2
)
```

### Nested Splits

```python
SplitView(
    SplitView(
        EditorGroup([EditorTab("top-left.py", tl)]),
        EditorGroup([EditorTab("top-right.py", tr)]),
        orientation="horizontal",
    ),
    EditorGroup([EditorTab("bottom.py", bottom_content)]),
    orientation="vertical",
)
```

## Styling

The component uses scoped CSS classes under `.miki-editor-area` and `.miki-splitview`. The theme system works automatically:

- Color themes (light, dark, dracula, solarized-dark) are inlined as CSS variables
- Framework themes (tailwind, bootstrap) use CDN or local CSS links
- The dark theme is applied by default in the demo

## JavaScript Behavior

The `splitview.js` runtime provides:
- Tab switching and closing
- Drag-and-drop between groups
- Splitter resize (mouse and touch)
- Double-click maximize/restore
- Keyboard navigation (Arrow keys, Home, End)
- Custom events: `miki:editor:tabchanged`, `miki:editor:tabclosed`, `miki:editor:tabdrop`, `miki:editor:resize`, `miki:editor:maximized`

## Accessibility

- `role="tablist"` on tab bars
- `role="tab"` on individual tabs
- `role="tabpanel"` on content panels
- `role="separator"` on splitters
- `aria-selected`, `aria-controls`, `aria-orientation` attributes
- Full keyboard navigation

## Demo

Run the full demo:

```bash
mikiui dev --app mikiui.examples.splitview_demo:app
```

The demo includes:
- Basic horizontal split (`/basic`)
- Multi-group vertical split (`/multi`)
- 2×2 editor grid (`/grid`)

## Static Assets

Component assets are served from the `static/` subdirectory:

```
mikiui/components/splitview/
    __init__.py
    splitview.py
    static/
        splitview.css
        splitview.js
```

URLs:
- CSS: `/_miki/components/splitview/static/splitview.css`
- JS: `/_miki/components/splitview/static/splitview.js`

## Theming

The component respects the app's theme. Use `app.set_theme()` before rendering:

```python
app = MikiApp()
app.set_theme("dark")  # or "light", "dracula", "solarized-dark"
```

Color themes set CSS variables (`--miki-bg`, `--miki-fg`, etc.) that the component's scoped CSS uses.

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Touch events supported for mobile
