"""04_routing.py — Blog platform with multiple routes and breadcrumbs.

Demonstrates path parameters, mounted routers, active navbar state,
breadcrumbs, and pagination.

Run with: mikiui dev --app mikiui.examples.04_routing:app
"""

from __future__ import annotations

from mikiui import (
    Breadcrumbs,
    Div,
    H1,
    H2,
    H3,
    MikiApp,
    P,
)
from mikiui.components import Navbar
from mikiui.router import Router
from mikiui.widgets import Avatar, Card, Pagination

app = MikiApp(title="MikiUI Blog", lang="en")

POSTS = [
    {
        "id": 1,
        "slug": "building-resilient-microservices",
        "title": "Building Resilient Microservices",
        "author": "Elena Vasquez",
        "avatar": "https://i.pravatar.cc/150?u=elena",
        "date": "2026-08-10",
        "category": "architecture",
        "excerpt": "Practical patterns for building resilient services using Python, FastAPI, and MikiUI.",
        "body": "Microservice architectures promise scalability and team autonomy, but they also introduce complexity around network failures...",
    },
    {
        "id": 2,
        "slug": "python-async-deep-dive",
        "title": "Python Async: A Deep Dive",
        "author": "Marcus Chen",
        "avatar": "https://i.pravatar.cc/150?u=marcus",
        "date": "2026-08-05",
        "category": "python",
        "excerpt": "Understanding asyncio, task groups, and structured concurrency in modern Python.",
        "body": "Asynchronous programming in Python has evolved dramatically since the introduction of asyncio...",
    },
    {
        "id": 3,
        "slug": "designing-accessible-uis",
        "title": "Designing Accessible UIs",
        "author": "Aisha Patel",
        "avatar": "https://i.pravatar.cc/150?u=aisha",
        "date": "2026-07-28",
        "category": "frontend",
        "excerpt": "Accessibility is not a feature — it is a requirement. Learn how to build inclusive UIs with MikiUI.",
        "body": "Every component in MikiUI ships with ARIA roles, keyboard navigation, and screen-reader support...",
    },
    {
        "id": 4,
        "slug": "docker-for-python-developers",
        "title": "Docker for Python Developers",
        "author": "Tomás Rivera",
        "avatar": "https://i.pravatar.cc/150?u=tomas",
        "date": "2026-07-20",
        "category": "devops",
        "excerpt": "From development to production: containerizing FastAPI apps with Docker Compose.",
        "body": "Containerization standardizes environments and eliminates 'it works on my machine' issues...",
    },
    {
        "id": 5,
        "slug": "testing-strategies-2026",
        "title": "Testing Strategies for 2026",
        "author": "Elena Vasquez",
        "avatar": "https://i.pravatar.cc/150?u=elena",
        "date": "2026-07-15",
        "category": "testing",
        "excerpt": "Unit, integration, and contract testing with pytest, Playwright, and Testcontainers.",
        "body": "A robust test suite is the safety net that lets teams refactor with confidence...",
    },
]

CATEGORIES = {
    "architecture": "Architecture",
    "python": "Python",
    "frontend": "Frontend",
    "devops": "DevOps",
    "testing": "Testing",
}


def _post_card(post: dict) -> Card:
    return Card(
        Div(
            H3(post["title"], class_="text-xl font-bold text-slate-900 mb-2"),
            P(post["excerpt"], class_="text-slate-600 mb-4"),
            Div(
                Avatar(post["avatar"], alt=post["author"], size="sm"),
                P(post["author"], class_="text-sm font-medium text-slate-700 ml-2"),
                P(post["date"], class_="text-xs text-slate-400 ml-auto"),
                class_="flex items-center",
            ),
            class_="p-6",
        ),
        class_="hover:shadow-md transition-shadow",
    )


def _page(title: str, breadcrumbs_items: list[tuple[str, str]], body: Div) -> Div:
    return Div(
        Navbar(
            brand="MikiUI Blog",
            links=[
                ("Home", "/"),
                ("Architecture", "/category/architecture"),
                ("Python", "/category/python"),
                ("About", "/about"),
            ],
            dark=True,
        ),
        Div(
            Breadcrumbs(breadcrumbs_items, class_="mb-6"),
            body,
            class_="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8",
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/")
def home() -> Div:
    cards = [_post_card(p) for p in POSTS]
    return _page(
        "Latest Posts",
        [("/", "Home")],
        Div(
            H1("Latest Posts", class_="text-3xl font-bold text-slate-900 mb-8"),
            Div(*cards, class_="grid gap-6"),
            Pagination(current=1, total=3, base_url="/page"),
            class_="space-y-8",
        ),
    )


@app.route("/post/{slug}")
def post_detail(ctx, slug: str) -> Div:
    post = next((p for p in POSTS if p["slug"] == slug), None)
    if not post:
        return Div(H1("Post Not Found", class_="text-2xl font-bold text-red-600"), P("The requested article does not exist."), class_="py-20 text-center")

    return _page(
        post["title"],
        [("/", "Home"), (f"/post/{slug}", "Post")],
        Div(
            Card(
                Div(
                    H1(post["title"], class_="text-3xl font-bold text-slate-900 mb-4"),
                    Div(
                        Avatar(post["avatar"], alt=post["author"], size="md"),
                        Div(
                            P(post["author"], class_="font-semibold text-slate-700"),
                            P(post["date"], class_="text-sm text-slate-500"),
                            class_="ml-3",
                        ),
                        class_="flex items-center mb-6",
                    ),
                    Hr(),
                    P(post["body"], class_="text-slate-700 leading-relaxed mt-6"),
                    class_="p-8",
                ),
                class_="shadow-lg",
            ),
            class_="max-w-3xl",
        ),
    )


@app.route("/category/{name}")
def category(ctx, name: str) -> Div:
    label = CATEGORIES.get(name, name.title())
    filtered = [p for p in POSTS if p["category"] == name]
    cards = [_post_card(p) for p in filtered] if filtered else [P("No posts in this category yet.", class_="text-slate-500")]

    return _page(
        f"Category: {label}",
        [("Home", "/"), ("Category", f"/category/{name}")],
        Div(
            H1(f"Category: {label}", class_="text-3xl font-bold text-slate-900 mb-8"),
            Div(*cards, class_="grid gap-6"),
            class_="space-y-8",
        ),
    )


@app.route("/about")
def about() -> Div:
    return _page(
        "About",
        [("Home", "/"), ("About", "/about")],
        Div(
            Card(
                H1("About MikiUI Blog", class_="text-2xl font-bold mb-4"),
                P("This blog is built with MikiUI, a Python-first UI framework that renders UIs as standalone desktops or websites."),
                P("We write about Python, architecture, frontend development, and DevOps — with a focus on production-ready patterns."),
                class_="p-8",
            ),
            class_="max-w-2xl",
        ),
    )


if __name__ == "__main__":
    app.run()
