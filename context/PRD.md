
---

## 📄 PRD.md (updated with components/widgets)

```markdown
# Product Requirements Document (PRD) - MikiUI

## Overview
MikiUI is a Python framework for building user interfaces that can run as standalone GUIs or websites. It targets both beginners and advanced developers, offering simplicity, extensibility, and performance.

## Goals
- Beginner-friendly API.
- Optimistic UI with partial updates.
- Lightweight builds.
- Plugin ecosystem.
- Full component/widget coverage (PyQt + VS UI parity).
- Advanced web features (streaming, recording, EQ, SSE).
- PWA support.
- Flexible packaging: fullstack (FastAPI serves frontend + backend) or separate (frontend + backend decoupled).

## Functional Requirements
- **Routing**: Multi-page, SPA, PWA-ready.
- **State Management**: Beginner (`app.state`) + advanced reactive store.
- **Components**: All HTML elements (Button, Input, Form, Table, Dialog, Modal, Tabs, Slider, ProgressBar, TreeView, ListView, Calendar, FilePicker, Chart).
- **Widgets**: DataGrid, MediaPlayer, Dashboard, KanbanBoard, ChatUI, IDE-like editor, Advanced Panels (dockable/floating panels, split views, property grids).
- **Plugin System**: `app.use(plugin)`, manifest schema, AST vetting, import allow-list, marketplace integration.
- **Media Module**: Streaming, recording, EQ.
- **Build System**: Packaging for web/desktop, optimized bundles, fullstack/separate modes. Desktop builds auto-install PyInstaller and produce native executables/bundles (`.app` on macOS, `.exe` on Windows, ELF on Linux).
- **Developer Tooling**: CLI, hot reload, DevTools, testing utilities.
- **Global Features**: i18n, accessibility, SSR, data fetching.
- **Desktop APIs**: Tray, notifications, file system, clipboard.

## Non-Functional Requirements
- Performance: Optimized rendering and build size.
- Accessibility: ARIA roles, keyboard navigation.
- Extensibility: Plugin system and marketplace with security-first design (manifest validation, AST vetting, import allow-list).
- Reliability: Stable runtime and engine.
- Usability: Simple API, clear documentation.
