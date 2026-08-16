"""02_basic_components.py — Full blog article page.

Demonstrates Picture, Avatar, article content, blockquote, code blocks,
table of contents, Carousel, comments section, and author bio card.

Run with: mikiui dev --app mikiui.examples.02_basic_components:app
"""

from __future__ import annotations

from mikiui import (
    A,
    Blockquote,
    Br,
    Code,
    Div,
    Em,
    Figcaption,
    H1,
    H2,
    H3,
    H4,
    Hr,
    Img,
    Li,
    MikiApp,
    Nav,
    Ol,
    P,
    Pre,
    Section,
    Small,
    Strong,
    Table,
    Tbody,
    Td,
    Th,
    Thead,
    Time,
    Tr,
    Ul,
)
from mikiui.components import Button, Form, Footer, Input, Label, Navbar, Picture, Textarea, TreeView
from mikiui.widgets import (
    Avatar,
    Badge,
    Card,
    Carousel,
    ChatUI,
    DataGrid,
    DatePicker,
    FilePicker,
    FormWizard,
    KanbanBoard,
    LoginForm,
    LogViewer,
    MediaPlayer,
    NotificationPanel,
    Pagination,
    Progress,
    SearchPanel,
    SidePanel,
    SignupForm,
    SplitView,
    StreamingPanel,
    TabbedPanel,
    TerminalWidget,
    Toolbar,
)
from mikiui.widgets.layout_widgets import Hero

app = MikiApp(title="Building Resilient Microservices with MikiUI", lang="en")

POSTS = [
    {
        "slug": "building-resilient-microservices",
        "title": "Building Resilient Microservices with MikiUI",
        "author": "Elena Vasquez",
        "avatar": "https://i.pravatar.cc/150?u=elena",
        "date": "2026-08-10",
        "read_time": "8 min read",
        "tags": ["Python", "Microservices", "Architecture"],
        "hero": "https://picsum.photos/seed/micro/1200/500",
        "content": [
            ("Introduction", """
<p>Microservice architectures promise scalability and team autonomy, but they also introduce
complexity around network failures, partial outages, and data consistency. In this post,
we explore practical patterns for building resilient services using <Strong>Python</Strong>,
<Strong>FastAPI</Strong>, and the <Strong>MikiUI</Strong> framework.</p>
"""),
            ("Why Resilience Matters", """
<p>Modern cloud-native applications run on unreliable infrastructure. Networks drop,
datasets lag, and third-party APIs go down. A resilient service anticipates these
failures and degrades gracefully.</p>

<Blockquote>"Resilience is not about preventing failures — it is about recovering fast."</Blockquote>

<p>The core patterns we will cover include circuit breakers, retries with exponential
back-off, and bulkhead isolation.</p>
"""),
            ("Circuit Breaker Pattern", """
<p>A circuit breaker prevents cascading failures by stopping requests to a failing
dependency after a threshold is reached. After a cool-down period, it allows a
limited number of test requests through.</p>

<Pre><Code>class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5):
        self.failure_threshold = failure_threshold
        self.failures = 0
        self.state = "closed"</Code></Pre>
"""),
            ("Retry Strategies", """
<p>Not all failures are permanent. Transient errors — such as 503 Service Unavailable —
should be retried with increasing delays. Exponential back-off with jitter prevents
thundering herds.</p>

<Table>
  <Thead>
    <Tr>
      <Th>Attempt</Th>
      <Th>Delay</Th>
      <Th>Jitter</Th>
    </Tr>
  </Thead>
  <Tbody>
    <Tr><Td>1</Td><Td>1 s</Td><Td>±200 ms</Td></Tr>
    <Tr><Td>2</Td><Td>2 s</Td><Td>±400 ms</Td></Tr>
    <Tr><Td>3</Td><Td>4 s</Td><Td>±800 ms</Td></Tr>
  </Tbody>
</Table>
"""),
            ("Observability", """
<p>Resilience without observability is guesswork. Structured logs, distributed traces,
and SLO-based alerting let you detect degradation before users notice.</p>

<Small>Tip: always include a <Code>request_id</Code> in your logs and propagate it across services.</Small>
"""),
        ],
        "related": [
            ("Event-Driven Architecture at Scale", "https://picsum.photos/seed/eda/400/250"),
            ("API Gateway Patterns", "https://picsum.photos/seed/api/400/250"),
            ("Testing Distributed Systems", "https://picsum.photos/seed/test/400/250"),
        ],
        "comments": [
            {"author": "Marcus Chen", "avatar": "https://i.pravatar.cc/150?u=marcus", "text": "Great breakdown of the circuit breaker pattern. Would love a follow-up on bulkheads.", "time": "2 hours ago"},
            {"author": "Aisha Patel", "avatar": "https://i.pravatar.cc/150?u=aisha", "text": "We implemented similar retry logic in our FastAPI stack. The jitter tip saved us from a thundering herd last quarter.", "time": "5 hours ago"},
            {"author": "Tomás Rivera", "avatar": "https://i.pravatar.cc/150?u=tomas", "text": "Could you share the full CircuitBreaker implementation? The snippet here is a nice start.", "time": "1 day ago"},
        ],
    }
]


