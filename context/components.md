# MikiUI Components & Widgets Catalog

## Purpose
This catalog defines all base components (HTML elements) and advanced widgets/panels available in MikiUI. It ensures parity with PyQt and VS UI, while remaining approachable for beginners.

---

## Base Components (All HTML Elements)

### Document & Metadata
- **Html** → `<html>`
- **Head** → `<head>`
- **Title** → `<title>`
- **Meta** → `<meta>`
- **Link** → `<link>`
- **Script** → `<script>`
- **Style** → `<style>`
- **Body** → `<body>`

### Text & Structure
- **Heading** → `<h1>` … `<h6>`
- **Paragraph** → `<p>`
- **Span** → `<span>`
- **Div** → `<div>`
- **Section** → `<section>`
- **Article** → `<article>`
- **Aside** → `<aside>`
- **Header** → `<header>`
- **Footer** → `<footer>`
- **Main** → `<main>`
- **Nav** → `<nav>`

### Lists
- **UnorderedList** → `<ul>`
- **OrderedList** → `<ol>`
- **ListItem** → `<li>`
- **DescriptionList** → `<dl>`
- **DescriptionTerm** → `<dt>`
- **DescriptionDetail** → `<dd>`

### Forms & Inputs
- **Form** → `<form>`
- **Input** → `<input>` (text, password, email, number, file, date, color, etc.)
- **Textarea** → `<textarea>`
- **Select** → `<select>` + `<option>`
- **Checkbox** → `<input type="checkbox">`
- **Radio** → `<input type="radio">`
- **Button** → `<button>`
- **Label** → `<label>`
- **Fieldset** → `<fieldset>`
- **Legend** → `<legend>`

### Media
- **Image** → `<img>`
- **Video** → `<video>`
- **Audio** → `<audio>`
- **Canvas** → `<canvas>`
- **SVG** → `<svg>`
- **Picture** → `<picture>`
- **Source** → `<source>`

### Interactive Elements
- **Dialog** → `<dialog>`
- **Details** → `<details>` + `<summary>`
- **Modal** → custom `<div>` + overlay
- **Tabs** → `<nav>` + `<section>`
- **Accordion** → collapsible panels
- **Tooltip** → hover info

### Data & Display
- **Table** → `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<td>`
- **ProgressBar** → `<progress>`
- **Meter** → `<meter>`
- **Slider** → `<input type="range">`
- **Output** → `<output>`

### Navigation
- **Anchor** → `<a>`
- **Breadcrumbs** → `<nav>` + `<ol>`
- **Menu** → `<menu>`
- **MenuItem** → `<menuitem>`

### Semantic & Misc
- **Time** → `<time>`
- **Code** → `<code>`
- **Preformatted** → `<pre>`
- **Blockquote** → `<blockquote>`
- **Figure** → `<figure>` + `<figcaption>`
- **Mark** → `<mark>`
- **Small** → `<small>`
- **Strong** → `<strong>`
- **Emphasis** → `<em>`
- **Abbreviation** → `<abbr>`
- **Address** → `<address>`
- **Citation** → `<cite>`
- **Keyboard** → `<kbd>`
- **Variable** → `<var>`
- **Sample** → `<samp>`

---

## Advanced Widgets (Composite Components)

### Data & Productivity
- **DataGrid** → Table + Pagination + Filters.
- **TreeView** → Hierarchical list.
- **ListView** → Scrollable list with selection.
- **Calendar** → Date/time picker + events.
- **FilePicker** → File upload/download UI.
- **Chart** → Line, bar, pie charts.
- **FormWizard** → Multi-step form with validation.
- **SearchPanel** → Search bar + filters + results.

### Media & Communication
- **MediaPlayer** → Video/Audio player with EQ, recording.
- **Recorder** → Audio/video recording widget.
- **ChatUI** → Messaging interface.
- **StreamingPanel** → Live data/video stream.
- **NotificationPanel** → Toasts, alerts, system notifications.

### Panels & Layouts
- **DockablePanel** → Panels that can be docked/floated.
- **SplitView** → Resizable split panes.
- **PropertyGrid** → Editable property/value pairs.
- **Dashboard** → Cards + Charts + Tabs.
- **KanbanBoard** → Task management board.
- **InspectorPanel** → Debugging state/routes.
- **CollapsiblePanel** → Expand/collapse sections.
- **SidePanel** → Slide-in navigation or tools.
- **TabbedPanel** → Multi-tabbed content areas.

### Theming
- **ThemeSwitcher** → Dynamic dropdown that auto-discovers all registered themes (built-in + custom plugins) and switches via HTMX or direct app API.

