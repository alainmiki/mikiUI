# Plan: MikiUI PyQt6 Equivalents Implementation

## Goal
Implement the PyQt6-equivalent widgets from the user's proposal, placing them according to the project architecture (`components/` = 1:1 HTML elements, `widgets/` = composites). Upgrade existing implementations where they overlap.

## Decisions
- **Placement**: All composites go in `mikiui/widgets/` (specifically `panels.py` for panel-like widgets, or a new file if volume justifies). `ListView` already lives in `components/listview.py`; upgrade it in place.
- **Dial**: Already exists in `widgets/panels.py` as a rich widget with rotary knob + JS (`data-miki-dial`). Leave as-is. Do NOT add the simpler duplicate `MikiDial` from the proposal — it conflicts with existing CSS classes and JS behavior.
- **ListView**: Upgrade in `components/listview.py` to use `Div` items with `role="listitem"` and container `role="list"` (matching the proposal's simpler, more generic structure). Preserve the `selected` parameter.
- **ToolboxPanel**: Upgrade in `widgets/panels.py` to accept arbitrary content per section (`dict[str, Any]`) using `Div` headers/bodies with `.miki-toolbox-section`, `.miki-toolbox-header`, `.miki-toolbox-body`, and `.active` toggling. Preserve backward compatibility with the existing list-based API if possible, or replace cleanly.
- **Menu**: Keep existing `MenuBar` in `widgets/panels.py`. Add `MikiMenu` as a simpler standalone menu widget (list of items) to complement `MenuBar`.
- **New widgets**: `MikiSizeGrip`, `MikiColumnView`, `MikiButtonGroup` — all go in `widgets/panels.py` (or a new `mikiui/widgets/pyqt_equivalents.py` if preferred).

## Task List

### 1. Upgrade `ListView` in `mikiui/components/listview.py`
- Change items from `Li(..., role="option")` to `Div(..., role="listitem")`.
- Change container from `Ul` inside `Div(role="listbox")` to `tag="ul"` with `role="list"`.
- Preserve `selected` parameter logic.
- Update CSS class to `miki-listview`.

### 2. Upgrade `ToolboxPanel` in `mikiui/widgets/panels.py`
- Change from `Details/Summary` + `Ul/Li` to `Div` sections with header/body.
- Accept `dict[str, Any]` where values are arbitrary content (not just lists).
- Use classes: `miki-toolbox`, `miki-toolbox-section`, `miki-toolbox-header`, `miki-toolbox-body`.
- Add `role="group"` to sections and `aria` attributes for accessibility.

### 3. Add new widgets to `mikiui/widgets/panels.py`
Add the following classes:

- **`MikiMenu`**: `tag="ul"`, accepts `list[str]` items, renders each as `Div(item, class_="miki-menu-item", role="menuitem")`. Container has `class_="miki-menu"`, `role="menu"`. Supports `onclick` per item.
- **`MikiSizeGrip`**: `tag="div"`, `class_="miki-sizegrip"`, `role="separator"`.
- **`MikiColumnView`**: `tag="div"`, `class_="miki-columnview"`, `role="list"`. Accepts `list[list[str]]` columns. Each column is `Div(*items, class_="miki-column")`, each item is `Div(item, class_="miki-column-item")`.
- **`MikiButtonGroup`**: `tag="div"`, `class_="miki-btngroup"`, `role="group"`. Accepts `list[str]` buttons, each rendered as `Div(label, class_="miki-btn")`.

### 4. Update CSS in `mikiui/runtime/miki.css`
- Update `.miki-listview` to style `ul > div` children (instead of `li`).
- Update `.miki-toolbox` to style the new `Div`-based section structure.
- Add new CSS blocks for:
  - `.miki-menu` and `.miki-menu-item`
  - `.miki-sizegrip`
  - `.miki-columnview`, `.miki-column`, `.miki-column-item`
  - `.miki-btngroup` and `.miki-btngroup .miki-btn`

### 5. Update exports
- Update `mikiui/widgets/__init__.py` to export `MikiMenu`, `MikiSizeGrip`, `MikiColumnView`, `MikiButtonGroup`.
- No change to `mikiui/components/__init__.py` (ListView stays, just upgraded).

### 6. Update tests
- Update `tests/test_components.py`: fix `ListView` test expectations for new HTML structure.
- Update `tests/test_advanced_widgets.py`: fix `ToolboxPanel` test expectations for new structure.
- Add tests for `MikiMenu`, `MikiSizeGrip`, `MikiColumnView`, `MikiButtonGroup`.

## Open Questions / Risks
- **ToolboxPanel backward compatibility**: The existing API takes `dict[str, list[Any]]`. The new API takes `dict[str, Any]`. If we change the type signature, existing code using lists will still work (lists are `Any`), but the rendering will change from `Ul/Li` to `Div`. This is a breaking visual change. Mitigation: document it as an upgrade.
- **ListView migration**: Existing code using `ListView` may depend on `Li`/`role="option"` semantics. Changing to `Div`/`role="listitem"` is a minor breaking change for accessibility tree but shouldn't break visual rendering.
- **CSS specificity**: The existing `.miki-dial` CSS is for the rich rotary widget. The proposal's simpler dial is intentionally NOT added to avoid conflict.

## Validation
- Run `pytest tests/test_components.py tests/test_advanced_widgets.py` after changes.
- Verify rendered HTML for each new/upgraded widget.
- Ensure ARIA roles and keyboard navigation attributes are present.
