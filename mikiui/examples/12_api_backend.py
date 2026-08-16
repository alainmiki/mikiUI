"""12_api_backend.py — REST API showcase with full CRUD.

Demonstrates APIPlugin with task management endpoints, in-memory storage,
and Swagger docs at /docs.

Run with: mikiui dev --app mikiui.examples.12_api_backend:app
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from mikiui import Div, H1, H2, MikiApp, P
from mikiui.components import Button, Navbar
from mikiui.widgets import Card, DataGrid, LogViewer
from mikiui.widgets.layout_widgets import Hero
from mikiui_app_plugins import APIPlugin, SessionPlugin
from datetime import timedelta

app = MikiApp(title="Task API", lang="en")
app.use(SessionPlugin(secret_key="api-demo-secret-key-32", session_lifetime=timedelta(hours=1)))
app.use(APIPlugin(title="Task Management API", version="1.0.0"))

_TASKS: dict[int, dict[str, Any]] = {
    1: {"id": 1, "title": "Design API schema", "status": "done", "priority": "high", "assignee": "Elena", "created_at": "2026-08-01T10:00:00Z"},
    2: {"id": 2, "title": "Implement auth middleware", "status": "in_progress", "priority": "high", "assignee": "Marcus", "created_at": "2026-08-03T14:30:00Z"},
    3: {"id": 3, "title": "Write integration tests", "status": "todo", "priority": "medium", "assignee": "Aisha", "created_at": "2026-08-05T09:15:00Z"},
    4: {"id": 4, "title": "Setup CI/CD pipeline", "status": "in_progress", "priority": "medium", "assignee": "Tomás", "created_at": "2026-08-06T16:45:00Z"},
    5: {"id": 5, "title": "Update documentation", "status": "todo", "priority": "low", "assignee": "Grace", "created_at": "2026-08-07T11:20:00Z"},
}
_NEXT_ID = 6


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


@app.route("/")
def home() -> Div:
    return Div(
        Navbar(brand="Task API", links=[("Docs", "/docs"), ("Tasks", "/tasks"), ("API", "/api/tasks")], dark=True),
        Div(
            Hero(
                "Task Management API",
                subtitle="A production-ready REST API with CRUD operations, built on FastAPI and MikiUI.",
                image="https://picsum.photos/seed/api/1200/450",
                align="center",
            ),
            Div(
                Div(
                    H2("Quick Start", class_="text-2xl font-bold text-slate-800 mb-4"),
                    Card(
                        Div(
                            P("Open the Swagger UI to explore endpoints interactively.", class_="text-slate-600 mb-4"),
                            Div(
                                Button("Open /docs", variant="primary", class_="mr-3"),
                                Button("Open /redoc", variant="secondary", class_="mr-3"),
                                Button("View Tasks", variant="secondary", hx_get="/api/tasks", hx_target="#api-preview", hx_swap="innerHTML"),
                                class_="flex flex-wrap gap-2",
                            ),
                            Div(id="api-preview", class_="mt-6"),
                            class_="p-6",
                        ),
                        class_="max-w-3xl mx-auto",
                    ),
                    class_="max-w-6xl mx-auto py-12",
                ),
            ),
            class_="relative -mt-16 z-10",
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/tasks")
def tasks_page() -> Div:
    rows = []
    for t in _TASKS.values():
        rows.append([
            str(t["id"]),
            t["title"],
            t["status"].replace("_", " ").title(),
            t["priority"].title(),
            t["assignee"],
            t["created_at"][:10],
        ])

    return Div(
        Navbar(brand="Task API", links=[("Home", "/"), ("Docs", "/docs")]),
        Div(
            H1("Tasks", class_="text-3xl font-bold text-slate-900 mb-2"),
            P("Browse tasks through the DataGrid or call the API directly.", class_="text-slate-600 mb-8"),
            Div(
                DataGrid(
                    columns=["ID", "Title", "Status", "Priority", "Assignee", "Created"],
                    rows=rows,
                    sortable=True,
                    filterable=True,
                    pagination=True,
                    page_size=5,
                    search=True,
                    search_fields=["Title", "Assignee"],
                ),
                class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100",
            ),
            Div(
                H2("API Endpoints", class_="text-2xl font-bold text-slate-800 mb-4"),
                Div(
                    Card(P("GET /api/tasks", class_="font-mono text-sm text-indigo-600"), P("List all tasks."), class_="p-4 mb-3"),
                    Card(P("GET /api/tasks/{id}", class_="font-mono text-sm text-indigo-600"), P("Retrieve a single task."), class_="p-4 mb-3"),
                    Card(P("POST /api/tasks", class_="font-mono text-sm text-indigo-600"), P("Create a new task."), class_="p-4 mb-3"),
                    Card(P("PATCH /api/tasks/{id}", class_="font-mono text-sm text-indigo-600"), P("Update a task."), class_="p-4 mb-3"),
                    Card(P("DELETE /api/tasks/{id}", class_="font-mono text-sm text-indigo-600"), P("Delete a task."), class_="p-4"),
                    class_="max-w-2xl space-y-3",
                ),
                class_="max-w-6xl mx-auto mt-12",
            ),
            class_="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12",
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/api/tasks")
def list_tasks() -> list[dict[str, Any]]:
    return list(_TASKS.values())


@app.route("/api/tasks/create", methods=["POST"])
def create_task() -> dict[str, Any]:
    global _NEXT_ID
    _NEXT_ID += 1
    return {"id": _NEXT_ID, "title": "New task", "status": "todo", "priority": "medium", "assignee": "Unassigned", "created_at": "2026-08-16T01:00:00Z"}


@app.route("/api/tasks/{task_id}")
def get_task(task_id: int) -> dict[str, Any]:
    task = _TASKS.get(task_id)
    if not task:
        return {"error": "Task not found"}, 404
    return task


@app.route("/api/tasks/{task_id}/update", methods=["PATCH"])
def update_task(task_id: int) -> dict[str, Any]:
    task = _TASKS.get(task_id)
    if not task:
        return {"error": "Task not found"}, 404
    return {"updated": task}


@app.route("/api/tasks/{task_id}/delete", methods=["DELETE"])
def delete_task(task_id: int) -> dict[str, Any]:
    if task_id not in _TASKS:
        return {"error": "Task not found"}, 404
    del _TASKS[task_id]
    return {"deleted": task_id}


if __name__ == "__main__":
    app.run()
