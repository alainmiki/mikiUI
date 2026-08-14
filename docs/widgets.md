# Widget Catalog

MikiUI ships with a growing catalog of high-level widgets built on top of the
base HTML components. Below is a reference for every widget, organized by
category.

All widgets inherit from `Component` and render valid HTML with ARIA
attributes for accessibility.

---

## Layout Widgets

### Hero

A full-width hero banner with title, subtitle, and optional action button.

```python
from mikiui.widgets import Hero, Button

Hero(
    "Build Beautiful UIs",
    subtitle="Python-first UI framework",
    action=Button("Get Started", variant="primary"),
    image="https://images.unsplash.com/photo-1547627298414-c67913ffc827",
    variant="primary",  # primary | secondary | accent
    align="left",       # left | center | right
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | `str` | — | Hero heading |
| `subtitle` | `str` | `None` | Subheading text |
| `action` | `Any` | `None` | Action element (e.g. a `Button`) |
| `image` | `str` | `None` | Background image URL |
| `variant` | `str` | `"primary"` | Color variant |
| `align` | `str` | `"left"` | Text alignment |

---

### Footer

A page footer with optional social links and copyright.

```python
from mikiui.widgets import Footer

Footer(
    P("© 2024 MikiUI. All rights reserved."),
    copyright="MikiUI v0.1.0",
    social=[("GitHub", "https://github.com"), ("Docs", "https://kilo.ai/docs")],
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*content` | `Any` | — | Footer body content |
| `copyright` | `str` | `None` | Copyright text |
| `social` | `list` | `None` | List of (label, url) tuples |

---

### Sidebar

A collapsible side navigation panel.

```python
from mikiui.widgets import Sidebar

Sidebar(
    ("Home", "/"),
    ("Components", "/components"),
    ("Forms", "/forms"),
    title="Navigation",
    width="240px",
    mobile=False,
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*items` | `tuple` | — | (label, url) tuples for nav links |
| `title` | `str` | `None` | Sidebar header title |
| `width` | `str` | `"250px"` | CSS width |
| `mobile` | `bool` | `False` | Whether it's a mobile sidebar |

---

### Navbar

A top navigation bar with brand, links, and optional right-side content.
(See also `mikiui.components.Navbar` for the lightweight version.)

```python
from mikiui.components import Navbar
from mikiui.widgets import Button

Navbar(
    brand="MikiUI",
    links=[("Home", "/"), ("Components", "/components")],
    sticky=True, dark=True,
    right=Button("Login", variant="ghost"),
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `brand` | `str` | — | Brand/logo text |
| `links` | `list` | `None` | List of (label, url) tuples |
| `sticky` | `bool` | `False` | Whether navbar sticks to top |
| `dark` | `bool` | `False` | Dark background variant |
| `right` | `Any` | `None` | Right-side content |

---

### Drawer

A slide-in panel with modal overlay. Uses native `<dialog>` accessibility.

```python
from mikiui.widgets import Drawer

Drawer(
    Div("Settings content"),
    title="Settings",
    side="right",   # left | right | top | bottom
    size="md",      # sm | md | lg
    closeable=True,
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*content` | `Any` | — | Drawer body |
| `title` | `str` | `None` | Header title |
| `side` | `str` | `"left"` | Slide-in direction |
| `size` | `str` | `"md"` | Drawer width |
| `closeable` | `bool` | `True` | Show close button |

---

### Rail

A slim icon-only navigation rail, typically on the left edge of the screen.

```python
from mikiui.widgets import Rail

Rail(
    ("Dashboard", "/dashboard", "home"),
    ("Settings", "/settings", "settings"),
    side="left",  # left | right
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*items` | `tuple` | — | (label, url, icon_name) tuples |
| `side` | `str` | `"left"` | Which edge to attach to |

---

### ContextWindow

A floating context menu / popover window.

```python
from mikiui.widgets import ContextWindow

def do_delete():
    print("deleted")

ContextWindow(
    ("Delete", do_delete),
    ("Archive", "/archive"),
    trigger=Button("⋮"),
    position="bottom",  # auto | top | bottom | left | right
    align="start",      # start | center | end
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*content` | `Any` | — | Menu items: `(label, callable)` or `(label, url)` |
| `trigger` | `Any` | `None` | Element that triggers the context window |
| `position` | `str` | `"auto"` | Preferred position |
| `align` | `str` | `"start"` | Alignment |

---

## Advanced Widgets

### Card

A paper-like container with optional title, image, and footer.

```python
from mikiui.widgets import Card

Card(
    "Body content",
    title="Card Title",
    footer="Footer content",
    image="/pic.jpg",
    variant="filled",  # default | outlined | filled
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*content` | `Any` | — | Card body |
| `title` | `str` | `None` | Card header title |
| `footer` | `str` | `None` | Card footer content |
| `image` | `str` | `None` | Image URL (top of card) |
| `variant` | `str` | `"default"` | `default` \| `outlined` \| `filled` |

---

### Carousel

A slideshow component with navigation controls and autoplay support.

```python
from mikiui.widgets import Carousel

Carousel(
    ("https://via.placeholder.com/600x300", "Slide 1"),
    ("https://via.placeholder.com/600x300", "Slide 2"),
    autoplay=True,
    interval=5000,
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*slides` | `tuple` | — | (image_url, caption) tuples |
| `autoplay` | `bool` | `False` | Auto-advance slides |
| `interval` | `int` | `3000` | Time between slides (ms) |

---

### Pagination

A pagination component with previous/next controls.

```python
from mikiui.widgets import Pagination

Pagination(current=1, total=10, base_url="/page")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `current` | `int` | `1` | Current page number |
| `total` | `int` | `1` | Total number of pages |
| `base_url` | `str` | `"/"` | Base URL for page links |

---

### Avatar

A user avatar with optional status indicator.

```python
from mikiui.widgets import Avatar

Avatar("https://example.com/img.png", alt="User Name", status="online", size="lg")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `src` | `str` | — | Image URL |
| `alt` | `str` | `None` | Alt text |
| `size` | `str` | `"md"` | `sm` \| `md` \| `lg` |
| `status` | `str` | `None` | `online` \| `offline` \| `away` \| `busy` |

---

### Badge

A small status indicator / label.

```python
from mikiui.widgets import Badge

Badge("New", variant="primary", size="md")
Badge("Beta", variant="warning")
Badge("Deprecated", variant="error")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | — | Badge text |
| `variant` | `str` | `"default"` | `default` \| `primary` \| `secondary` \| `success` \| `warning` \| `error` \| `ghost` |
| `size` | `str` | `"md"` | `sm` \| `md` \| `lg` |

---

### Progress

A progress bar with optional label and color variant.

```python
from mikiui.widgets import Progress

Progress(75, label="Loading", variant="success")
Progress(100, label="Complete")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | `int`/`float` | — | Progress value (0–100, clamped) |
| `label` | `str` | `None` | Visible label |
| `variant` | `str` | `"default"` | `default` \| `primary` \| `success` \| `warning` \| `error` |

---

### Icon

An inline SVG icon — works in both web and desktop contexts without external dependencies.

```python
from mikiui.widgets import Icon, IconSet

Icon("home", size=24, variant="solid", class_="text-blue-400")
Icon("star", variant="outline")

# Check if an icon exists
IconSet.has_icon("home")  # True

# List all available icon names
IconSet.icon_names()      # ['alert', 'arrow-left', 'arrow-right', ...]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Icon name (see available list below) |
| `size` | `int` | `16` | Pixel size |
| `variant` | `str` | `"outline"` | `outline` \| `solid` |
| `class_` | `str` | `None` | Additional CSS classes |

**Available icons** (28 total):

`alert`, `arrow-left`, `arrow-right`, `badge`, `bell`, `calendar`, `check`,
`chevron-left`, `chevron-right`, `clock`, `copy`, `download`, `edit`, `eye`,
`external-link`, `home`, `info`, `menu`, `moon`, `plus`, `search`, `settings`,
`star`, `sun`, `trash`, `upload`, `user`, `close`

---

## Data & Media Widgets

### DataGrid

An interactive data table with sorting and filtering.

```python
from mikiui.widgets import DataGrid

DataGrid(
    columns=["Name", "Email", "Role"],
    rows=[["Alice", "alice@example.com", "Admin"]],
    sortable=True,
    filterable=True,
)
```

---

### TabbedPanel

A tabbed interface.

```python
from mikiui.widgets import TabbedPanel

TabbedPanel([
    ("Overview", Div("Overview content")),
    ("Details", Div("Details content")),
])
```

---

### CollapsiblePanel

A collapsible/accordion panel.

```python
from mikiui.widgets import CollapsiblePanel

CollapsiblePanel("Click to Toggle", Div("Hidden content"), open=False)
```

---

### MessageBox

A contextual message/alert box.

```python
from mikiui.widgets import MessageBox

MessageBox("Operation completed successfully!", type="success")
MessageBox("Error: something went wrong.", type="error")
```

---

### Drawer

See [Drawer](#drawer) above.

---

### MediaPlayer

An audio/video player widget.

```python
from mikiui.widgets import MediaPlayer

MediaPlayer(kind="audio", src="https://example.com/audio.mp3")
MediaPlayer(kind="video", src="https://example.com/video.mp4")
```

---

### KanbanBoard

A Kanban task board with drag-and-drop columns.

```python
from mikiui.widgets import KanbanBoard

KanbanBoard(
    columns={
        "Todo": ["Task A", "Task B"],
        "In Progress": ["Task C"],
        "Done": ["Task D"],
    },
)
```

---

### IDEEditor

A code editor with syntax highlighting.

```python
from mikiui.widgets import IDEEditor

IDEEditor(
    language="python",
    theme="dark",
    code="print('Hello, World!')",
)
```

---

### Dashboard

A dashboard layout for arranging widgets.

```python
from mikiui.widgets import Dashboard

Dashboard(
    widgets=[Button("Widget 1"), Button("Widget 2")],
)
```

---

## Form & Input Widgets

### DatePicker

A date picker input.

```python
from mikiui.widgets import DatePicker

DatePicker(label="Pick Date:", name="date")
```

---

### ColorPicker

A color picker input.

```python
from mikiui.widgets import ColorPicker

ColorPicker(label="Pick Color:", name="color", default="#3b82f6")
```

---

### Dial

A circular dial / knob control.

```python
from mikiui.widgets import Dial

Dial(value=50, min=0, max=100)
```

---

### LCDNumber

A digital-style number display.

```python
from mikiui.widgets import LCDNumber

LCDNumber(value=42, digits=6)
```

---

### Chart

A chart widget (line, bar, pie).

```python
from mikiui.components import Chart

Chart(
    type="line",
    data=[10, 20, 15, 25, 30],
    labels=["Mon", "Tue", "Wed", "Thu", "Fri"],
)
```

---

### LogViewer

A log display widget with auto-scrolling.

```python
from mikiui.widgets import LogViewer

LogViewer(lines=["info: Server started", "debug: Processing request"])
```

---

### TerminalWidget

A terminal emulator widget.

```python
from mikiui.widgets import TerminalWidget

TerminalWidget(prompt="$ ", history=["ls", "cat README.md"])
```

---

### FilePicker

A file browser / picker.

```python
from mikiui.widgets import FilePicker

FilePicker(path=".", accept=[".py", ".js"])
```

---

## Container & Layout Widgets

### DockablePanel

A dockable panel that can be dragged, closed, or float.

```python
from mikiui.widgets import DockablePanel

DockablePanel("Properties", Div("Property values"), closable=True, floatable=True)
```

---

### SplitView

A resizable split view with two panes.

```python
from mikiui.widgets import SplitView

SplitView(
    Div("Left pane"),
    Div("Right pane"),
    is_horizontal=True,
)
```

---

### ScrollPanel

A scrollable content panel.

```python
from mikiui.widgets import ScrollPanel

ScrollPanel(Div("Long content here..."), height="300px")
```

---

### TabbedPanel

See [TabbedPanel](#tabbedpanel) above.

---

### ToolboxPanel

A collapsible toolbox container.

```python
from mikiui.widgets import ToolboxPanel

ToolboxPanel("Tool Box", Div("Tools here"))
```

---

### ProgressDialog

A modal progress dialog.

```python
from mikiui.widgets import ProgressDialog

ProgressDialog(label="Loading...", value=50)
```

---

### GroupBox

A styled container with a title.

```python
from mikiui.components import GroupBox

GroupBox("Section Title", Div("Content"))
```

---

## Auth Widgets

### LoginForm

A pre-built login form.

```python
from mikiui.widgets import LoginForm

LoginForm(action="/login", method="post")
```

### SignupForm

A pre-built signup form.

```python
from mikiui.widgets import SignupForm

SignupForm(action="/signup", method="post")
```

---

## Navigation & Utility Widgets

### SplitView

See [SplitView](#splitview) above.

---

### GroupBox

See [GroupBox](#groupbox) above.

---

## Accessibility

All MikiUI widgets include:

- **ARIA roles** (`role="dialog"`, `role="navigation"`, `role="menu"`, etc.)
- **ARIA attributes** (`aria-label`, `aria-hidden`, `aria-modal`, `aria-current`)
- **Keyboard navigation** (Tab, Escape, arrow keys handled where applicable)
- **Semantic HTML** (`<nav>`, `<main>`, `<aside>`, `<section>`, etc.)

---

## i18n Support

All widgets accept a `data-i18n` attribute for internationalization:

```python
from mikiui.widgets import Button

Button("Save", data_i18n="buttons.save")
```

The `data-i18n` key can be used by a client-side i18n library to replace
the text content at runtime.
