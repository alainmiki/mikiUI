# Changelog

All notable changes to MikiUI are documented in this file.

## [Unreleased]

### Build System Hardening & Desktop Packaging Improvements

#### Web Build

- **`build_web()` report now includes `robots` and `404`**: `robots.txt` and
  `404.html` are generated automatically for every web build.
- **Sitemap accuracy**: `_render_sitemap()` now receives original route paths
  instead of rendered filenames, so paths with underscores (e.g.
  `/user_profile`) are preserved correctly instead of being corrupted to
  `/user/profile`.
- **Configurable URL scheme**: sitemap uses `app.url_scheme` instead of
  hardcoded `http://`, defaulting to `https`.
- **Server script respects app host/port**: `server.py` now reads `host` and
  `port` from the app instance instead of hardcoding `127.0.0.1:8000`.
- **Tailwind build error handling**: `_build_tailwind()` raises
  `RuntimeError` with actionable guidance when the Tailwind CLI fails,
  instead of silently falling back.
- **Parameterized route sitemap support**: `_render_parameterized_routes()`
  now returns resolved route paths so parameterized examples appear in the
  sitemap.

#### Desktop Build

- **Auto-install PyInstaller**: `_ensure_pyinstaller()` attempts
  `pip install pyinstaller` when PyInstaller is missing, so users do not
  need to manually install it.
- **Executable output**: `_write_pyinstaller_spec()` now returns
  `(spec_path, error)` and runs the build. The desktop report includes
  `bundle` (path to the final executable/app bundle) and `warning` on
  partial failure.
- **macOS `.app` bundle**: `_create_platform_bundle()` wraps the PyInstaller
  executable in a proper macOS `.app` bundle with `Info.plist`, icon
  embedding, and bundled web assets.
- **Socket leak fix**: `_start_server()` closes the pre-bound socket on
  bind failure instead of leaking it.
- **pywebview detection fix**: `_has_pywebview()` and `_import_webview()`
  now check the module-level `_webview` variable instead of `sys.modules`,
  fixing false negatives when pywebview is imported under a different name.
- **File watcher debounce**: `_watch_and_restart()` adds a 0.3 s debounce
  to prevent excessive rebuilds on rapid file changes.

#### Tailwind + DaisyUI Production Fixes

- **Local JIT config is now passed to Tailwind**: `_build_tailwind()` writes
  the generated config to a temp file and passes `-c <config>` to
  `npx tailwindcss`, ensuring DaisyUI plugin and theme bridges are applied.
- **Tailwind output path corrected**: Compiled CSS is written to
  `themes/tailwind.css`, matching what the HTML shell and renderer expect.
- **`miki.css` is never overridden**: Base widget/component CSS is always
  copied and preserved, even when Tailwind is active.
- **DaisyUI plugin resolution**: `_resolve_daisyui_plugin_path()` finds
  `daisyui.min.js` from the bundled runtime or `node_modules`; missing plugin
  now falls back with a clear warning instead of crashing.
- **CDN mode DaisyUI uses theme colors**: `_tailwind_config_script()` reads
  actual theme colors via `daisyui_config()` instead of hardcoded blue values.
- **CSP allows Tailwind CDN dynamic styles**: `'unsafe-inline'` is added to
  `style-src` in CDN mode so `@tailwindcss/browser@4` can inject utility CSS.
- **404 page respects framework**: 404 fallback now loads Tailwind/DaisyUI or
  plain `miki.css` based on the app's framework selection.

#### Tests

- **`tests/test_web_build.py`**: New test module covering `build_web()`,
  `_render_sitemap()`, `_write_robots_txt()`, `_write_404_page()`, and
  report fields for fullstack/separate modes.
- **`tests/test_desktop.py`**: Added tests for `_ensure_pyinstaller()`,
  `build_desktop()` report fields, `_create_platform_bundle()` on macOS,
  and updated `test_run_native_reload_calls_restart_server` to patch
  `db._webview` directly.
- **`tests/test_themes.py`**: Updated `test_tailwind_config_generation` to
  mock DaisyUI plugin resolution.

#### CLI

- **`mikiui build --target desktop`** now prints the bundle path and any
  PyInstaller warnings after the build completes.
- **Avoided double Tailwind build**: CLI now passes `skip_tailwind=True` to
  `build_web()` after pre-building CSS.

## [0.3.0] — 2026-09-09

### Build System Hardening & Desktop Packaging Improvements

#### Web Build

- **`build_web()` report now includes `robots` and `404`**: `robots.txt` and
  `404.html` are generated automatically for every web build.
- **Sitemap accuracy**: `_render_sitemap()` now receives original route paths
  instead of rendered filenames, so paths with underscores (e.g.
  `/user_profile`) are preserved correctly instead of being corrupted to
  `/user/profile`.
- **Configurable URL scheme**: sitemap uses `app.url_scheme` instead of
  hardcoded `http://`, defaulting to `https`.
- **Server script respects app host/port**: `server.py` now reads `host` and
  `port` from the app instance instead of hardcoding `127.0.0.1:8000`.
