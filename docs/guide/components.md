# Components

All HTML elements are available as Python classes in MikiUI. Components map 1:1 to HTML tags, accept children and attributes, and render valid, accessible HTML.

## Basic Usage

```python
from mikiui import Div, H1, P, Button

Div(
    H1("Hello"),
    P("World"),
    Button("Click me", class_="miki-btn-primary"),
)
```

Renders as:

```html
<div>
  <h1>Hello</h1>
  <p>World</p>
  <button class="miki-btn-primary">Click me</button>
</div>
```

## Component Categories

### Document & Metadata
`Html`, `Head`, `Title`, `Meta`, `Link`, `Script`, `Style`, `Body`

### Text & Structure
`Heading`, `Paragraph`, `Span`, `Div`, `Section`, `Article`, `Aside`, `Header`, `Footer`, `Main`, `Nav`

### Lists
`UnorderedList`, `OrderedList`, `ListItem`, `DescriptionList`, `DescriptionTerm`, `DescriptionDetail`

### Forms & Inputs
`Form`, `Input`, `Textarea`, `Select`, `Checkbox`, `Radio`, `Button`, `Label`, `Fieldset`, `Legend`

### Media
`Image`, `Video`, `Audio`, `Canvas`, `SVG`, `Picture`, `Source`

### Interactive
`Dialog`, `Details`, `Summary`, `Menu`, `MenuItem`

## Accessibility

All components include appropriate ARIA attributes and semantic HTML by default:

- `Button.toggle` emits `aria-pressed`
- `Progress` emits `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
- `Input` emits `aria-required` and `aria-invalid` when applicable
- `Tabs` uses `<button>` elements for proper keyboard navigation

## Styling

Components accept `class_` and `style` parameters:

```python
Button("Save", class_="miki-btn-primary", style="margin-top: 1rem;")
```

Use `class_` (not `class`) to avoid Python keyword conflicts.

## Raw HTML

For trusted content that should not be escaped (e.g., inline SVG), use `RawHtml`:

```python
from mikiui.engine.dom import RawHtml

Div(RawHtml("<svg>...</svg>"))
```

## See Also

- [Widgets Guide](../guide/widgets.md) — high-level composite UI built from components
- [Styling Guide](../guide/styling.md) — Tailwind, plain CSS, and themes
- [API Reference](../guide/api-reference.md) — full component API
