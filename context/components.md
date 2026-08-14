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

### Developer Tools
- **IDE-like Editor** → Code editor with syntax highlighting.
- **TerminalWidget** → Embedded console/terminal.
- **LogViewer** → Real-time logs with filters.
- **ProfilerPanel** → Performance metrics visualization.

---

## Notes
- All components are **Python classes** returning HTML + Tailwind/Bootstrap styling.
- Widgets are **composite classes** built from base components.
- Accessibility (ARIA roles, keyboard navigation) is mandatory.
- Internationalization hooks must be available in all components/widgets.
