# Changelog

All notable changes to MikiUI are documented in this file.

## [Unreleased] — 2026-08-19

### Plugin System: Security, Sandboxing, Marketplace

#### New Files

- **`mikiui/app/plugin_security.py`**: New module providing:
  - `PluginManifest` dataclass for structured plugin metadata (name, version, capabilities, dependencies, checksum, etc.)
  - `PluginSecurityConfig` policy dataclass (`allow_untrusted`, `allowed_imports`, `blocked_imports`, `blocked_capabilities`, `vet_ast`, `max_plugin_size_bytes`)
  - `PluginValidator` class that runs identity, capability, AST vetting, and import scanning checks
  - `PluginSecurityViolation` exception raised when a plugin violates policy
  - `validate_plugin()` and `load_manifest()` convenience helpers
  - Default safe import list including stdlib, `mikiui`, `mikiui_app_plugins`, built-in plugin modules (`session`, `notifications`, `api`, `demo`), and common web deps (`fastapi`, `starlette`, `pydantic`, etc.)

- **`mikiui/app/marketplace.py`**: New marketplace client providing:
  - `PluginInfo` dataclass for marketplace plugin metadata
  - `MarketplaceSource` abstract base class
  - `DirectoryIndexSource` for local directory-based indexes
  - `PyPIIndexSource` for remote PyPI-like JSON APIs
  - `PluginMarketplace` client with `search()`, `install()`, and `install_all()` methods
  - Security validation is enforced before any plugin is loaded or registered

- **`tests/test_plugin_security.py`**: 18 regression tests covering manifest loading, AST vetting, import scanning, capability blocking, and validator integration.

- **`tests/test_marketplace.py`**: 8 tests covering directory indexing, search, fetch, install, validation rejection, and bulk install.

#### Plugin Discovery Fixes

- **`mikiui/app/plugin_discovery.py`**:
  - `discover_from_directory` now uses package-qualified imports for built-in plugins, fixing silent failures for plugins using relative imports or dataclasses
  - `_import_module_rel` sanitizes module names and registers them in `sys.modules` so dataclass field introspection works
  - `_get_module_metadata` now checks `attr.__module__ == module.__name__` to avoid falsely claiming imported classes as local plugins
  - `auto_load` now runs security validation before `app.use()`, respecting the app's `PluginSecurityConfig`
  - Added `_load_manifest_for_class` and `_resolve_source_for_class` helpers for AST vetting in `auto_load`
  - Added `allow_untrusted` enforcement: plugins from `directory`/`marketplace` sources are skipped when `allow_untrusted=False` (default)
  - `auto_load` now accepts an explicit `security_config` parameter that overrides the app's default policy

#### Plugin Base Class Updates

- **`mikiui/app/plugins.py`**:
  - Added `capabilities: list[str] = []` attribute to `Plugin` base class
  - Added `manifest: PluginManifest | None = None` attribute to `Plugin` base class
  - Fixed circular import with `plugin_security.py` using `from __future__ import annotations`

#### App Integration

- **`mikiui/app/app.py`**:
  - `use()` now calls `PluginValidator.validate_plugin()` before `plugin.register(self)` so even manually instantiated plugins are checked
  - Added `set_plugin_security_config(config)` and `get_plugin_security_config()` methods
  - Added `_resolve_plugin_source()` helper for AST vetting
  - Defensive `getattr(plugin, "depends_on", [])` to handle non-Plugin instances gracefully
  - `get_backend_routes()`, `get_middleware_classes()`, and `get_plugin_assets()` now return cached lists collected at `use()` time, eliminating duplicate route registration
  - Fixed missing `os` import used in `_resolve_plugin_source`

#### Bug Fixes

- **`mikiui/app/app.py`**: Fixed `RouteGroupBuilder` NameError by importing `RouteGroup` and `RouteGroupBuilder` from `..router.group`
- **`mikiui/backend/server.py`**: Fixed undefined `runtime_dir` NameError in `_RUNTIME_DIR` definition
- **`mikiui/backend/api_routes.py`: Fixed `Request` import placement that caused NameError when module was imported
- **`mikiui/engine/renderer.py`**: Fixed unterminated f-string literal on line 135

#### Documentation

- **`docs/plugins.md`**: Added sections for Plugin Manifest, Security & Sandboxing, and Marketplace
- **`docs/security.md`**: Added §11 Plugin Security covering `PluginValidator`, `PluginSecurityConfig`, default safe imports, built-in plugin allow-list, and violation flow
- **`context/PRD.md`**: Updated Functional and Non-Functional Requirements to include manifest schema, AST vetting, import allow-list, and marketplace integration

### Component Fixes & Hardening

#### Critical Fixes

- **Chart** (`components/chart.py`): Fixed SVG being rendered as escaped text by
  introducing the `RawHtml` node type in `mikiui.engine.dom`. Chart's `_bars()`,
  `_line()`, and `_pie()` methods now use `RawHtml` to emit inline SVG elements
  without HTML escaping.

- **Heading** (`components/base.py`): Fixed `Heading("Title", level=2)` rendering
  as `<div>` instead of `<h2>`. Removed `self.tag = self.__class__.tag` overwrite
  in `Component.__init__` that clobbered dynamic tag assignment from subclasses.