- **Tailwind build error handling**: `_build_tailwind()` raises
  `RuntimeError` with actionable guidance when the Tailwind CLI fails,
  instead of silently falling back.
- **Parameterized route sitemap support**: `_render_parameterized_routes()`
  now returns resolved route paths so parameterized examples appear in the
  sitemap.

#### Desktop Build

- **Auto-install PyInstaller**: `_ensure_pyinstaller()` attempts
  `pip install pyinstaller` when PyInstaller is missing, so users do not
  need to manually install it.
- **Executable output**: `_write_pyinstaller_spec()` now returns
  `(spec_path, error)` and runs the build. The desktop report includes
  `bundle` (path to the final executable/app bundle) and `warning` on
  partial failure.
- **macOS `.app` bundle**: `_create_platform_bundle()` wraps the PyInstaller
  executable in a proper macOS `.app` bundle with `Info.plist`, icon
  embedding, and bundled web assets.
- **Socket leak fix**: `_start_server()` closes the pre-bound socket on
  bind failure instead of leaking it.
- **pywebview detection fix**: `_has_pywebview()` and `_import_webview()`
  now check the module-level `_webview` variable instead of `sys.modules`,
  fixing false negatives when pywebview is imported under a different name.
- **File watcher debounce**: `_watch_and_restart()` adds a 0.3 s debounce
  to prevent excessive rebuilds on rapid file changes.

#### Tests

- **`tests/test_web_build.py`**: New test module covering `build_web()`,
  `_render_sitemap()`, `_write_robots_txt()`, `_write_404_page()`, and
  report fields for fullstack/separate modes.
- **`tests/test_desktop.py`**: Added tests for `_ensure_pyinstaller()`,
  `build_desktop()` report fields, `_create_platform_bundle()` on macOS,
  and updated `test_run_native_reload_calls_restart_server` to patch
  `db._webview` directly.

#### CLI

- **`mikiui build --target desktop`** now prints the bundle path and any
  PyInstaller warnings after the build completes.

## [Unreleased] — 2026-08-29

### Hardening: Routing, Security, Build, Accessibility

#### Routing & Path Parameters

- **Type-coerced path parameters**: `{param:int}`, `{param:float}`, `{param:uuid}`, `{param:path}` with validation and clear error messages
- **Route method merging**: Same path with different methods (e.g., GET + POST) merges into one RouteDef instead of overwriting
- **Pattern-matched route lookup**: `get_route('/users/42')` now matches `/users/{user_id}` via `match_route()`
- **New HTTP convenience methods**: `put()`, `patch()`, `delete()`, `head()`, `options()` — all accept OpenAPI metadata
- **Route OpenAPI metadata**: `summary`, `description`, `tags` parameters on all route decorators; auto-extracted from docstrings
- **Route group auth propagation**: Group-level `auth()` applies to all routes unless explicitly overridden
- **Route group rate limiting**: Group `rate_limit()` configs collected and applied automatically in `server.py`

#### Security

- **CSRF protection by default**: `create_app()` enables CSRF with double-submit cookie pattern; opt-out via `enable_csrf=False`
- **New CSRF helpers**: `generate_csrf_token()`, `default_get_session_token()`, `default_validate_csrf()`, `apply_csrf_middleware()`
- **Auth middleware browser detection**: Returns `RedirectResponse` for browser navigations, JSON 401 for API requests
- **Bridge action validation**: `validate_action()` for untrusted input; bridge attr values escaped
- **Request ID middleware**: `X-Request-ID` header generated/propagated for distributed tracing
- **Compression middleware**: `apply_compression_middleware()` using gzip

#### Accessibility & Correctness

- **SVG camelCase attributes**: `viewBox` and other SVG attributes preserved correctly
- **Tabs ARIA fix**: Removed duplicate `role="tablist"` on outer container
- **i18n wrapping**: Menu aria-label and other hardcoded strings wrapped in `_()`
- **Ctx.form() rewrite**: Correct multi-value query parameter handling

#### Build System

- **Recursive asset copying**: Widget JS/CSS files in subdirectories now copied to build output
- **Windows path separators**: Asset manifest uses forward slashes for URL correctness
- **Fixed Windows .bat launcher**: Proper batch syntax with separate Python launcher script
- **File watcher exclusions**: Excludes dist/, build/, node_modules/, __pycache__/ to prevent infinite rebuilds

#### API Documentation

- **RouteDef OpenAPI fields**: `summary`, `description`, `tags` carried through to FastAPI schema
- **APIPlugin enhanced**: Path param support, ctx passing, proper error handling, security schemes in OpenAPI schema
- **OpenAPI security schemes**: `bearerAuth` and `cookieAuth` documented in schema

#### WebSocket

- **WebSocketAuthHelper**: Integrates WS connections with app auth strategies (session, JWT, api_key)
- **Room/channel support**: `join_room()`, `leave_room()`, `broadcast_to_room()`, `broadcast_to_user()`
- **Connection info**: `get_connection_info()`, `get_user_rooms()`, `get_room_count()`
- **Automatic cleanup**: Rooms cleaned up on disconnect

