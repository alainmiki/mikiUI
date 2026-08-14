# Agent Instructions - MikiUI

## Purpose
This file guides AI agents and developers collaborating on MikiUI to ensure consistency, completeness, and quality.

## Responsibilities
- Follow the project plan and PRD strictly.
- Ensure all modules (App, Engine, Runtime, Router, Build, Plugin, Media) are implemented.
- Maintain beginner-friendly APIs while supporting advanced features.
- Guarantee full component and widget coverage (all HTML elements + PyQt + VS UI parity).
- Optimize builds for small file sizes.
- Handle FastAPI packaging in both fullstack and separate modes.

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
- **Always commit after every change** with clear commit messages.
- **Use local tools** for builds, testing, and packaging (no hidden external dependencies).
- **Follow modular architecture**: components → widgets → app → engine → runtime.
- **Security-first**: validate plugins, sandbox runtime, enforce safe defaults.
- **Performance-first**: optimize rendering, minimize bundle size.
- **Documentation-first**: every module must have clear docs and examples.
- **Testing-first**: write unit/integration tests before merging.
- **Accessibility-first**: ARIA roles, keyboard navigation, screen reader support.
- **Internationalization-first**: ensure i18n hooks are available in all components.
- **Version control discipline**: feature branches, pull requests, code reviews, CI/CD pipelines.

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
- **Build system**: supports fullstack (FastAPI serves frontend + backend) and separate mode.  
- **Agents**: must follow architecture strictly, handle events/callbacks, and commit after every change.  
- always review before committing

always use software engineering and programming best practices.