def _toc(content: list[tuple[str, str]]) -> Ul:
    items = []
    for heading, _ in content:
        items.append(Li(A(heading, href=f"#{heading.lower().replace(' ', '-')}", class_="text-indigo-600 hover:underline")))
    return Ul(*items, class_="space-y-2")


def _render_body(content: list[tuple[str, str]]) -> Div:
    children = []
    for heading, body in content:
        children.append(H2(heading, id=heading.lower().replace(" ", "-"), class_="text-2xl font-bold mt-10 mb-4 scroll-mt-24"))
        children.append(Div(body, class_="prose prose-slate max-w-none"))
    return Div(*children)


def _comments(comments: list[dict]) -> Div:
    items = []
    for c in comments:
        items.append(
            Div(
                Div(
                    Avatar(c["avatar"], alt=c["author"], size="sm"),
                    Div(
                        P(c["author"], class_="font-semibold text-sm"),
                        Time(c["time"], class_="text-xs text-slate-400"),
                        class_="ml-3",
                    ),
                    class_="flex items-center mb-2",
                ),
                P(c["text"], class_="text-slate-700 ml-12"),
                Hr(class_="my-4"),
                class_="mb-4",
            )
        )
    return Div(*items)


@app.route("/")
def home() -> Div:
    post = POSTS[0]

    carousel_items = []
    for url, alt in post["related"]:
        carousel_items.append((url, alt))

    return Div(
        Navbar(
            brand="Tech Blog",
            links=[
                ("Home", "/"),
                ("Architecture", "/category/architecture"),
                ("Python", "/category/python"),
                ("About", "/about"),
            ],
            sticky=True,
            dark=True,
        ),
        Div(
            Hero(
                post["title"],
                subtitle=f"By {post['author']} · {post['read_time']} · {post['date']}",
                image=post["hero"],
                align="center",
                variant="primary",
            ),
            class_="relative -mt-16 z-10",
        ),
        Div(
            Div(
                Div(
                    Div(
                        _render_body(post["content"]),
                        class_="bg-white rounded-xl shadow-sm border border-slate-100 p-8 md:p-12",
                    ),
                    class_="flex-1 min-w-0",
                ),
                Div(
                    Div(
                        H4("Table of Contents", class_="font-semibold text-slate-700 mb-3"),
                        _toc(post["content"]),
                        class_="bg-white rounded-xl shadow-sm border border-slate-100 p-6",
                    ),
                    Div(
                        H4("Author", class_="font-semibold text-slate-700 mb-3"),
                        Card(
                            Avatar(post["avatar"], alt=post["author"], size="lg"),
                            Div(
                                P(post["author"], class_="font-bold text-lg"),
                                P("Senior Platform Engineer at Acme Corp. Writing about distributed systems, Python, and developer experience.", class_="text-sm text-slate-600 mt-1"),
                                Div(
                                    A("Twitter", href="#", class_="text-xs text-indigo-600 hover:underline mr-3"),
                                    A("GitHub", href="#", class_="text-xs text-indigo-600 hover:underline mr-3"),
                                    A("Website", href="#", class_="text-xs text-indigo-600 hover:underline"),
                                    class_="mt-3",
                                ),
                                class_="mt-4",
                            ),
                            class_="p-0",
                        ),
                        class_="bg-white rounded-xl shadow-sm border border-slate-100 p-6 mt-6",
                    ),
                    class_="w-80 shrink-0 hidden xl:block",
                ),
                class_="max-w-7xl mx-auto flex gap-8 px-4 sm:px-6 lg:px-8",
            ),
            Div(
                H3("Related Posts", class_="text-2xl font-bold text-slate-800 mb-6"),
                Carousel(*carousel_items, autoplay=True, interval=5000),
                class_="max-w-7xl mx-auto mt-16",
            ),
            Div(
                H3("Discussion", class_="text-2xl font-bold text-slate-800 mb-6"),
                Card(
                    Form(
                        Div(
                            Label("Name", for_="comment-name"),
                            Input(type="text", id="comment-name", name="name", placeholder="Ada Lovelace", class_="w-full rounded border-slate-300"),
                            Label("Comment", for_="comment-body"),
                            Textarea(id="comment-body", name="body", placeholder="Share your thoughts...", rows=4, class_="w-full rounded border-slate-300"),
                            Button("Post Comment", type="submit", variant="primary"),
                            hx_post="/comments",
                            hx_target="#comments-list",
                            hx_swap="innerHTML",
                            class_="space-y-4",
                        )
                    ),
                    _comments(post["comments"]),
                    Div(id="comments-list"),
                    class_="max-w-3xl mx-auto",
                ),
                class_="max-w-7xl mx-auto mt-16 pb-20",
            ),
            class_="space-y-6",
        ),
        Footer(
            copyright="© 2026 Tech Blog — Powered by MikiUI",
            social=[
                ("RSS", "#"),
                ("Newsletter", "#"),
                (" Mastodon", "#"),
            ],
        ),
        class_="bg-slate-50",
    )


if __name__ == "__main__":
    app.run()
