"""09_auth_sessions.py — Secure portal with authentication and sessions.

Demonstrates LoginForm, protected routes, session management,
session timeout warning, and logout.

Run with: mikiui dev --app mikiui.examples.09_auth_sessions:app
"""

from __future__ import annotations

from datetime import timedelta

from fastapi.responses import RedirectResponse

from mikiui import Div, H1, H2, MikiApp, P
from mikiui.components import Button, Form, Input, Label, Navbar
from mikiui.themes import Theme
from mikiui.widgets import Avatar, Badge, Card, LoginForm, SignupForm
from mikiui.widgets.layout_widgets import Footer, Hero
from mikiui.widgets.panels import SidePanel
from mikiui_app_plugins import SessionPlugin

app = MikiApp(title="MikiUI Portal", lang="en")
app.use(SessionPlugin(secret_key="secure-portal-secret-key-32", session_lifetime=timedelta(hours=1)))

app.register_theme(Theme(
    name="portal",
    source="custom",
    framework="css",
    variables={"--miki-bg": "#f8fafc", "--miki-fg": "#0f172a", "--miki-accent": "#2563eb"},
    extra_classes=["miki-theme-portal"],
))


def _is_authenticated(ctx) -> tuple[bool, str | None]:
    token = ctx.request.cookies.get("mikiui_session") if ctx.request else None
    if token and app.validate_session(token):
        return True, app.validate_session(token)
    return False, None


@app.route("/")
def home(ctx) -> Div:
    authenticated, user = _is_authenticated(ctx)
    if authenticated:
        return Div(
            Navbar(brand="Portal", links=[("Dashboard", "/dashboard"), ("Profile", "/profile"), ("Logout", "/logout")], dark=True),
            Div(
                Hero(
                    f"Welcome back, {user}",
                    subtitle="Your secure dashboard is ready.",
                    image="https://picsum.photos/seed/portal/1200/450",
                    align="center",
                ),
                class_="relative -mt-16 z-10",
            ),
            Div(
                Div(
                    Card(
                        H2("Recent Activity", class_="text-xl font-bold mb-4"),
                        Div(
                            Div(P("Deployed v2.4.1 to production", class_="text-sm"), P("2 hours ago", class_="text-xs text-slate-400"), class_="flex justify-between mb-2"),
                            Div(P("Merged PR #482: fix auth edge case", class_="text-sm"), P("5 hours ago", class_="text-xs text-slate-400"), class_="flex justify-between mb-2"),
                            Div(P("Updated billing plan", class_="text-sm"), P("1 day ago", class_="text-xs text-slate-400"), class_="flex justify-between"),
                            class_="space-y-3",
                        ),
                        class_="p-6",
                    ),
                    class_="max-w-xl mx-auto",
                ),
                class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12",
            ),
            Footer(copyright="© 2026 MikiUI Portal"),
            class_="min-h-screen bg-slate-50",
        )

    return Div(
        Navbar(brand="Portal", links=[("Home", "/")], dark=True),
        Div(
            Hero("Sign in to Portal", subtitle="Access your projects, analytics, and team chat.", align="center"),
            Div(
                Card(
                    LoginForm(action="/login"),
                    class_="max-w-md mx-auto p-8",
                ),
                Div(id="login-result", class_="mt-6 max-w-md mx-auto"),
                class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10",
            ),
            Footer(copyright="© 2026 MikiUI Portal"),
            class_="min-h-screen bg-slate-50",
        )
    )


@app.route("/login", methods=["POST"])
async def login(ctx) -> Div:
    data = await ctx.form()
    username = data.get("username", "").strip()
    if not username:
        return Div(P("Username is required.", class_="text-red-600"), class_="p-4 bg-red-50 border border-red-200 rounded-lg")
    token = app.create_session(username, role="user")
    response = RedirectResponse("/dashboard", status_code=303)
    app.set_session_cookie(response, token)
    return response


