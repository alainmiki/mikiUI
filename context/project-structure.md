# MikiUI Project Structure

## Root Layout
mikiui/
├── app/                # User-facing API (routing, state, plugin use)
│   ├── init.py
│   ├── routes.py
│   ├── state.py
│   └── plugins.py
│
├── components/         # Core components (all HTML elements)
│   ├── init.py
│   ├── button.py
│   ├── input.py
│   ├── form.py
│   ├── table.py
│   ├── dialog.py
│   ├── modal.py
│   ├── tabs.py
│   ├── slider.py
│   ├── progressbar.py
│   ├── treeview.py
│   ├── listview.py
│   ├── calendar.py
│   ├── filepicker.py
│   └── chart.py
│
├── widgets/            # High-level composite widgets
│   ├── init.py
│   ├── datagrid.py
│   ├── mediaplayer.py
│   ├── dashboard.py
│   ├── kanbanboard.py
│   ├── chatui.py
│   ├── ide_editor.py
│   ├── dockable_panel.py
│   ├── splitview.py
│   ├── property_grid.py
│   ├── inspector_panel.py
│   └── terminal_widget.py
│
├── engine/             # Core rendering and diffing
│   ├── init.py
│   ├── renderer.py
│   ├── diff.py
│   └── updater.py
│
├── runtime/            # JS runtime (HTMX + Alpine)
│   ├── init.py
│   ├── htmx_runtime.js
│   ├── alpine_runtime.js
│   └── runtime_loader.py
│
├── router/             # Multi-page, SPA, PWA routing
│   ├── init.py
│   ├── router.py
│   └── middleware.py
│
├── build/              # Packaging system
│   ├── init.py
│   ├── web_build.py
│   ├── desktop_build.py
│   └── optimizer.py
│
├── media/              # Streaming, recording, EQ
│   ├── init.py
│   ├── streaming.py
│   ├── recorder.py
│   ├── equalizer.py
│   └── filters.py
│
├── backend/            # FastAPI backend
│   ├── init.py
│   ├── server.py
│   ├── websocket.py
│   ├── sse.py
│   └── api_routes.py
│
├── cli/                # CLI tooling
│   ├── init.py
│   ├── commands.py
│   └── scaffolding.py
│
├── tests/              # Testing utilities
│   ├── init.py
│   ├── test_components.py
│   ├── test_widgets.py
│   ├── test_engine.py
│   └── test_router.py
│
├── docs/               # Documentation
│   ├── getting_started.md
│   ├── api_reference.md
│   └── contributing.md
│
└── package.json        # For frontend runtime bundling (Vite/Webpack)


---

## Web vs Desktop Differences

- **File Handling**  
  - Web → `components/filepicker.py` (browser upload/download).  
  - Desktop → `widgets/dockable_panel.py` + OS file system APIs.

- **Notifications**  
  - Web → Service worker + browser notifications.  
  - Desktop → Native system notifications via `desktop_build.py`.

- **Clipboard**  
  - Web → Browser clipboard API.  
  - Desktop → OS clipboard integration.

- **Plugins**  
  - Web → JS plugins loaded via `runtime_loader.py`.  
  - Desktop → Python plugins loaded via `app/plugins.py`.

---

## Notes
- **Components**: cover all HTML elements (including `<dialog>`, `<form>`, `<table>`, etc.).  
- **Widgets**: composite, high-level UI (DataGrid, MediaPlayer, DockablePanel, IDE Editor).  
- **Backend**: FastAPI for routes, WebSocket, SSE.  
- **Build system**: supports fullstack (FastAPI serves frontend + backend) and separate mode.  
- **Agents**: must follow architecture strictly, handle events/callbacks, and commit after every change.  
