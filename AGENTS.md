# AGENTS.md — MikiUI

Python-first UI framework (`mikiui`) that renders UIs as standalone desktops or websites.
**Greenfield:** no package code or tests exist yet. `pyproject.toml` targets **Python ≥3.14** with no dependencies declared yet.

## Source of truth
- `agent.md` — full rulebook and guardrails (read it).
- `context/` — the spec. Read everything in it before design/coding work:
  - `context/plan.md` (vision, tech stack, CLI examples)
  - `context/PRD.md` (functional/non-functional requirements)
  - `context/project-structure.md` (intended package layout + web/desktop differences)
  - `context/components.md` (component & widget catalog; the coverage target)
- `README.md` is currently empty — do not rely on it.

## Tech stack (verified in `pyproject`/`context/plan.md`)
- Backend: FastAPI (routes, WebSocket, SSE).
- Frontend runtime: HTMX + Alpine.js (partial/optimistic updates; full HTML only on route change).
- Styling: TailwindCSS default, Bootstrap optional.
- CLI: Click/Typer (`mikiui new | dev | build`).
- Testing: Pytest (unit) + Playwright (browser). **Not scaffolded yet** — put tests under `tests/` per `project-structure.md`.
- Frontend bundling: a `package.json` (Vite/Webpack) lives at package root.
- Optional DB: PostgreSQL/Redis for state persistence.

## Architecture (planned in `context/project-structure.md`, not yet created)
Build order / dependency direction: `components` → `widgets` → `app` → `engine` → `runtime` → `router` → `build` → `media`; `backend` (FastAPI) and `cli` are siblings.
- `components/` = Python classes mapping 1:1 to HTML elements (incl. `<dialog>`, `<form>`, `<table>`).
- `widgets/` = composite high-level UI built from components (DataGrid, MediaPlayer, DockablePanel, IDE editor, etc.).
- `engine/` = rendering + diffing + optimistic updater.
- Two build modes: **fullstack** (FastAPI serves frontend+backend) and **separate**; targets **web** and **desktop**.

## Workflow rules (honor these)
- **Use subagents and available tools to move faster** — delegate independent research/build tasks rather than doing everything inline.
- **Always review changes before committing.** Inspect diffs/status first; only then commit.
- Commit discipline: clear messages; the repo expects frequent, small, review-first commits. Use feature branches + PRs.
- Work from the spec in `context/` and keep every module documented (doc-first).
- **GIT SAFETY — NEVER run these without explicit user approval:** `git reset`, `git revert`, `git checkout --`, `git clean`, `git stash`, `git push --force`, `git rebase`, `git commit --amend`, or any command that rewrites history or discards uncommitted work. If you need to undo something, **ask the user first**. Always inspect `git status` and `git diff` before any git operation.

## Conventions that differ from defaults
- **Accessibility is mandatory**: ARIA roles, keyboard nav, screen-reader support on every component/widget.
- **i18n hooks required** in all components/widgets.
- **Security-first** for the plugin system: validate plugins and sandbox the runtime.
- **Performance-first**: minimize bundle size; full HTML only on route changes, partial updates otherwise.
- Beginner-friendly API is a hard requirement (usable with ~2 weeks of Python).
