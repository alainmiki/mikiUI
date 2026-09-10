# Widgets

Widgets are high-level composite UI components built on top of base HTML components. They provide ready-to-use patterns for common application interfaces.

## Using Widgets

```python
from mikiui.widgets import DataGrid, Card, ChatUI

grid = DataGrid(
    columns=["Name", "Email"],
    rows=[{"Name": "Alice", "Email": "alice@example.com"}],
)

card = Card(
    title="Profile",
    body="User information here",
)
```

## Widget Categories

### Layout
`DockablePanel`, `SplitView`, `StackedPanel`, `MdiArea`, `MdiSubWindow`

### Data Display
`DataGrid`, `Table`, `TreeView`, `Calendar`, `Carousel`

### Media
`MediaPlayer`, `VideoPlayer`, `AudioPlayer`

### Input & Forms
`ChatUI`, `CommandPalette`, `SearchBox`

### Code & Editing
`IDEEditor`, `EditorGroup`, `EditorArea`

### Navigation
`Sidebar`, `Navbar`, `Breadcrumbs`, `Tabs`, `Pagination`

### Feedback
`Toast`, `ProgressBar`, `Spinner`, `Alert`

## Custom Widgets

Create custom widgets by composing components:

```python
from mikiui.components import Component, Div, H2, P, Button
from mikiui.widgets import Card

class ProfileCard(Card):
    def __init__(self, name, role, bio, **attrs):
        super().__init__(
            H2(name),
            P(f"Role: {role}"),
            P(bio),
            **attrs,
        )
```

## Lifecycle Hooks

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

## See Also

- [Components Guide](../guide/components.md) — base HTML element components
- [Styling Guide](../guide/styling.md) — styling widgets with Tailwind or plain CSS
- [API Reference](../guide/api-reference.md) — full widget API
