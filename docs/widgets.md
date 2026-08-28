# Widget Catalog

MikiUI ships with a growing catalog of high-level widgets built on top of the
base HTML components. Below is a reference for every widget, organized by
category.

All widgets inherit from `Component` and render valid HTML with ARIA
attributes for accessibility.

---

## Widget Lifecycle

### Creation

Widgets are instantiated as Python objects:

```python
from mikiui.widgets import DataGrid

grid = DataGrid(
    columns=["Name", "Email"],
    rows=[{"Name": "Alice", "Email": "alice@example.com"}],
)
```

### Hooks

Custom widgets can implement lifecycle hooks:

```python
class MyWidget(Component):
    def __init__(self, *children, **attrs):
        super().__init__(*children, **attrs)
        self.on_mount()

    def on_mount(self):
        """Called when widget is first rendered."""
        pass

    def on_update(self, old_state):
        """Called when widget state changes."""
        pass

    def on_unmount(self):
        """Called when widget is removed from DOM."""
        pass
```

### Custom Widget Creation

Create a custom widget by composing components:

```python
from mikiui.components import Component, Div, H2, P, Button
from mikiui.widgets import Card

class ProfileCard(Card):
    def __init__(self, name, role, bio, **attrs):
        super().__init__(
            H2(name, class_="text-xl font-bold"),
            P(f"{role} — {bio}"),
            Button("Follow", variant="primary"),
            title=name,
            **attrs,
        )
```

Use it in your app:

```python
@app.route("/profile")
def profile():
    return ProfileCard("Alice", "Admin", "Python enthusiast")
```

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

A slide-in panel with modal overlay. Supports four sides, custom slide-in
direction via `open_side`, and ESC/overlay/close-button dismissal.

```python
from mikiui.widgets import Drawer

Drawer(
    Div("Settings content"),
    title="Settings",
    side="right",       # left | right | top | bottom  (panel anchor edge)
    open_side="right",  # optional: override slide-in direction
    size="md",          # sm | md | lg
    closable=True,
    open=False,
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*content` | `Any` | — | Drawer body |
| `title` | `str` | `None` | Header title |
| `side` | `str` | `"left"` | Edge the panel is anchored to |
| `size` | `str` | `"md"` | Panel width (`sm`=240px, `md`=320px, `lg`=480px) |
| `closable` | `bool` | `True` | Show close button |
| `open` | `bool` | `False` | Initial open state |
| `open_side` | `str\|None` | `None` | Override slide-in direction (e.g. `side="left"` with `open_side="right"`) |

**JS API:**

```javascript
// You can pass a CSS selector string, ID, or a DOM element
mikiDrawer.open('.my-drawer')     // opens
mikiDrawer.close('#drawer-1')     // closes
mikiDrawer.toggle('.my-drawer')   // toggles
```

---

### BottomSheet

A bottom sheet overlay that slides up from the bottom of the screen.
Supports drag-to-dismiss on touch devices, backdrop click, and ESC to close.

```python
from mikiui.components import BottomSheet

BottomSheet(
    Div("Sheet content"),
    title="My Sheet",
    size="md",       # sm | md | lg | full
    closable=True,
    on_close="handleClose",
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `*children` | `Any` | — | Sheet content |
| `title` | `str` | `None` | Header title |
| `closable` | `bool` | `True` | Show close button and enable backdrop/ESC close |
| `size` | `str` | `"md"` | Sheet width (`sm`=384px, `md`=640px, `lg`=90vw, `full`=100vw) |
| `on_open` | `str` | `None` | Callback name invoked on open |
| `on_close` | `str` | `None` | Callback name invoked on close |

**JS API:**

```javascript
mikiBottomSheet.open('.my-sheet')
mikiBottomSheet.close('#sheet-1')
```

---

### Rail

A slim icon-only navigation rail.

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

An inline SVG icon.

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

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `columns` | `list` | — | Column definitions |
| `rows` | `list` | — | Row data |
| `sortable` | `bool` | `True` | Allow sorting |
| `filterable` | `bool` | `False` | Allow filtering |
| `pagination` | `bool` | `True` | Enable pagination |
| `search` | `bool` | `True` | Enable search input |
| `page` | `int` | `0` | Current page (0-indexed) |
| `page_size` | `int` | `10` | Rows per page |
| `height` | `int` | `None` | Fixed height in px |

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

A lightweight code editor with a line-number gutter, tab handling,
auto-indent, undo/redo, and scroll-synced gutter.

```python
from mikiui.widgets import IDEEditor

