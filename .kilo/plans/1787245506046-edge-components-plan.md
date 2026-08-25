# Component System Hardening Plan — MikiUI

## Goal
Make the existing `mikiui/components/` and `mikiui/widgets/` systems production-ready for mobile (Capacitor + optional Chaquopy), web, and desktop from one Python codebase. Fix known bugs, close mobile-first gaps, and unify CSS so Tailwind v4 scanning works. Target: publish-ready by tomorrow evening.

---

## 1. Audit Summary

### Confirmed blocking issues
1. **CSS architecture is split.** `miki_components.css` is the `@layer components` source, but 90% of component styles live in `miki.css`. Tailwind scans both, but the layer is incomplete.
2. **Navbar toggle mismatch.** `onclick` toggles `active`; CSS expects `.open`.
3. **Drawer side animations broken.** JS only toggles `.miki-drawer-open`; CSS requires `.miki-drawer-{side}-open`.
4. **Button.toggle icon swap broken.** Icon is plain text; JS looks for `.miki-toggle-icon`.
5. **Carousel has no touch/swipe.** Autoplay doesn't pause on touch.
6. **Rail is hover-only.** No `:active`/touch states or safe-area insets.
7. **Badge has no core component.** Only a widget in `advanced_widgets.py`; CSS not in `miki_components.css`.
8. **SplitView touch drag fragile.** Splitter lacks `touch-action: none` during drag.
9. **Accordion missing keyboard nav and CSS.**
10. **Icon SVG accessibility gap.** Missing `focusable="false"` and consistent `aria-hidden`.

### Design constraints (already in edge-components plan; apply here too)
- One codebase, zero platform branches.
- Static-export safe: no server round-trips for initial render.
- Theming via `var(--miki-*)` only.
- Mobile-first: min touch target 44×44px; no hover-only core behavior.
- Capacitor-aware: `env(safe-area-inset-*)`, no `alert()`, no listening sockets.
- Chaquopy-safe: no `localhost` assumptions in JS.
- Progressive enhancement: works without Alpine.js; `data-miki-*` drives `miki_ui.js`.
- Accessibility + i18n mandatory.
- No coupling to runtime/build from component code.

---

## 2. CSS Architecture Fix

**File:** `mikiui/runtime/miki_components.css`

Move ALL component CSS classes from `miki.css` into `miki_components.css` under `@layer components { ... }`.

Classes to migrate:
- `.miki-scrollpanel`, `.miki-stackedpanel`, `.miki-stack-tabs`, `.miki-stack-pages`
- `.miki-columnview`, `.miki-column`, `.miki-column-item`
- `.miki-drawer`, `.miki-drawer-overlay`, `.miki-drawer-panel`, `.miki-drawer-open`, `.miki-drawer-{side}`, `.miki-drawer-{size}`, `.miki-drawer-header`, `.miki-drawer-title`, `.miki-drawer-close`, `.miki-drawer-body`
- `.miki-splitview`, `.miki-split-pane`, `.miki-splitter`, `.miki-split-h`, `.miki-split-v`
- `.miki-rail`, `.miki-rail-{side}`, `.miki-rail-item`, `.miki-rail-label`
- `.miki-navbar`, `.miki-navbar-sticky`, `.miki-navbar-dark`, `.miki-navbar-brand`, `.miki-navbar-links`, `.miki-navbar-link`, `.miki-navbar-toggle`, `.miki-navbar-right`
- `.miki-badge`, `.miki-badge-success`, `.miki-badge-warning`, `.miki-badge-error`, `.miki-badge-info`
- `.miki-carousel`, `.miki-carousel-container`, `.miki-carousel-slide`, `.miki-carousel-slide-hidden`, `.miki-carousel-image`, `.miki-carousel-dots`, `.miki-carousel-dot`, `.miki-carousel-dot-active`, `.miki-carousel-prev`, `.miki-carousel-next`
- `.miki-toggle-btn`, `.miki-toggle-btn-wrapper`, `.miki-toggle-icon`
- `.miki-accordion`, `.miki-accordion > details`, `.miki-accordion summary`
- `.miki-toolbar`, `.miki-statusbar`, `.miki-menubar`, `.miki-menu`, `.miki-menu-item`, `.miki-splash`, `.miki-messagebox`, `.miki-messagebox-body`
- `.miki-toolbox`, `.miki-toolbox-section`, `.miki-toolbox-header`, `.miki-toolbox-body`
- `.miki-btngroup`, `.miki-btn-block`, `.miki-btn-xs`, `.miki-btn-sm`, `.miki-btn-lg`, `.miki-btn-xl`
- `.miki-sizegrip`, `.miki-columnview`, `.miki-mdiarea`, `.miki-mdi-subwindow`

