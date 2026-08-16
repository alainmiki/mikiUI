"""11_websocket_chat.py — Team chat with channels and online users.

Demonstrates ChatUI, Avatar with status indicators, channel switching,
message input simulation, and connection status.

Run with: mikiui dev --app mikiui.examples.11_websocket_chat:app
"""

from __future__ import annotations

from mikiui import Div, H1, H2, H3, MikiApp, P
from mikiui.components import Button, Form, Input, Navbar
from mikiui.widgets import Avatar, Badge, ChatUI, Card, SidePanel
from mikiui.backend.websocket import ConnectionManager

app = MikiApp(title="Team Chat", lang="en")

manager = ConnectionManager(max_connections_per_ip=20, max_message_size=1024 * 16)

CHANNELS = {
    "general": [
        {"role": "bot", "text": "Welcome to #general. Use this channel for team-wide announcements."},
        {"role": "user", "text": "Morning everyone! Sprint planning is at 10 AM."},
        {"role": "bot", "text": "Alice joined the channel."},
    ],
    "random": [
        {"role": "bot", "text": "Welcome to #random. Share memes, recipes, and weekend plans."},
        {"role": "user", "text": "Has anyone tried the new ramen place on Main St?"},
        {"role": "user", "text": "Yes! The tonkotsu is incredible."},
    ],
    "engineering": [
        {"role": "bot", "text": "Welcome to #engineering. Post PRs, RFCs, and architecture diagrams here."},
        {"role": "user", "text": "Merged PR #512: refactor auth middleware."},
        {"role": "user", "text": "Can someone review the WebSocket connection pooling patch?"},
    ],
}

USERS = [
    ("Alice Kim", "https://i.pravatar.cc/150?u=alice", "online"),
    ("Marcus Chen", "https://i.pravatar.cc/150?u=marcus", "online"),
    ("Elena Rossi", "https://i.pravatar.cc/150?u=elena", "away"),
    ("Tomás Rivera", "https://i.pravatar.cc/150?u=tomas", "online"),
    ("Grace Li", "https://i.pravatar.cc/150?u=grace", "offline"),
]


def _user_list() -> Div:
    items = []
    for name, avatar, status in USERS:
        items.append(
            Div(
                Avatar(avatar, alt=name, size="sm", status=status),
                P(name, class_="text-sm text-slate-700"),
                Badge(status.capitalize(), variant={"online": "success", "away": "warning", "offline": "default"}.get(status, "default"), size="sm"),
                class_="flex items-center gap-3 py-2",
            )
        )
    return Div(*items)


def _channel_buttons(active: str) -> Div:
    buttons = []
    for ch in CHANNELS:
        variant = "primary" if ch == active else "secondary"
        buttons.append(
            Button(f"# {ch}", variant=variant, hx_post=f"/api/chat/switch/{ch}", hx_target="#chat-body", hx_swap="innerHTML", class_="mr-2 mb-2")
        )
    return Div(*buttons, class_="flex flex-wrap gap-2")


@app.route("/")
def home(ctx) -> Div:
    active = "general"
    return Div(
        Navbar(brand="Team Chat", links=[("Chat", "/"), ("Connections", "/connections")], dark=True),
        Div(
            Div(
                SidePanel(
                    "left",
                    Div(
                        H3("Channels", class_="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3"),
                        _channel_buttons(active),
                        H3("Online Users", class_="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 mt-6"),
                        _user_list(),
                        class_="p-4",
                    ),
                    header="Channels",
                    width="280px",
                ),
                Div(
                    Card(
                        Div(
                            H2(f"# {active}", class_="text-xl font-bold text-slate-800"),
                            Badge("Live", variant="success", size="sm"),
                            class_="flex items-center gap-2 mb-4",
                        ),
                        ChatUI(CHANNELS[active]),
                        Form(
                            Div(
                                Input(name="message", placeholder=f"Message # {active}...", class_="flex-1 rounded border-slate-300"),
                                Button("Send", type="submit", variant="primary"),
                                hx_post=f"/api/chat/send/{active}",
                                hx_target="#chat-body",
                                hx_swap="innerHTML",
                                class_="flex gap-2 mt-3",
                            )
                        ),
                        id="chat-body",
                        class_="p-6",
                    ),
                    class_="flex-1 min-w-0 p-4",
                ),
                class_="flex min-h-[calc(100vh-64px)]",
            ),
            class_="max-w-7xl mx-auto",
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/connections")
def connections() -> Div:
    return Div(
        Navbar(brand="Team Chat", links=[("Chat", "/")]),
        Div(
            H1("Connection Stats", class_="text-3xl font-bold text-slate-900 mb-2"),
            P(f"Active WebSocket connections: {len(manager.active)}", class_="text-slate-600 mb-8"),
            Card(
                P("WebSocket endpoints are mounted on the FastAPI app during build.", class_="text-slate-600"),
                P("Use ConnectionManager to broadcast messages to all connected clients.", class_="text-slate-600 mt-2"),
                class_="max-w-2xl p-6",
            ),
            class_="max-w-6xl mx-auto py-12",
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/api/chat/send/{channel}", methods=["POST"])
async def send_message(ctx, channel: str) -> Div:
    data = await ctx.form()
    message = data.get("message", "").strip()
    if not message:
        return Div(ChatUI(CHANNELS.get(channel, [])), class_="p-6")

    if channel not in CHANNELS:
        CHANNELS[channel] = []
    CHANNELS[channel].append({"role": "user", "text": message})

    if len(message) > 100:
        CHANNELS[channel].append({"role": "bot", "text": "Message received (truncated for demo)."})

    return Div(
        Card(
            Div(
                H2(f"# {channel}", class_="text-xl font-bold text-slate-800"),
                Badge("Live", variant="success", size="sm"),
                class_="flex items-center gap-2 mb-4",
            ),
            ChatUI(CHANNELS[channel]),
            Form(
                Div(
                    Input(name="message", placeholder=f"Message # {channel}...", class_="flex-1 rounded border-slate-300"),
                    Button("Send", type="submit", variant="primary"),
                    hx_post=f"/api/chat/send/{channel}",
                    hx_target="#chat-body",
                    hx_swap="innerHTML",
                    class_="flex gap-2 mt-3",
                )
            ),
            id="chat-body",
            class_="p-6",
        ),
        class_="flex-1 min-w-0 p-4",
    )


@app.route("/api/chat/switch/{channel}", methods=["POST"])
async def switch_channel(ctx, channel: str) -> Div:
    if channel not in CHANNELS:
        CHANNELS[channel] = [{"role": "bot", "text": f"Welcome to #{channel}."}]

    return Div(
        Card(
            Div(
                H2(f"# {channel}", class_="text-xl font-bold text-slate-800"),
                Badge("Live", variant="success", size="sm"),
                class_="flex items-center gap-2 mb-4",
            ),
            ChatUI(CHANNELS[channel]),
            Form(
                Div(
                    Input(name="message", placeholder=f"Message # {channel}...", class_="flex-1 rounded border-slate-300"),
                    Button("Send", type="submit", variant="primary"),
                    hx_post=f"/api/chat/send/{channel}",
                    hx_target="#chat-body",
                    hx_swap="innerHTML",
                    class_="flex gap-2 mt-3",
                )
            ),
            id="chat-body",
            class_="p-6",
        ),
        class_="flex-1 min-w-0 p-4",
    )


if __name__ == "__main__":
    app.run()
