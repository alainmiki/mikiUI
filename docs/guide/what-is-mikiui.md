# What is MikiUI?

MikiUI is a Python-first UI framework that lets you build user interfaces as standalone desktop apps or websites. It uses FastAPI for the backend, HTMX + Alpine.js for the frontend runtime, and a Python component API that maps directly to HTML elements.

## Key Concepts

- **Components**: Python classes that map 1:1 to HTML elements (`Button`, `Input`, `Div`, `Table`, etc.)
- **Widgets**: High-level composite UI built from components (`DataGrid`, `ChatUI`, `IDEEditor`, etc.)
- **Routes**: Python functions decorated with `@app.route("/path")` that return component trees
- **Themes**: CSS-based theming system with 4 built-in themes and custom theme support
- **Plugins**: Extend MikiUI with custom components, widgets, themes, and backend routes

## When to Use MikiUI

- You want to build UIs **in Python** without touching JavaScript for logic.
- You need **both web and desktop** deployment from the same codebase.
- You prefer **server-side rendering** with optimistic client-side updates.
- You want a **beginner-friendly API** that is still powerful enough for advanced use cases (plugins, custom components, widgets).
