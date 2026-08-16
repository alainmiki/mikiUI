"""10_notifications.py — Notification center and toast system.

Demonstrates toast notifications, a notification bell dropdown,
real-time notification feed, settings, and clear/mark-read actions.

Run with: mikiui dev --app mikiui.examples.10_notifications:app
"""

from __future__ import annotations

from mikiui import Div, H1, H2, H3, MikiApp, P
from mikiui.components import Button, Footer, Navbar, Select
from mikiui.widgets import Avatar, Badge, Card
from mikiui.widgets.layout_widgets import Hero
from mikiui_app_plugins import NotificationPlugin, SessionPlugin
from datetime import timedelta

app = MikiApp(title="Notification Center", lang="en")
app.use(SessionPlugin(secret_key="notif-portal-secret-key-32", session_lifetime=timedelta(hours=2)))
notifications = NotificationPlugin(default_duration=5000)
app.use(notifications)


def _toast(level: str, message: str) -> Div:
    colors = {
        "info": "bg-sky-50 border-sky-200 text-sky-800",
        "success": "bg-emerald-50 border-emerald-200 text-emerald-800",
        "warning": "bg-amber-50 border-amber-200 text-amber-800",
        "error": "bg-red-50 border-red-200 text-red-800",
    }
    icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
    return Div(
        Div(icons.get(level, "ℹ️"), class_="text-lg"),
        P(message, class_="text-sm font-medium"),
        class_=f"flex items-start gap-3 p-4 rounded-lg border shadow-sm {colors.get(level, colors['info'])}",
    )