**File:** `mikiui/runtime/miki.css`

Replace component styles with:
```css
@import url("./miki_components.css");

/* Base/reset utilities only — no component styles here */
```

Verify `styling/tailwind.py` content paths still include both:
- `mikiui/runtime/miki.css`
- `mikiui/runtime/miki_components.css`

---

## 3. Component Fixes

### 3.1 Navbar (`components/navbar.py`)
- Change `onclick` to toggle `open` instead of `active`.
- Add `padding-top: env(safe-area-inset-top, 0px)` on mobile.
- Ensure `.miki-navbar-toggle` and `.miki-navbar-link` min-height/min-width = 44px.
- Add `touch-action: manipulation` to interactive elements.

### 3.2 Drawer (`widgets/navigation_widgets.py` + `miki_ui.js`)
- Update `mikiDrawer.open/close/toggle` to toggle BOTH `.miki-drawer-open` AND `.miki-drawer-{side}-open`.
- Add `padding: env(safe-area-inset-{side}, 0px)` to `.miki-drawer-panel`.
- Ensure close button min-touch-target = 44×44px.
- Ensure overlay `pointer-events: none` when closed, `auto` when open.

### 3.3 Button.toggle() (`components/button.py`)
- Wrap icon in `<span class="miki-toggle-icon">` so JS can swap it.
- Add `touch-action: manipulation` and `:active` scale feedback via CSS.

### 3.4 Accordion (`components/accordion.py` + `miki_ui.js`)
- Add `data-miki-accordion="true"` to container.
- Add `mikiAccordion` JS for arrow-key/Home/End navigation.
- Add `.miki-accordion` CSS to `miki_components.css`.
- Ensure `summary` min-height = 44px on mobile.

### 3.5 Carousel (`widgets/advanced_widgets.py` + `miki_ui.js`)
- Add `touchstart`/`touchend` swipe handlers.
- Pause autoplay on touchstart, resume on touchend.
- Ensure prev/next buttons min-touch-target = 44×44px.
- Add `touch-action: pan-y` to carousel container.

### 3.6 Rail (`widgets/navigation_widgets.py`)
- Replace hover-only states with `:hover, :active, .miki-rail-item-active`.
- Add safe-area insets to rail container.
- Ensure `.miki-rail-item` min-width/min-height = 48px.
- Add `touch-action: manipulation`.

### 3.7 SplitView (`widgets/splitview.py`)
- Add `touch-action: none` to `.miki-splitter` during drag.
- Add `@media (pointer: coarse)` to increase splitter width on touch devices.

### 3.8 Badge (`components/badge.py` + `widgets/advanced_widgets.py`)
- Add lightweight `Badge` core component in `components/badge.py`.
- Keep widget `Badge` as alias/re-export.
- Ensure `.miki-badge` CSS is in `miki_components.css`.

### 3.9 Icon (`widgets/icon.py`)
- Ensure inline SVG has `aria-hidden="true"` and `focusable="false"`.
- Re-export `Icon`/`IconSet` from `components/__init__.py`.

---

## 4. New Edge Components to Add

Add these only after the CSS consolidation and existing fixes are complete.

| Component | File | JS Required |
|-----------|------|-------------|
| `Column` | `components/column.py` | No |
| `Row` | `components/row.py` | No |
| `Stack` | `components/stack.py` | No |
| `Spacer` | `components/spacer.py` | No |
| `Divider` | `components/divider.py` | No |
| `Shape` | `components/shape.py` | No |
| `ActivityIndicator` | `components/activityindicator.py` | No |
| `Pressable` | `components/pressable.py` | Yes |
| `SafeAreaView` | `components/safeareaview.py` | No |
| `BottomNavigation` | `components/bottomnavigation.py` | Yes (HTMX-driven state) |
| `BottomSheet` | `components/bottomsheet.py` | Yes (JS-only state) |
| `FloatingActionButton` | `components/floatingactionbutton.py` | No |
| `Chip` | `components/chip.py` | Yes |
| `LazyGrid` | `components/lazygrid.py` | Yes |
| `VirtualList` | `components/virtuallist.py` | Yes |
| `ScrollView` | `components/scrollview.py` | No |

---

## 5. JS Runtime Additions

**File:** `mikiui/runtime/miki_ui.js`