### Developer Tools
- **IDE-like Editor** → Code editor with syntax highlighting.
- **TerminalWidget** → Embedded console/terminal.
- **LogViewer** → Real-time logs with filters.
- **ProfilerPanel** → Performance metrics visualization.

---

## Notes
- All components are **Python classes** returning HTML + Tailwind/plain-CSS styling.
- Widgets are **composite classes** built from base components.
- Accessibility (ARIA roles, keyboard navigation) is mandatory.
- Internationalization hooks must be available in all components/widgets.

---

## Styling & Theming System

### Overview

MikiUI uses a layered CSS architecture that works seamlessly with both:
- **Plain CSS mode** - Built-in styles via `miki.css`
- **Tailwind CSS mode** - Hybrid approach with Tailwind utilities

### CSS Layers

1. **`miki.css`** (Always loaded) - Contains:
   - CSS custom properties (`--miki-*`) for themeable values
   - Base styles, typography, and widget layouts
   - Component styles using Tailwind-like utility classes (`miki-btn`, `miki-card`, etc.)
   - `@layer base`, `@layer components`, `@layer utilities` declarations

2. **Color Theme CSS** (light.css, dark.css, dracula.css, etc.) - Sets:
   - `--miki-*` CSS variable values on `:root`
   - Color palette for the active theme

3. **Framework CSS** (optional) - Tailwind:
   - CDN mode: Loads Tailwind via `https://cdn.tailwindcss.com`
   - Local mode: Loads pre-built CSS via `mikiui build`

### Using Tailwind with Widgets

Widgets work in Tailwind mode because:

1. **CSS Variables Contract**: Widgets use `--miki-*` variables that Tailwind can define in `tailwind.config.js`

2. **CSS Cascade**: `miki.css` loads **after** Tailwind, ensuring widget styles apply

3. **Class Composition**: Widgets add both `miki-*` classes (for structured styles) and allow `class_` for Tailwind customization

```python
from mikiui.widgets import Card, Button

# Works in both plain and Tailwind modes
Card(
    Button("Click me", class_="bg-blue-500 hover:bg-blue-600"),
    class_="shadow-lg"
)
```

### Available Color Themes

Built-in themes are DaisyUI-compatible and work with both modes:

| Theme | Style |
|-------|-------|
| `light` | Light background |
| `dark` | Dark theme |
| `dracula` | Dark violet theme |
| `solarized-dark` | Solarized dark |
| `cupcake` | Soft pastel |
| `synthwave` | Neon synthwave |
| `cyberpunk` | Cyberpunk neon |
| `forest` | Green forest |
| `halloween` | Halloween theme |
| `valentine` | Valentine theme |
| `emerald` | Emerald theme |
| `aqua` | Aqua theme |
| `bumblebee` | Bumblebee (light) |
| `garden` | Garden theme |
| `pastel` | Pastel colors |
| `retro` | Retro theme |

### Switching Themes

```python
from mikiui import MikiApp

app = MikiApp()
app.set_theme("dark")  # or "light", "dracula", etc.

# Or use Tailwind mode with a color theme
app.set_style_framework("tailwind", daisyui=True)
app.set_theme("dark")
```

### Combining Tailwind Utilities with MikiUI Classes

```python
from mikiui.components import Div, Button, Grid
from mikiui.widgets import DataGrid

# Use Tailwind for layout + MikiUI for behavior
Div(
    DataGrid(columns=["Name", "Email"], rows=[...], class_="w-full"),
    class_="bg-gray-50 p-4 rounded-xl shadow-md"
)

# Override button styles with Tailwind
Button("Submit", class_="px-6 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold")
```

### CSS Custom Properties Reference

Widgets reference these CSS variables (defined in `miki.css`):

| Variable | Default | Description |
|----------|---------|-------------|
| `--miki-bg` | `#f8fafc` | Background color |
| `--miki-fg` | `#0f172a` | Foreground/text color |
| `--miki-accent` | `#2563eb` | Accent color |
| `--miki-accent-hover` | `#1d4ed8` | Accent hover state |
| `--miki-border` | `#e2e8f0` | Border color |
| `--miki-surface` | `#ffffff` | Surface/background |
| `--miki-surface-hover` | `#f1f5f9` | Surface hover state |
| `--miki-text-muted` | `#64748b` | Muted text color |
| `--miki-success` | `#16a34a` | Success state |
| `--miki-warning` | `#d97706` | Warning state |
| `--miki-error` | `#dc2626` | Error state |
| `--miki-radius` | `0.5rem` | Border radius |
| `--miki-shadow` | `0 1px 3px rgba(0,0,0,0.1)` | Shadow |
