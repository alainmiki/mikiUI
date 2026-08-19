# Agent Instructions - MikiUI

## Source of Truth (Read Order)

1. **`context/plan.md`** — vision, tech stack, CLI examples
2. **`context/PRD.md`** — functional and non-functional requirements
3. **`context/project-structure.md`** — intended package layout
4. **`context/components.md`** — component and widget catalog
5. **`context/mobile.md`** — mobile build plan (DESIGN DOC ONLY — see Phase Lock below)

## Purpose

This file guides AI agents and developers collaborating on MikiUI to ensure consistency, completeness, and quality.

## Responsibilities

- Follow the project plan and PRD strictly.
- Ensure all modules (App, Engine, Runtime, Router, Build, Plugin, Media) are implemented.
- Maintain beginner-friendly APIs while supporting advanced features.
- Guarantee full component and widget coverage (all HTML elements + PyQt + VS UI parity).
- Optimize builds for small file sizes.
- Handle FastAPI packaging in both fullstack and separate modes.

## Phase Lock — Mobile Work Is Gated

**Mobile implementation is frozen until web and desktop are mature.**

Before touching ANY file in `mikiui/build/mobile_*`, `mikiui/runtime/*bridge.js`, or `mikiui/app/mobile/`, verify ALL of the following:

- [ ] All base HTML components are implemented and tested
- [ ] All advanced widgets are mature (DataGrid, MediaPlayer, DockablePanel, IDE Editor)
- [ ] `mikiui build --target web` is stable and production-ready
- [ ] `mikiui build --target desktop` is stable and production-ready
- [ ] Plugin system is security-reviewed and marketplace is functional
- [ ] CI/CD passes on Linux, Windows, and macOS
- [ ] No critical bugs open against web/desktop builds

If any item is unchecked, **stop and report the blocker.** Do not begin mobile implementation.

After mobile work is unblocked, follow the implementation order in `context/mobile.md` Section 18.

## Development Guidelines

- Use Python for core framework logic.
- Use FastAPI for backend routes and WebSocket/SSE.
- Use HTMX + Alpine.js for runtime interactivity.
- TailwindCSS as default styling, Bootstrap optional.
- Ensure accessibility and internationalization.
- Provide testing utilities and DevTools integration.
- Implement CLI commands (`new`, `dev`, `build`).
- Support hot reload during development.
- Include advanced panels/widgets (dockable panels, split views, property grids, IDE-like editors).

## Guardrails & Best Practices

### Version Control
- **Always commit after every change** with clear commit messages.
- **Use feature branches + PRs** for all non-trivial work.
- **Review diffs before committing.** Stage only intended files.
- **Never commit secrets** (API keys, tokens, credentials).

### Architecture
- **Follow modular architecture**: components → widgets → app → engine → runtime.
- **One Python codebase, three deployment wrappers.** Never add platform-specific Python code for mobile.
- **Static export is the source of truth for frontend builds.** Mobile wraps the web build output.

### Security
- **Security-first**: validate plugins, sandbox runtime, enforce safe defaults.
- **No listening sockets on Android.** The on-device backend uses the Chaquopy bridge (direct function calls). If generated Kotlin/Java code contains `ServerSocket`, `ServerSocketChannel`, or `socket.bind`, the build must fail.
- **iOS on-device mode is a build error.** If `target` includes `ios` and `backend == "ondevice"`, fail fast with a clear message before generating files.
- **Capacitor plugins are opt-in.** No plugin is enabled unless explicitly declared in `MobileConfig.plugins` or required by a registered plugin's `capabilities`.
- **HTTPS enforced for cloud mode.** The generated Capacitor config must not set `cleartext: true` unless `backend == "ondevice"`.
- **Plugin capabilities are declarative.** A Python plugin's `capabilities` list auto-maps to Capacitor plugins. No silent permission grants.

### Performance
- **Performance-first**: optimize rendering, minimize bundle size.
- **APK size budgets:** cloud mode < 12MB, on-device mode < 40MB.
- **Bridge latency target:** < 5ms p99 for on-device Chaquopy calls.
- **Static export must handle 100+ routes** without errors or excessive build time.

### Documentation
- **Documentation-first**: every module must have clear docs and examples.
- **Read everything in the `context/` folder before designing or coding.**
- Every component, widget, panel, utility, and file must be documented.

### Testing
- **Testing-first**: write unit/integration tests before merging.
- Mobile tests must cover: cloud build structure, on-device build structure, iOS rejection of on-device mode, plugin permission mapping, bridge latency.

### Accessibility and i18n
- **Accessibility-first**: ARIA roles, keyboard navigation, screen reader support.
- **Internationalization-first**: ensure i18n hooks are available in all components.

### CI/CD
- CI must pass on Linux, Windows, and macOS.
- Mobile smoke tests must run on every PR that touches mobile-related files.
- Store compliance checks (no listening sockets, correct permissions) must be automated.

## Collaboration Rules

- Document all modules and APIs clearly.
- Maintain modular, extensible architecture.
- Ensure plugin system is secure and flexible.
- Prioritize performance and usability.
- Align with roadmap milestones.

always read everything in the context folder.
every component,widget/panel,utility and files should be documented

## Notes
- **Components**: cover all HTML elements (including `<dialog>`, `<form>`, `<table>`, etc.).  
- **Widgets**: composite, high-level UI (DataGrid, MediaPlayer, DockablePanel, IDE Editor).  
- **Backend**: FastAPI for routes, WebSocket, SSE.  
- **Build system**: supports fullstack (FastAPI serves frontend + backend), separate mode, and (eventually) mobile.  
- **Agents**: must follow architecture strictly, handle events/callbacks, and commit after every change.  
- Always review before committing.
- Always use software engineering and programming best practices.
- **Mobile is a deployment target, not a feature.** It ships when the product is already shippable on web and desktop.