- **Textarea** (`components/input.py`): Fixed duplicate `class` attributes caused
  by mixing `"class"` and `"class_"` keys. All components now use `"class_"` consistently.

- **SplitView Name Collision** (`components/splitview/splitview.py`): Renamed the
  editor-area component from `SplitView` to `EditorArea` to resolve the collision
  with `widgets/splitview.py`'s layout splitter widget.

- **MenuItem** (`components/menuitem.py`): Replaced deprecated `<menuitem>` HTML
  element with `<button type="button" role="menuitem">` for browser compatibility.

- **Select** (`components/input.py`): `multiple` attribute is now properly preserved
  instead of being silently discarded by `attrs.pop("multiple", False)`.

- **Dead code removal** (`components/form.py`): Removed duplicate `Select` and
  `Option` classes that were shadowing the working versions in `input.py`.

#### Accessibility

- **Table/Th** (`components/table.py`): Added default `scope="col"` attribute for
  screen readers to associate headers with cells.

- **Breadcrumbs** (`components/breadcrumbs.py`): Added `aria-current="page"` to
  the last breadcrumb item (current page indicator).

- **Dialog** (`components/dialog.py`): Fixed fragile string-based `has_close`
  detection; removed redundant `role="button"` on `<button>` elements.

- **Progress** (`components/progressbar.py`): Added `aria-valuenow`,
  `aria-valuemin`, `aria-valuemax` attributes for screen reader compatibility.

- **Input/Textarea** (`components/input.py`): Added `aria-required` when `required`
  is set; added `aria-invalid` when `state="invalid"`.

- **Tabs** (`components/tabs.py`): Fixed closeable tabs to use `<button>` instead of
  `<div>` for proper keyboard focus and semantics.

- **Button.toggle** (`components/button.py`): Added `pressed` kwarg; `aria-pressed`
  and `data-miki-state` now reflect the initial state instead of being hardcoded to
  `"true"`.

#### Catalog Aliases

Added backward-compatible aliases so short names match the component catalog in
`context/components.md`:

- `Paragraph = P`, `Image = Img`, `Anchor = A`, `Preformatted = Pre`
- `Emphasis = Em`, `Abbreviation = Abbr`, `Citation = Cite`
- `Keyboard = Kbd`, `Variable = Var`, `Sample = Samp`
- `SVG = Svg`, `ProgressBar = Progress`
- `UnorderedList = Ul`, `OrderedList = Ol`, `ListItem = Li`
- `DescriptionList = Dl`, `DescriptionTerm = Dt`, `DescriptionDetail = Dd`

All aliases are exported from `mikiui.components` and re-exported from `mikiui`.

#### Engine

- **`RawHtml`** (`mikiui/engine/dom.py`): New node type for trusted, unescaped HTML
  content. Handles SVG inline elements and other trusted markup. Exported from
  `mikiui.engine` and `mikiui`.

- **`I18nText.format()`** (`mikiui/engine/dom.py`): Added `format(**kwargs)` method
  to resolve translations and apply `str.format()` for dynamic content like
  `"Page {n} of {total}"`.

#### Desktop Icon

- **`run_desktop`** (`mikiui/build/desktop_build.py`): Fixed desktop window icon
  not showing — icon is now properly passed to `webview.start(icon=...)`.
  Added `_default_desktop_icon()` which returns `.ico` on Windows, `.png` on other
  platforms. Fallback chain: `icon` param → `miki_app.desktop_icon` → `_default_desktop_icon()`.

- **`mikiui-icon.ico`**: Converted from a PNG file renamed as `.ico` to a proper
  multi-resolution ICO file (16–256px).

### Plugin Security Fixes

- **`plugin_security.py`**: Added `"__future__"` to `_DEFAULT_SAFE_IMPORTS`
  allowlist (built-in plugins use `from __future__ import annotations`).

- **`plugin_discovery.py`**: Fixed relative import resolution in
  `_extract_imports` — `from .sibling import X` now resolves to the parent package
  before validation. Fixed missing imports (`PluginManifest`,
  `PluginSecurityViolation`, `load_manifest`).

- **`plugins.py`**: Fixed circular import between `plugins.py` and
  `plugin_security.py` using `TYPE_CHECKING` guard and string annotation for the
  `manifest` field.

### Styling/Tailwind

- **`build/tailwind/__init__.py`**: Removed broken import from nonexistent
  `mikiui.build.styling.tailwind` module.

- **`styling/tailwind.py`**: Fixed missing `tailwind_config` import; fixed
  incorrect relative import `..styling.system`.

### Documentation

- **`docs/api-reference.md`**: Updated to document `RawHtml`, `Heading` component,
  `Button.toggle` `pressed` kwarg, catalog aliases, corrected `Chart` signature
  (`series`/`kind` instead of `data`/`type`), and `EditorArea` vs `SplitView`
  distinction.

- **`docs/widgets.md`**: Updated `Chart` section with correct API; added
  `EditorArea` note in `SplitView` section.

- **`docs/plugins.md`**: Added "Auto-load" and "Import allowlist" sections
  documenting `auto_load()` and the `__future__` entry in the default safe imports.

- **`AUDIT_REPORT.md`**: Complete audit report with all 18 issues documented,
  status tracking (P0–P3), and a detailed changelog of all fixes.