@app.route("/signup", methods=["GET", "POST"])
async def signup(ctx) -> Div:
    if ctx.request.method == "POST":
        data = await ctx.form()
        username = data.get("name", "").strip()
        if not username:
            return Div(P("Name is required.", class_="text-red-600"), class_="p-4 bg-red-50 border border-red-200 rounded-lg")
        token = app.create_session(username, role="user")
        response = RedirectResponse("/dashboard", status_code=303)
        app.set_session_cookie(response, token)
        return response

    return Div(
        Navbar(brand="Portal", links=[("Sign In", "/")]),
        Div(
            Hero("Create Account", subtitle="Join the team in under a minute.", align="center"),
            Div(
                Card(SignupForm(action="/signup"), class_="max-w-md mx-auto p-8"),
                class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10",
            ),
            Footer(copyright="© 2026 MikiUI Portal"),
            class_="min-h-screen bg-slate-50",
        ),
    )


@app.route("/dashboard", requires_auth=True)
def dashboard(ctx) -> Div:
    token = ctx.request.cookies.get("mikiui_session") if ctx.request else None
    user = app.validate_session(token) if token else "guest"
    session_data = app.get_session_data(token) if token else {}

    return Div(
        Navbar(brand="Portal", links=[("Dashboard", "/dashboard"), ("Profile", "/profile"), ("Logout", "/logout")], dark=True),
        Div(
            Div(
                SidePanel(
                    "left",
                    Div(
                        P("Dashboard", class_="font-semibold text-slate-700"),
                        P("Projects"),
                        P("Analytics"),
                        P("Team"),
                        P("Settings"),
                        class_="space-y-3",
                    ),
                    header="Navigation",
                    collapsible=True,
                ),
                Div(
                    Div(
                        Card(
                            H2(f"Hello, {user}", class_="text-2xl font-bold text-slate-900"),
                            P("Here's your secure dashboard overview.", class_="text-slate-600"),
                            class_="p-6",
                        ),
                        class_="max-w-4xl mx-auto mb-8",
                    ),
                    Div(
                        H2("Quick Stats", class_="text-xl font-bold text-slate-800 mb-4"),
                        Div(
                            Card(P("12", class_="text-3xl font-bold text-slate-800"), P("Active Projects", class_="text-sm text-slate-500"), class_="p-5"),
                            Card(P("48", class_="text-3xl font-bold text-slate-800"), P("Team Members", class_="text-sm text-slate-500"), class_="p-5"),
                            Card(Badge("Pro", variant="success"), P("Plan", class_="text-sm text-slate-500 mt-2"), class_="p-5"),
                            class_="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8",
                        ),
                    ),
                    class_="flex-1 min-w-0 p-6",
                ),
                class_="flex min-h-[calc(100vh-64px)]",
            ),
            class_="max-w-7xl mx-auto",
        ),
        Footer(copyright="© 2026 MikiUI Portal"),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/profile", requires_auth=True)
def profile(ctx) -> Div:
    token = ctx.request.cookies.get("mikiui_session") if ctx.request else None
    user = app.validate_session(token) if token else "guest"
    session_data = app.get_session_data(token) if token else {}

    return Div(
        Navbar(brand="Portal", links=[("Dashboard", "/dashboard"), ("Profile", "/profile"), ("Logout", "/logout")], dark=True),
        Div(
            Card(
                Div(
                    Avatar("https://i.pravatar.cc/150?u=portal", alt=user, size="lg"),
                    H2(user, class_="text-2xl font-bold text-slate-900 mt-4"),
                    Badge("Authenticated", variant="success"),
                    Div(
                        Div(P("Role", class_="text-xs text-slate-500"), P(session_data.get("role", "user"), class_="text-sm font-medium"), class_="flex justify-between py-2 border-b border-slate-100"),
                        Div(P("Session started", class_="text-xs text-slate-500"), P("Just now", class_="text-sm font-medium"), class_="flex justify-between py-2 border-b border-slate-100"),
                        Div(P("Session ID", class_="text-xs text-slate-500"), P(str(id(token))[-8:], class_="text-sm font-medium"), class_="flex justify-between py-2"),
                        class_="mt-4",
                    ),
                    Button("Logout", variant="secondary", hx_post="/logout", hx_target="#profile-body", hx_swap="innerHTML"),
                    class_="p-8",
                ),
                class_="max-w-lg mx-auto",
            ),
            Div(id="profile-body"),
            class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12",
        ),
        Footer(copyright="© 2026 MikiUI Portal"),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/logout", methods=["GET", "POST"])
def logout() -> Div:
    response = RedirectResponse("/", status_code=303)
    app.delete_session_cookie(response)
    return response


if __name__ == "__main__":
    app.run()