### Fixes
- **Drawer:** toggle side-specific open classes.
- **Carousel:** add touch swipe handlers.
- **Accordion:** add keyboard nav module.

### New modules
- `mikiBottomSheet` — open/close, backdrop, ESC, drag handle.
- `mikiBottomNav` — visual active-state + keyboard arrows only; state is HTMX-driven.
- `mikiPressable` — pointer feedback.
- `mikiChip` — Space/Enter toggle.
- `mikiLazyGrid` — IntersectionObserver hydration.
- `mikiVirtualList` — scroll windowing.

All re-init on `miki:swapped` and `htmx:afterSwap`.

---

## 6. Theming Integration

All new and redesigned CSS uses existing custom properties. No hard-coded colors.

| Variable | Used by |
|----------|---------|
| `--miki-accent` | FAB, active chip/nav, spinner |
| `--miki-fg` | FAB icon, chip text |
| `--miki-surface` | Bottom sheet, nav, chip selected |
| `--miki-surface-hover` | Chip, rail, accordion |
| `--miki-border` | Divider, chip, spinner, handle |
| `--miki-radius` | Shape, chip, sheet, FAB |
| `--miki-radius-lg` | Sheet panel |
| `--miki-shadow` / `--miki-shadow-lg` | FAB, sheet |
| `--miki-text-muted` | Inactive nav |
| `--miki-transition` | Pressable, drawer |
| `--miki-success` / `--miki-warning` / `--miki-error` | Badge variants |

Tailwind v4 + DaisyUI v5 config in `styling/tailwind.py` scans `miki.css`, which will import `miki_components.css`. After consolidation, all classes are auto-discovered.

---

## 7. Mobile / Capacitor / Chaquopy

### Capacitor cloud
- Fixed-position elements (FAB, BottomNav, BottomSheet) work in WebView.
- `env(safe-area-inset-*)` passes through.
- Touch targets ≥ 44×44px enforced.
- No hover-only core behavior.
- Carousel supports touch swipe.

### Capacitor on-device (Android + Chaquopy)
- Static export pre-renders HTML. Components must not require server round-trips for initial render.
- LazyGrid/VirtualList degrade gracefully in static export; JS hydrates in WebView.
- API calls go through `MikiBackend.call()`; no direct `fetch("http://localhost")`.
- No `ServerSocket`, `ServerSocketChannel`, or `socket.bind` in generated Kotlin.

### Desktop (pywebview)
- Fixed-position elements work inside pywebview.
- BottomSheet behaves as a modal.
- VirtualList/LazyGrid reduce DOM size.

---

## 8. Accessibility & i18n

Every hardened component must:
- Set `role` appropriately.
- Include `aria-label`, `aria-selected`, `aria-expanded`, `aria-modal`, `aria-orientation`, `aria-live` where applicable.
- Support keyboard interaction for all interactive widgets.
- Expose i18n via `from ..engine import _` and `data-i18n`.

---

## 9. Implementation Order

1. **CSS consolidation** — move all component styles from `miki.css` to `miki_components.css`; slim `miki.css`.
2. **Fix existing components** — Navbar, Drawer, Button.toggle, Accordion, Carousel, Rail, SplitView, Badge, Icon.
3. **Add new edge components** — Column, Row, Stack, Spacer, Divider, Shape, ActivityIndicator, Pressable, SafeAreaView, BottomNavigation, BottomSheet, FloatingActionButton, Chip, LazyGrid, VirtualList, ScrollView.
4. **JS runtime updates** — fix drawer/carousel/accordion; add new modules.
5. **Re-exports** — update `components/__init__.py`.
6. **Validation** — unit tests, regression tests, CSS audit, static export smoke test, accessibility audit.

---

## 10. Validation

- **Unit tests:** render each component, assert tag, role, class names, ARIA, i18n.
- **Regression tests:** verify existing components render correctly after fixes.
- **CSS audit:** grep emitted `miki-` classes, verify each has a rule in `miki_components.css`.
- **Static export smoke test:** build app with all components, verify HTML, verify no server round-trips for initial render.
- **Playwright (web/desktop):** drawer side animations, carousel swipe, bottom sheet, FAB, virtual list scroll, chip toggle.
- **Accessibility audit:** axe-core on each component page.

---

## 11. Out of Scope

Same as edge-components plan §13:
- Dynamic VirtualList heights
- Shape image backgrounds
- BottomNavigation drag-to-reorder
- LazyGrid server-side rendering
- Desktop native file dialogs (handled by pywebview bridge)