IDEEditor(
    content="print('Hello, World!')",
    language="python",
    tab_size=4,
    line_numbers=True,
    readonly=False,
    placeholder="Start typing...",
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content` | `str` | `""` | Initial editor text |
| `language` | `str` | `"python"` | Language hint (CSS class) |
| `tab_size` | `int` | `4` | Spaces inserted on Tab |
| `line_numbers` | `bool` | `True` | Show line-number gutter |
| `readonly` | `bool` | `False` | Read-only mode |
| `placeholder` | `str` | `""` | Placeholder text |
| `editor_id` | `str` | `None` | DOM id for the container |

**JS API:**

```python
editor = document.querySelector('[data-miki-editor="true"]')
mikiIDE.setValue(editor, "new code")
text = mikiIDE.getValue(editor)
mikiIDE.insert(editor, "snippet")
```

**Events:** `miki:ide:input` (detail: `{ text }`), `miki:ide:scroll`.

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

A circular dial / knob control with click-to-value, drag, and keyboard
support. Smoothly animates via CSS transforms.

```python
from mikiui.widgets import Dial

Dial(
    value=50,
    min=0,
    max=100,
    step=5,
    size=140,     # diameter in pixels
    wrap="none",  # none | soft | hard
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | `float` | `50` | Current value |
| `min` | `float` | `0` | Minimum value |
| `max` | `float` | `100` | Maximum value |
| `step` | `float` | `1` | Increment step |
| `size` | `int` | `140` | Dial diameter in pixels |
| `wrap` | `str` | `"none"` | Wrap behavior at extremes |

**JS API:**

```javascript
var dial = document.querySelector('[data-miki-dial="true"]');
mikiDial.setValue(dial, 75);   // set value programmatically
var current = mikiDial.getValue(dial);  // get current value
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

A chart component for inline SVG line, bar, or pie charts.

```python
from mikiui.components import Chart

Chart(
    series=[10, 20, 15, 25, 30],
    kind="line",           # "line" | "bar" | "pie" (default: "bar")
    width=320,
    height=160,
)
```

Internally uses `RawHtml` to render SVG elements without HTML escaping.

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

A resizable split view with two panes (widget-level layout component).

```python
from mikiui.widgets import SplitView

SplitView(
    Div("Left pane"),
    Div("Right pane"),
    is_horizontal=True,
)
```

**Note:** The `EditorArea` component (`mikiui.components`) is a separate VS Code-like
multi-tab editor with `EditorGroup` and `EditorTab` companions. It was previously
named `SplitView` in `components/splitview/` but was renamed to resolve a
name collision with this layout widget.

---

### ScrollPanel

A scrollable content panel.

```python
from mikiui.widgets import ScrollPanel

ScrollPanel(Div("Long content here..."), height="300px")
```

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

---

### SignupForm

A pre-built signup form.

```python
from mikiui.widgets import SignupForm

SignupForm(action="/signup", method="post")
```

---

## Navigation & Utility Widgets

### ChatUI

A messaging interface with a scrollable log, typing indicator, and input form.

```python
from mikiui.widgets import ChatUI

ChatUI(
    messages=[
        {"role": "user", "text": "Hello!", "avatar": "U"},
        {"role": "bot", "text": "Hi there.", "avatar": "B", "time": "10:30"},
    ],
    multiline=False,
    placeholder="Type a message...",
)
```

**Message fields:** `role` (`"user"`/`"bot"`), `text`, `avatar` (text/URL/HTML), `time`.

**JS API:**

```python
chat = document.querySelector('[data-miki-chat="true"]')
mikiChat.appendMessage(chat, {"role": "bot", "text": "New message", "avatar": "B"})
mikiChat.toggleTyping(chat, True)
mikiChat.clear(chat)
```

**Events:** `miki:chat:send` (detail: `{ text }`), `miki:chat:messageadded`.

---

### InspectorPanel

A debugging state/routes panel.

```python
from mikiui.widgets import InspectorPanel

InspectorPanel(
    app_state=app.state,
    routes=list(app.routes.values()),
)
```

---

### PropertyGrid

An editable property/value grid.

```python
from mikiui.widgets import PropertyGrid

PropertyGrid(
    properties={
        "name": "Alice",
        "role": "Admin",
        "active": True,
    }
)
```

---

## Accessibility

All MikiUI widgets include:

- **ARIA roles** (`role="dialog"`, `role="navigation"`, `role="menu"`, etc.)
- **ARIA attributes** (`aria-label`, `aria-hidden`, `aria-modal`, `aria-current`)
- **Keyboard navigation** (Tab, Escape, arrow keys handled where applicable)
- **Semantic HTML** (`<nav>`, `<main>`, `<aside>`, `<section>`, etc.)

---

## i18n Support

All widgets accept a `data_i18n` attribute for internationalization:

```python
from mikiui.widgets import Button

Button("Save", data_i18n="buttons.save")
```

The `data_i18n` key can be used by a client-side i18n library to replace
the text content at runtime.

---

## JavaScript-Enhanced Widgets

Many MikiUI widgets rely on the bundled `miki_ui.js` for interactivity.
When `miki_ui.js` is loaded, it auto-initializes elements that have
`data-miki-*` attributes. This works **without** Alpine.js — the framework
includes its own minimal JS runtime that replaces all `x_on:*` / `x_data`
directives.

### Auto-Initialization

`miki_ui.js` runs on `DOMContentLoaded` and scans for elements with
`data-miki-*` attributes:

| Widget | Data Attribute | Description |
|--------|---------------|-------------|
| Tabs | `data-miki-tabs="true"` | Enables tab switching with keyboard navigation |
| Drawer | `data-miki-drawer="true"` | Slide-in panel with overlay close and ESC |
| Modal | `data-miki-modal="true"` | Modal dialog with ESC close and backdrop click |
| Dialog | `data-miki-dialog="true"` | Native `<dialog>` with polyfill for `showModal()` |
| ProgressDialog | `data-miki-progress-dialog="true"` | Modal progress with ESC close |
| SplitView | `data-miki-splitview="true"` | VS Code-style resizing; supports nested SplitViews, `resize_mode` (horizontal/vertical/both), min_size, dynamic add/remove panes, save/load layout |
| DockablePanel | `data-miki-dockable="true"` | Draggable header; drag toward any edge (top/left/right/bottom) to snap; customizable dimensions |
| Slider | `data-miki-slider="true"` | Live value display + PageUp/PageDown support |
| Dial | `data-miki-dial="true"` | Circular knob with rotation + keyboard support |
| Collapsible | `data-miki-collapsible="true"` | Smooth-expand accordion with toggle icon rotation |
| ProgressBar | `data-miki-progress="true"` | Striped animated progress bar |
| Toggle Button | `data-miki-toggle="true"` | Click to switch between two icon states |
| Searchable Select | `data-miki-searchable="true"` | Filter options by typing |
| Dropzone / FilePicker | `data-miki-dropzone="true"` | Drag-drop file selection with filename display |
| Upload | `data-miki-file-input="true"` | Hidden file input with label click handler |
| ContextWindow | `data-miki-context-window="true"` | Click-to-toggle floating context menu |
| MessageBox | `data-miki-messagebox="true"` | Alert with ESC and overlay close |
| MenuBar | `data-miki-menubar="true"` | Click/hover dropdowns, full keyboard nav, touch support |
| StackedPanel | `data-miki-stackedpanel="true"` | Tabbed page container with keyboard nav |
| IDEEditor | `data-miki-editor="true"` | Code editor with gutter, tab, undo/redo |
| MdiArea | `data-miki-mdiarea="true"` | Drag/resize/minimize/maximize sub-windows |
| EditorArea | `data-miki-editor-area="true"` | VS Code-like multi-group editor with splitters |
| DataGrid | `data-miki-datagrid="true"` | Sortable, filterable, paginated table |
| Kanban | `data-miki-kanban="true"` | Drag-and-drop task board |
| Carousel | `data-miki-carousel="true"` | Autoplay slideshow with arrows/dots |
| Chat | `data-miki-chat="true"` | Scrolling message log with typing indicator, append API |

### Global API

`miki_ui.js` exposes several `window.miki*` objects for imperative control
from Python-rendered `onclick` handlers:

```js
// Dialog
mikiDialog.show(dlg);     // Opens a <dialog> (with showModal polyfill)
mikiDialog.close(dlg);    // Closes it

// Modal
mikiModal.show(el);       // Shows modal overlay
mikiModal.close(el);      // Hides it

// Drawer
mikiDrawer.open(el);      // Opens drawer (adds .miki-drawer-open)
mikiDrawer.close(el);     // Closes drawer
mikiDrawer.toggle(el);    // Toggles

// SplitView
mikiSplitView.getLayout(el);   // Returns JSON-serializable layout state
mikiSplitView.setLayout(el, layout); // Restores layout from getLayout() result
mikiSplitView.addPane(el, html, position?); // Add a new pane (position: "before-first" or default)
mikiSplitView.removePane(el, index); // Remove a pane by index (0=first, 1=second)

// DockablePanel
mikiDockablePanel.toggle(el);   // Expand/collapse body
mikiDockablePanel.close(el);    // Hide panel (display:none)
mikiDockablePanel.show(el);     // Restore panel from closed state
mikiDockablePanel.detach(el);   // Float / dock
mikiDockablePanel.dockAt(el, 'top'|'left'|'right'|'bottom'|'floating'|'in-page'); // Snap to edge
// Default dock='in-page' keeps the panel inline in the parent flow.
// Use dockAt() to move to any edge, or detach() to float.

// Tabs
mikiTabs.show(groupId, index);  // Switch to tab at index
mikiTabs.close(groupId, index); // Close a tab
mikiTabs.activate(groupId, index);

// Slider
mikiSlider.setValue(input, value);

// Dial
// Value syncs automatically; use input.value to set programmatically

// Progress
mikiProgress.set(el, value, max);

// Progress Dialog
mikiProgressDialog.setValue(dlg, value);

// Collapsible
mikiCollapsible.open(el);
mikiCollapsible.close(el);
mikiCollapsible.toggle(el);

// Context Window
mikiContextWindow.open(container);
mikiContextWindow.close(container);
mikiContextWindow.toggle(container);

// Message Box
mikiMessageBox.show(el);
mikiMessageBox.close(el);

// Carousel
mikiCarousel.next(el);
mikiCarousel.prev(el);
mikiCarousel.goTo(el, index);
mikiCarousel.startAutoplay(el, interval);
mikiCarousel.stopAutoplay(el);

// DataGrid
mikiDataGrid.sort(el, field);
mikiDataGrid.applyFilter(el);

// Kanban
mikiKanban.draggedItem;  // Currently dragged item

// Chat
mikiChat.scrollToBottom(el);
mikiChat.toggleTyping(el, show);

// Global helpers (used in onclick attrs)
mikiCloseDialog(btn);   // Closes the dialog containing btn
mikiClose.dialog(btn);  // Closes dialog
mikiClose.modal(btn);   // Closes modal
```

### SplitView

The SplitView supports VS Code-style dynamic resizing via the `resize_mode` parameter:

```python
from mikiui.widgets import SplitView
from mikiui.components import Div

# Horizontal resize (drag splitter left/right — primary axis is X)
SplitView(Div("Left"), Div("Right"), resize_mode="horizontal")

# Vertical resize (drag splitter up/down — primary axis is Y)
SplitView(Div("Top"), Div("Bottom"), orientation="vertical", resize_mode="vertical")

# Bidirectional resize — drag in any direction
# The first meaningful mouse movement determines the active axis
SplitView(Div("A"), Div("B"), resize_mode="both")

# Vertical orientation with bidirectional resize
SplitView(Div("A"), Div("B"), orientation="vertical", resize_mode="both")
```

**Behavior**:
- The first pane's `flex-basis` grows/shrinks with the drag; the second pane
  automatically fills remaining space (flexbox `flex: 1 1 0` on release).
- In `both` mode, the system watches the initial drag direction: if you move more
  horizontally, it locks to X-axis; if vertically, Y-axis. This prevents accidental
  diagonal jitter.
- Double-click maximizes the first pane; double-click again restores.
- Keyboard: arrow keys adjust by 5px (Shift for 1px steps). Keys map to the
  orientation's primary axis (left/right for horizontal, up/down for vertical).
- Touch: single-finger drag works the same as mouse.

The splitter cursor indicates the active mode:
- `ew-resize` for horizontal drag
- `ns-resize` for vertical drag
- `nwse-resize` for bidirectional `both` mode

A visual gripper (`● ● ●`) appears on hover with dots oriented to match the
primary resize axis (vertical for horizontal mode, horizontal for vertical mode).

### DockablePanel

DockablePanel headers are draggable. When you drag a docked panel, it automatically
detaches into a floating window. Drag the floating window toward any screen edge
(top, left, right, or bottom) — visual snap zones appear with labels ("Dock Top",
"Dock Left", "Dock Right", "Dock Bottom") when you get close to an edge.

```python
from mikiui.widgets import DockablePanel

# Docked to the right by default, fully draggable
DockablePanel("Properties", Div("Content"), dock="right")

# Start floating (centered)
DockablePanel("Inspector", Div("Content"), dock="floating")

# Fully customized
DockablePanel(
    "Console",
    Div("Log output"),
    dock="bottom",
    collapsible=True,
    closeable=True,
    detachable=True,
    close_on_escape=True,
    snap_threshold=80,       # pixels from edge to trigger snap
    dock_width="400px",      # width when left/right docked
    dock_height="250px",     # height when top/bottom docked
    float_width="50vw",      # width when floating
    float_height="60vh",     # height when floating
)
```

**Customization parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dock` | `"right"` | Initial dock position: `top`, `left`, `right`, `bottom`, `floating` |
| `collapsible` | `True` | Show collapse/expand toggle button |
| `closeable` | `False` | Show close button |
| `detachable` | `True` | Allow detaching as floating panel |
| `open` | `True` | Initial expanded state |
| `close_on_escape` | `True` | Close floating panel with ESC key |
| `snap_threshold` | `100` | Pixel distance from screen edge to trigger snap-to-dock |
| `dock_width` | `"300px"` | Panel width when docked left/right |
| `dock_height` | `"300px"` | Panel height when docked top/bottom |
| `float_width` | `"40vw"` | Panel width when floating |
| `float_height` | `"50vh"` | Panel height when floating |

**Action buttons in the header**:
- **Toggle** (▼/▶ with rotation animation): Collapse/expand the panel body
- **Close** (×): Hide the panel
- **Detach** (⇋): Toggle between docked and floating state

**Drag-to-dock**:
1. Click and drag the header from any state (docked or floating)
2. The panel detaches to floating if it was docked
3. Drag toward a screen edge — snap zone indicators appear
4. Release near an edge to dock there, or release elsewhere to stay floating
5. Drag is constrained within viewport bounds during movement

### Fallback Behavior

If `miki_ui.js` fails to load, all widgets degrade gracefully to standard
HTML:

- **Tabs**: All tab panels are visible (no hiding). Navigation falls back to
  anchor links.
- **Drawer/Modal**: The `open` attribute on `<dialog>` is used as fallback.
- **Slider/Dial**: Native `<input type="range">` behavior with `<output>`.
- **SplitView**: Panes display side-by-side at their CSS-defined widths.
- **Toggle Button**: The button is static (no click-to-switch). The current
  icon state is shown as-is.
- **Searchable Select**: Falls back to native `<select>` dropdown.
- **Dropzone**: Falls back to plain file input (no drag-drop, no filename display).

### Accessibility Notes

- All interactive widgets support keyboard navigation (Tab, Enter, Space,
  Escape, arrow keys).
- ARIA attributes (`aria-expanded`, `aria-hidden`, `aria-modal`, etc.) are
  updated automatically by `miki_ui.js`.
- DockablePanel and Drawer include `tabindex="0"` for focus management.
- **Focus trap**: Dialogs, Modals, and MessageBoxes trap focus within them —
  Tab cycles between the first and last focusable element. Focus is restored
  to the triggering element when closed.
- **Focus restoration**: When a Dialog or Modal closes, focus returns to the
  element that opened it (stored via `data-miki-focus-trap-return`).
- **SplitView splitter**: Supports both mouse drag and keyboard (arrow keys
  for 1px, Shift+arrow for 5px, double-click to maximize).

---

## StackedPanel

A QStackedWidget-like container showing one page at a time with a tab strip.

```python
from mikiui.widgets import StackedPanel

StackedPanel(
    pages=[
        ("Overview", Div("Project overview metrics and KPIs.")),
        ("Analytics", Div("Traffic and engagement data.")),
        ("Reports", Div("Generated reports and exports.")),
    ],
    active=0,
)
```

**Parameters:** `pages` (list of `(title, content)`), `active` (initial index), `panel_id`.

**JS API:** `mikiStackedPanel.show(el, index)`, `mikiStackedPanel.activeIndex(el)`.

**Events:** `miki:stackedpanel:change` (detail: `{ index }`).

**Keyboard:** ArrowLeft/Right to move, Home/End to jump, Enter/Space to activate.

---

## MdiArea / MdiSubWindow

A multiple-document interface (QMdiArea) with draggable, resizable sub-windows.

```python
from mikiui.widgets import MdiArea, MdiSubWindow

MdiArea(
    MdiSubWindow("main.py", Div("code..."), icon="📄"),
    MdiSubWindow("readme.md", Div("docs..."), left=60),
)
```

**MdiSubWindow parameters:** `title`, `*content`, `icon`, `minimizable`, `maximizable`, `closeable`, `left`, `top`, `width`, `height`.

**JS API:**
- `mikiMDI.activate(win)`, `mikiMDI.close(win)`, `mikiMDI.minimize(win)`, `mikiMDI.maximize(win)`, `mikiMDI.restore(win)`
- `mikiMDI.cascade(area)`, `mikiMDI.tile(area)`

**Events:** `miki:mdi:activate`, `miki:mdi:close`, `miki:mdi:minimize`, `miki:mdi:maximize`, `miki:mdi:move`, `miki:mdi:resize`.

**Interactions:** Drag titlebar to move, drag edges/corners to resize, double-click titlebar to maximize/restore, click to bring to front.

---

## EditorArea / EditorGroup / EditorTab

A VS Code-like multi-group editor with tab bars, drag-and-drop tabs, and resizable splitters.

```python
from mikiui.components import EditorArea, EditorGroup, EditorTab

EditorArea(
    EditorGroup([EditorTab("main.py", "print('hello')"), EditorTab("readme.md", "# README")], active=0),
    EditorGroup([EditorTab("utils.py", "def helper(): pass")]),
    orientation="horizontal",
)
```

**EditorTab:** `label`, `content`, `closable`, `icon`.

**EditorGroup:** `tabs`, `active`, `group_id`.

**EditorArea:** `*groups`, `orientation` (`"horizontal"`/`"vertical"`), `min_size`, `separator_width`.

**Events:** `miki:editor:tabchanged`, `miki:editor:tabclosed`, `miki:editor:tabdrop`, `miki:editor:resize`, `miki:editor:maximized`.

**Keyboard:** ArrowLeft/Right to switch tabs, Home/End to jump, Enter/Space to activate, arrow keys on splitter to resize.

