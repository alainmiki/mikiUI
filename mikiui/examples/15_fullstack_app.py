"""15_fullstack_app.py — Project management system (fullstack).

Combines authentication, dashboard, project DataGrid, KanbanBoard,
real-time notifications, team chat, file upload, activity log,
settings with theme switching, and responsive sidebar.

Run with: mikiui dev --app mikiui.examples.15_fullstack_app:app
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any

from fastapi.responses import RedirectResponse

from mikiui import (
    Chart,
    Div,
    Footer,
    H1,
    H2,
    H3,
    MikiApp,
    P,
    register_theme,
)
from mikiui.components import Button, Form, Input, Label, Navbar, Select, Textarea
from mikiui.components.form import Option
from mikiui.themes import Theme
from mikiui.widgets import (
    Avatar,
    Badge,
    Card,
    ChatUI,
    DataGrid,
    FilePicker,
    FormWizard,
    KanbanBoard,
    LogViewer,
    LoginForm,
    NotificationPanel,
    ProgressDialog,
    SidePanel,
    SplitView,
    StatusBar,
    TabbedPanel,
    TerminalWidget,
    Toolbar,
)
from mikiui.widgets.layout_widgets import Hero
from mikiui_app_plugins import APIPlugin, NotificationPlugin, SessionPlugin
from mikiui.validation import Email, Length, Required
from mikiui.validation.form import Field, FormValidator

app = MikiApp(title="MikiUI Projects", lang="en")
app.use(SessionPlugin(secret_key="fullstack-secret-key-32", session_lifetime=timedelta(hours=2)))
app.use(NotificationPlugin(max_per_user=50, default_duration=4000))
app.use(APIPlugin(title="Projects API", version="1.0.0"))

register_theme(Theme(
    name="midnight",
    source="custom",
    framework="css",
    variables={"--miki-bg": "#0f172a", "--miki-fg": "#e2e8f0", "--miki-accent": "#38bdf8"},
    extra_classes=["miki-theme-midnight"],
))
app.set_theme("midnight")

form_validator = FormValidator(
    Field("name", Required(), Length(min=2, max=60)),
    Field("email", Required(), Email()),
    Field("role", Required()),
)

USERS = {
    "alice": {"name": "Alice Kim", "avatar": "https://i.pravatar.cc/150?u=alice", "role": "admin"},
    "marcus": {"name": "Marcus Chen", "avatar": "https://i.pravatar.cc/150?u=marcus", "role": "user"},
    "elena": {"name": "Elena Rossi", "avatar": "https://i.pravatar.cc/150?u=elena", "role": "user"},
}

PROJECTS = [
    {"id": 1, "name": "Website Redesign", "status": "In Progress", "owner": "Alice Kim", "progress": 72},
    {"id": 2, "name": "Mobile App v2", "status": "Planning", "owner": "Marcus Chen", "progress": 15},
    {"id": 3, "name": "API Migration", "status": "In Review", "owner": "Elena Rossi", "progress": 90},
    {"id": 4, "name": "Security Audit", "status": "In Progress", "owner": "Alice Kim", "progress": 45},
    {"id": 5, "name": "Analytics Dashboard", "status": "Done", "owner": "Marcus Chen", "progress": 100},
]

TASKS = {
    "Todo": ["Write RFC for caching", "Evaluate Redis vs Valkey", "Migrate documentation"],
    "In Progress": ["Refactor auth service", "Fix pagination bug", "Update CI pipeline"],
    "Review": ["Security patch #4021", "API rate-limit refactor"],
    "Done": ["Setup Docker Compose", "Write onboarding guide"],
}

ACTIVITY_LOG = [
    ("info", "Alice Kim deployed Website Redesign to staging."),
    ("info", "Marcus Chen merged PR #512: refactor auth middleware."),
    ("warning", "High memory usage on worker-3: 87%."),
    ("error", "Job #1024 failed: timeout after 30s."),
    ("debug", "Cache hit ratio: 94.2%."),
    ("info", "Elena Rossi created a new project: Analytics Dashboard."),
]


def _is_auth(ctx) -> tuple[bool, str | None]:
    token = ctx.request.cookies.get("mikiui_session") if ctx.request else None
    if token and app.validate_session(token):
        return True, app.validate_session(token)
    return False, None


def _layout(body: Div, user: str | None = None) -> Div:
    nav_links = [("Dashboard", "/dashboard"), ("Projects", "/projects"), ("Tasks", "/tasks"), ("Chat", "/chat"), ("Settings", "/settings")]
    if user:
        nav_links.append(("Logout", "/logout"))
    return Div(
        Toolbar(
            Button("New Project", variant="primary", class_="mr-2"),
            Button("Invite", variant="secondary", class_="mr-2"),
            Button("Notifications", variant="secondary"),
            class_="px-4 py-2 border-b border-slate-200 bg-white",
        ),
        Div(
            SidePanel(
                "left",
                Div(
                    P("Dashboard", class_="font-semibold text-slate-700"),
                    P("Projects"),
                    P("Tasks"),
                    P("Team"),
                    P("Chat"),
                    P("Settings"),
                    class_="space-y-3",
                ),
                header="Navigation",
                collapsible=True,
            ),
            Div(
                body,
                class_="flex-1 min-w-0 p-6 overflow-y-auto",
            ),
            class_="flex min-h-[calc(100vh-48px)]",
        ),
        StatusBar(
            Div(P("v1.0.0"), class_="text-xs"),
            Div(P("CPU 28%"), class_="text-xs"),
            Div(P("MEM 54%"), class_="text-xs"),
            class_="px-4 py-1 bg-slate-800 text-slate-300 text-xs border-t border-slate-700",
        ),
        class_="max-w-7xl mx-auto",
    )


@app.route("/")
def home(ctx) -> Div:
    authenticated, user = _is_auth(ctx)
    if authenticated:
        return RedirectResponse("/dashboard", status_code=303)
    return Div(
        Navbar(brand="Projects", links=[("Sign In", "/login")], dark=True),
        Div(
            Hero(
                "MikiUI Projects",
                subtitle="Plan, track, and ship software with your team.",
                image="https://picsum.photos/seed/projects/1200/500",
                align="center",
            ),
            Div(
                Div(
                    Card(
                        LoginForm(action="/login"),
                        class_="max-w-md mx-auto p-8 -mt-8 relative z-10",
                    ),
                    Div(id="login-result", class_="mt-6 max-w-md mx-auto"),
                    class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
                ),
                class_="relative",
            ),
            Footer(copyright="© 2026 MikiUI Projects"),
            class_="min-h-screen bg-slate-50",
        ),
    )


@app.route("/login", methods=["GET", "POST"])
async def login(ctx) -> Div:
    if ctx.request.method == "POST":
        data = await ctx.form()
        errors = form_validator.validate(data)
        if errors:
            return Div(
                P("Invalid submission.", class_="text-red-600 font-semibold"),
                *[P(f"{k}: {v}", class_="text-red-500") for k, v in errors.items()],
                class_="p-4 bg-red-50 border border-red-200 rounded-lg",
            )
        username = data.get("name", "user").lower().replace(" ", "")
        token = app.create_session(username, role="user")
        response = RedirectResponse("/dashboard", status_code=303)
        app.set_session_cookie(response, token)
        return response

    return Div(
        Navbar(brand="Projects", links=[("Home", "/")], dark=True),
        Div(
            Hero("Sign In", subtitle="Access your workspace.", align="center"),
            Div(
                Card(LoginForm(action="/login"), class_="max-w-md mx-auto p-8 -mt-8 relative z-10"),
                class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
            ),
            Footer(copyright="© 2026 MikiUI Projects"),
            class_="min-h-screen bg-slate-50",
        ),
    )


@app.route("/dashboard", requires_auth=True)
def dashboard(ctx) -> Div:
    authenticated, user = _is_auth(ctx)
    if not authenticated:
        return RedirectResponse("/", status_code=303)
    profile = USERS.get(user, {"name": user, "avatar": "", "role": "user"})

    body = Div(
        Div(
            Card(
                H2(f"Welcome, {profile['name']}", class_="text-2xl font-bold text-slate-900"),
                P("Here's what's happening across your projects today.", class_="text-slate-600"),
                class_="p-6",
            ),
            class_="max-w-4xl mb-8",
        ),
        Div(
            Card(H1("Revenue"), P("$91.2k"), class_="p-5"),
            Card(H1("Active Tasks"), P("18"), class_="p-5"),
            Card(H1("Team Members"), P("5"), class_="p-5"),
            Card(Badge("Online", variant="success"), P("System Status", class_="text-sm text-slate-500 mt-1"), class_="p-5"),
            class_="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8",
        ),
        Div(
            Div(
                H2("Revenue Trend", class_="text-lg font-bold text-slate-800 mb-3"),
                Chart([4200, 5100, 4800, 6200, 5900, 7100, 6800, 7500, 8200, 7800, 8500, 9100], kind="line", width=600, height=180),
                class_="bg-white p-5 rounded-xl shadow-sm border border-slate-100 mb-6",
            ),
            Div(
                H2("Recent Activity", class_="text-lg font-bold text-slate-800 mb-3"),
                LogViewer(lines=[f"{level}: {msg}" for level, msg in ACTIVITY_LOG], line_numbers=True),
                class_="bg-white p-5 rounded-xl shadow-sm border border-slate-100",
            ),
            class_="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8",
        ),
        Div(
            NotificationPanel(),
            class_="max-w-2xl",
        ),
        class_="space-y-6",
    )
    return _layout(body, user)


@app.route("/projects", requires_auth=True)
def projects(ctx) -> Div:
    authenticated, user = _is_auth(ctx)
    if not authenticated:
        return RedirectResponse("/", status_code=303)

    rows = [[str(p["id"]), p["name"], p["status"], p["owner"], f"{p['progress']}%"] for p in PROJECTS]

    body = Div(
        H1("Projects", class_="text-3xl font-bold text-slate-900 mb-2"),
        P("Manage and track all active projects.", class_="text-slate-600 mb-8"),
        DataGrid(
            columns=["ID", "Name", "Status", "Owner", "Progress"],
            rows=rows,
            sortable=True,
            filterable=True,
            pagination=True,
            page_size=5,
        ),
        class_="space-y-6",
    )
    return _layout(body, user)


@app.route("/tasks", requires_auth=True)
def tasks(ctx) -> Div:
    authenticated, user = _is_auth(ctx)
    if not authenticated:
        return RedirectResponse("/", status_code=303)

    body = Div(
        H1("Task Board", class_="text-3xl font-bold text-slate-900 mb-2"),
        P("Drag tasks between columns to update status.", class_="text-slate-600 mb-8"),
        KanbanBoard(TASKS),
        class_="space-y-6",
    )
    return _layout(body, user)


@app.route("/chat", requires_auth=True)
def chat(ctx) -> Div:
    authenticated, user = _is_auth(ctx)
    if not authenticated:
        return RedirectResponse("/", status_code=303)

    body = Div(
        H1("Team Chat", class_="text-3xl font-bold text-slate-900 mb-2"),
        P("Real-time messaging for the team.", class_="text-slate-600 mb-8"),
        ChatUI([
            {"role": "bot", "text": "Welcome to the team chat."},
            {"role": "user", "text": "Who is working on the API migration?"},
            {"role": "bot", "text": "Elena is currently handling the API migration."},
            {"role": "user", "text": "Great, I will sync with her after lunch."},
        ]),
        class_="space-y-6",
    )
    return _layout(body, user)


@app.route("/settings", requires_auth=True)
def settings(ctx) -> Div:
    authenticated, user = _is_auth(ctx)
    if not authenticated:
        return RedirectResponse("/", status_code=303)

    body = Div(
        H1("Settings", class_="text-3xl font-bold text-slate-900 mb-2"),
        P("Customize your workspace preferences.", class_="text-slate-600 mb-8"),
        Div(
            Div(
                H2("Appearance", class_="text-xl font-bold text-slate-800 mb-4"),
                Div(
                    Label("Theme", for_="theme", class_="block text-sm font-medium text-slate-700 mb-1"),
                    Select(
                        Option("Midnight", value="midnight", selected=True),
                        Option("Light", value="light"),
                        Option("Dark", value="dark"),
                        Option("Dracula", value="dracula"),
                        id="theme",
                        name="theme",
                        class_="w-full rounded border-slate-300",
                    ),
                    Button("Save Theme", variant="primary", hx_post="/api/settings/theme", hx_target="#theme-result", hx_swap="innerHTML"),
                    Div(id="theme-result", class_="mt-3"),
                    class_="max-w-sm",
                ),
                class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100 mb-6",
            ),
            Div(
                H2("Uploads", class_="text-xl font-bold text-slate-800 mb-4"),
                FilePicker(name="attachments", accept=".pdf,.doc,.docx,.png,.jpg", label="Drop files here or click to browse..."),
                class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100 mb-6",
            ),
            Div(
                H2("Notifications", class_="text-xl font-bold text-slate-800 mb-4"),
                Div(
                    Label("Default Duration", for_="duration", class_="block text-sm font-medium text-slate-700 mb-1"),
                    Select(
                        Option("3 seconds", value="3000"),
                        Option("5 seconds", value="5000", selected=True),
                        Option("10 seconds", value="10000"),
                        id="duration",
                        name="duration",
                        class_="w-full rounded border-slate-300",
                    ),
                    class_="max-w-sm",
                ),
                class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100",
            ),
            class_="max-w-3xl space-y-6",
        ),
        class_="space-y-6",
    )
    return _layout(body, user)


@app.route("/api/settings/theme", methods=["POST"])
async def save_theme(ctx) -> Div:
    data = await ctx.form()
    theme_name = data.get("theme", "midnight")
    try:
        app.set_theme(theme_name)
        return Div(P(f"Theme switched to {theme_name}.", class_="text-emerald-600"), id="theme-result")
    except Exception as exc:
        return Div(P(f"Error: {exc}", class_="text-red-600"), id="theme-result")


@app.route("/logout", methods=["GET", "POST"])
def logout() -> Div:
    response = RedirectResponse("/", status_code=303)
    app.delete_session_cookie(response)
    return response


if __name__ == "__main__":
    app.run()