@app.route("/")
def home(ctx) -> Div:
    token = ctx.request.cookies.get("mikiui_session") if ctx.request else None
    user = app.validate_session(token) if token else "guest"

    return Div(
        Navbar(
            brand="Notifications",
            links=[
                ("Home", "/"),
                ("Center", "/center"),
                ("Settings", "/settings"),
            ],
            dark=True,
        ),
        Div(
            Hero("Notification Center", subtitle="Stay on top of alerts, updates, and mentions.", align="center"),
            Div(
                Div(
                    H2("Trigger Toasts", class_="text-xl font-bold text-slate-800 mb-4"),
                    Div(
                        Button("Info", variant="secondary", class_="mr-2", onclick="notify('info')"),
                        Button("Success", variant="primary", class_="mr-2", onclick="notify('success')"),
                        Button("Warning", variant="secondary", class_="mr-2 text-amber-700", onclick="notify('warning')"),
                        Button("Error", variant="secondary", class_="mr-2 text-red-700", onclick="notify('error')"),
                        class_="flex flex-wrap gap-2",
                    ),
                    P("Click a button to enqueue a toast. Toasts auto-dismiss after the configured duration.", class_="text-sm text-slate-500 mt-3"),
                    Div(id="toast-stack", class_="fixed top-4 right-4 z-50 flex flex-col gap-3 w-80"),
                    class_="max-w-2xl",
                ),
                Div(
                    H2("Notification Feed", class_="text-xl font-bold text-slate-800 mb-4"),
                    Div(*[_toast("info", f"Notification {i}: system check passed.") for i in range(1, 4)], class_="space-y-3"),
                    class_="max-w-2xl",
                ),
                class_="max-w-6xl mx-auto space-y-12 py-12",
            ),
            class_="relative -mt-16 z-10",
        ),
        Footer(copyright="© 2026 MikiUI Notifications"),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/center")
def center(ctx) -> Div:
    token = ctx.request.cookies.get("mikiui_session") if ctx.request else None
    user = app.validate_session(token) if token else "guest"
    unread = notifications.get_notifications(user, unread_only=True)

    if not unread:
        items = [P("No unread notifications.", class_="text-slate-500")]
    else:
        items = []
        for n in unread:
            level = n.get("type", "info")
            items.append(
                Div(
                    Div(
                        Badge(level.capitalize(), variant={"info": "primary", "success": "success", "warning": "warning", "error": "error"}.get(level, "default"), size="sm"),
                        P(n.get("message", ""), class_="text-sm text-slate-700"),
                        class_="flex items-start gap-2",
                    ),
                    P("Just now", class_="text-xs text-slate-400 mt-1"),
                    Button("Mark read", variant="secondary", hx_post=f"/api/notifications/read/{n['id']}", hx_target="#feed", hx_swap="innerHTML", class_="mt-2 text-xs"),
                    Hr(class_="my-3"),
                    class_="p-4 border border-slate-100 rounded-lg bg-white",
                )
            )

    return Div(
        Navbar(brand="Notifications", links=[("Home", "/"), ("Center", "/center"), ("Settings", "/settings")]),
        Div(
            H1("Notification Center", class_="text-3xl font-bold text-slate-900 mb-2"),
            P(f"{len(unread)} unread notification{'s' if len(unread) != 1 else ''}.", class_="text-slate-600 mb-8"),
            Div(*items, id="feed", class_="max-w-2xl space-y-3"),
            Div(
                Button("Clear All", variant="secondary", hx_post="/api/notifications/clear", hx_target="#feed", hx_swap="innerHTML"),
                class_="mt-6 max-w-2xl"),
            class_="max-w-6xl mx-auto py-12",
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/settings")
def settings() -> Div:
    return Div(
        Navbar(brand="Notifications", links=[("Home", "/"), ("Center", "/center")]),
        Div(
            H1("Notification Settings", class_="text-3xl font-bold text-slate-900 mb-2"),
            P("Configure default behavior for toasts and alerts.", class_="text-slate-600 mb-8"),
            Div(
                Card(
                    Div(
                        Div(
                            Label("Default Duration (ms)", for_="dur", class_="block text-sm font-medium text-slate-700 mb-1"),
                            Select(
                                Option("3 seconds", value="3000"),
                                Option("5 seconds", value="5000", selected=True),
                                Option("10 seconds", value="10000"),
                                Option("Sticky", value="0"),
                                id="dur",
                                name="duration",
                                class_="w-full rounded border-slate-300",
                            ),
                            class_="mb-4",
                        ),
                        Div(
                            Label("Sound", class_="block text-sm font-medium text-slate-700 mb-1"),
                            Div(
                                Button("Preview", variant="secondary", onclick="alert('🔔 Ding!')"),
                                class_="mt-1",
                            ),
                            class_="mb-4",
                        ),
                        Button("Save Preferences", variant="primary", hx_post="/api/notifications/settings", hx_target="#settings-result", hx_swap="innerHTML"),
                        Div(id="settings-result", class_="mt-4"),
                        class_="p-6",
                    ),
                    class_="max-w-lg",
                ),
                class_="max-w-6xl mx-auto py-12",
            ),
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/api/notifications/clear", methods=["POST"])
async def clear_notifications(ctx) -> Div:
    token = ctx.request.cookies.get("mikiui_session") if ctx.request else None
    user = app.validate_session(token) if token else "guest"
    notifications.clear(user)
    return Div(P("All notifications cleared.", class_="text-slate-500"), id="feed", class_="max-w-2xl space-y-3")


@app.route("/api/notifications/read/{notif_id}", methods=["POST"])
async def mark_read(ctx, notif_id: str) -> Div:
    token = ctx.request.cookies.get("mikiui_session") if ctx.request else None
    user = app.validate_session(token) if token else "guest"
    notifications.mark_read(user, notif_id)
    unread = notifications.get_notifications(user, unread_only=True)
    if not unread:
        return Div(P("No unread notifications.", class_="text-slate-500"), id="feed", class_="max-w-2xl space-y-3")
    items = []
    for n in unread:
        level = n.get("type", "info")
        items.append(
            Div(
                Div(
                    Badge(level.capitalize(), variant={"info": "primary", "success": "success", "warning": "warning", "error": "error"}.get(level, "default"), size="sm"),
                    P(n.get("message", ""), class_="text-sm text-slate-700"),
                    class_="flex items-start gap-2",
                ),
                P("Just now", class_="text-xs text-slate-400 mt-1"),
                Button("Mark read", variant="secondary", hx_post=f"/api/notifications/read/{n['id']}", hx_target="#feed", hx_swap="innerHTML", class_="mt-2 text-xs"),
                Hr(class_="my-3"),
                class_="p-4 border border-slate-100 rounded-lg bg-white",
            )
        )
    return Div(*items, id="feed", class_="max-w-2xl space-y-3")


@app.route("/api/notifications/settings", methods=["POST"])
async def save_settings(ctx) -> Div:
    data = await ctx.form()
    duration = data.get("duration", "5000")
    notifications.default_duration = int(duration)
    return Div(P(f"Settings saved. Default duration: {duration} ms.", class_="text-emerald-600"), id="settings-result")


if __name__ == "__main__":
    app.run()