#### Developer Experience

- **MikiApp.test_client()**: One-line test client creation: `client = app.test_client()`
- **match_route() utility**: Standalone function for pattern-matched route lookup

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

### Static Files & Build System

#### Production-Ready Static File Serving

- **`mikiui/app/static_assets.py`**:
  - Added `CachingStaticFiles` class (moved out of `backend/server.py`) with
    conditional cache headers: `immutable, max-age=31536000` for content-hashed
    filenames (e.g. `app.abc123.css`), `max-age=3600` for all others.
  - `register_plugin_assets()` collision warning message refactored for readability.
  - `get_versioned_asset_url()` signature split across multiple lines for PEP 8.
  - Exports `CachingStaticFiles` for use by backend and tests.

- **`mikiui/backend/server.py`**:
  - **P0**: Auto-mounts the project's `static/` directory at `/static` if present,
    fixing the broken `mikiui new plain` scaffold.
  - **P0**: `build_web()` now copies `mikiui/components/*/static/` and
    `mikiui/widgets/*/static/` into `dist/_miki/`, making static-exported sites
    self-contained.
  - **P1**: New `_register_app_static_roots()` scans the app's `WidgetRegistry`
    and `ThemeRegistry` for module/css paths and auto-registers their parent
    directories, so custom themes, widgets, components, and plugins get their
    `static/` folders discovered and mounted automatically.
  - Removed inline `_CachingStaticFiles` class definition; uses the shared
    `CachingStaticFiles` from `static_assets.py` instead.
  - Cleaned up unused imports (`StaticFiles`, `JSONResponse`, `MikiUIError`,
    `NotFoundError`, `error_response`, `CSRFMiddleware`, `RateLimitMiddleware`,
    `AuthRequirement`, `resolve_auth_requirement`).

- **`mikiui/app/app.py`**:
  - **P1**: Added `MikiApp.mount_static(url_path, directory)` — public API to
    mount arbitrary static directories without dropping to raw FastAPI.
  - **P1**: Added `MikiApp.asset_url(package_type, package_name, filename)` —
    resolves `/_miki/...` URLs for components, widgets, plugins, and themes.
  - Added `_static_mounts: list[tuple[str, str]]` to track user-registered mounts.
  - Fixed `TYPE_CHECKING` guard for `Router` import to satisfy type checkers.

- **`mikiui/build/web_build.py`**:
  - **P0**: Static export now copies component/widget/plugin/theme static assets
    into `dist/_miki/`, including all `.css` theme files from `runtime/themes/`.
  - **P1**: Component/widget/theme assets are included in `manifest.json` with
    content hashes for cache busting.
  - **P3**: Added `_render_parameterized_routes()` and `_load_route_manifest()`
    to support `route-manifest.json` — a JSON file mapping parameterized routes
    to example path values for static export.
  - **Mobile compatibility**: Changed runtime asset copying from a hardcoded
    `_RUNTIME_ASSETS` list to a directory scan, so new bridge JS files
    (`backend_bridge.js`, `capacitor_bridge.js`, etc.) are automatically
    included when added to `mikiui/runtime/`.
  - Removed unused `config_path` variable in `_build_tailwind`.

- **`mikiui/router/middleware.py`**:
  - **P2**: Dev-mode CSP now strips `'unsafe-inline'` from `style-src` when a
    nonce is present, replacing it with `'nonce-<value>'`. The renderer adds
    `nonce` attributes to inline `<style>` tags for CSS variables.
  - Added missing `typing.Any` import.

- **`mikiui/engine/renderer.py`**:
  - **P2**: `render_page()` and `_theme_styles()` now accept `csp_nonce` and
    apply it to inline `<style>` tags for CSS variables.
  - Added `framework`, `style_mode`, `daisyui` parameters to `_theme_styles()`
    and `render_page()` so Tailwind/DaisyUI configuration flows from the app.
  - Fixed base CSS logic: Tailwind framework skips loading `miki.css` to avoid
    duplication; plain CSS and color themes load it normally.
  - Removed unused `_RUNTIME_DIR` import from `themes`.

- **`mikiui/build/__init__.py`**:
  - **P3**: Now imports `optimize` from `optimizer.py` (real CSS/JS minification)
    instead of the inline blank-line-stripping stub.

- **`package.json`**:
  - Removed orphaned Vite scripts and `vite` devDependency.
  - Added accurate Tailwind CLI scripts (`tailwind:build`, `tailwind:watch`).
  - Updated `tailwindcss` to `^4.1.7` and `daisyui` to `^5.0.0`.

#### Verification

- All 134 existing tests pass.
- `ruff check` passes on all changed files.
- `mypy` shows no new errors introduced by these changes.
- Integration tests confirm: `mount_static()`, `asset_url()`, project `static/`
  auto-mount, component asset copying in web build, and custom package static
  directory discovery all work correctly.
