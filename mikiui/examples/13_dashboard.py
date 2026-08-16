"""13_dashboard.py — Analytics dashboard combining widgets.

Demonstrates stats cards, charts, DataGrid, LogViewer, NotificationPanel,
and sidebar navigation.

Run with: mikiui dev --app mikiui.examples.13_dashboard:app
"""

from __future__ import annotations

from mikiui import Chart, Div, H1, H2, MikiApp, P
from mikiui.components import Button, Navbar
from mikiui.widgets import (
    Avatar,
    Badge,
    Card,
    DataGrid,
    KanbanBoard,
    LogViewer,
    NotificationPanel,
    ProgressDialog,
    SidePanel,
    SplitView,
    StatusBar,
    TabbedPanel,
    TerminalWidget,
    Toolbar,
)

app = MikiApp(title="Ops Dashboard", lang="en")

LATENCY = [12, 18, 15, 22, 19, 25, 30, 28, 21, 17, 14, 20]
SALES = [4200, 5100, 4800, 6200, 5900, 7100, 6800, 7500, 8200, 7800, 8500, 9100]
SERVICES = [35, 25, 20, 20]

TRANSACTIONS = [
    ["TXN-1001", "Acme Corp", "$2,400", "Completed", "2 min ago"],
    ["TXN-1002", "Globex", "$1,800", "Pending", "5 min ago"],
    ["TXN-1003", "Initech", "$3,200", "Completed", "12 min ago"],
    ["TXN-1004", "Umbrella", "$950", "Failed", "18 min ago"],
    ["TXN-1005", "Stark Ind", "$12,400", "Completed", "25 min ago"],
    ["TXN-1006", "Wayne Ent", "$8,100", "Completed", "31 min ago"],
]

LOGS = [
    "info: Scheduler started",
    ("info", "Database connection pool: 8/20"),
    ("warning", "High memory usage on worker-3: 87%"),
    ("error", "Job #1024 failed: timeout after 30s"),
    ("debug", "Cache hit ratio: 94.2%"),
    ("info", "New deployment: v2.4.1"),
    ("warning", "Rate limit approaching for /api/search"),
    ("info", "Backup completed in 4m 12s"),
    ("error", "Email service unavailable"),
    ("debug", "GC pause: 12ms"),
]


@app.route("/")
def home() -> Div:
    return Div(
        Toolbar(
            Button("Refresh", variant="secondary", class_="mr-1"),
            Button("Export", variant="secondary", class_="mr-1"),
            Button("Settings", variant="secondary"),
            class_="px-4 py-2 border-b border-slate-200 bg-white",
        ),
        Div(
            SidePanel(
                "left",
                Div(
                    P("Dashboard", class_="font-semibold text-slate-700"),
                    P("Transactions"),
                    P("Queue"),
                    P("Logs"),
                    P("Settings"),
                    class_="space-y-3",
                ),
                header="Navigation",
                collapsible=True,
            ),
            Div(
                Div(
                    Card(H1("Revenue (30d)"), P("$91.2k"), class_="p-5"),
                    Card(H1("Latency (avg)"), P("20.2 ms"), class_="p-5"),
                    Card(H1("Error Rate"), P("0.02%"), Badge("Low", variant="success"), class_="p-5"),
                    Card(H1("Active Users"), P("1,284"), class_="p-5"),
                    class_="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6",
                ),
                Div(
                    Div(
                        H2("Revenue Trend", class_="text-lg font-bold text-slate-800 mb-3"),
                        Chart(SALES, kind="line", width=600, height=180),
                        class_="bg-white p-5 rounded-xl shadow-sm border border-slate-100",
                    ),
                    Div(
                        H2("Service Distribution", class_="text-lg font-bold text-slate-800 mb-3"),
                        Chart(SERVICES, kind="pie", width=300, height=180),
                        class_="bg-white p-5 rounded-xl shadow-sm border border-slate-100",
                    ),
                    class_="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6",
                ),
                Div(
                    Div(
                        H2("Recent Transactions", class_="text-lg font-bold text-slate-800 mb-3"),
                        DataGrid(
                            columns=["ID", "Customer", "Amount", "Status", "Time"],
                            rows=TRANSACTIONS,
                            sortable=True,
                            filterable=True,
                            pagination=True,
                            page_size=5,
                        ),
                        class_="bg-white p-5 rounded-xl shadow-sm border border-slate-100",
                    ),
                    class_="mb-6",
                ),
                Div(
                    H2("System Logs", class_="text-lg font-bold text-slate-800 mb-3"),
                    LogViewer(lines=LOGS, line_numbers=True, auto_scroll=True),
                    class_="bg-white p-5 rounded-xl shadow-sm border border-slate-100 mb-6",
                ),
                Div(
                    H2("Task Queue", class_="text-lg font-bold text-slate-800 mb-3"),
                    KanbanBoard({
                        "Backlog": ["Design auth", "Update docs"],
                        "In Progress": ["Refactor router", "Fix pagination"],
                        "Review": ["Security patch"],
                        "Done": ["CI setup", "Dockerfile"],
                    }),
                    class_="bg-white p-5 rounded-xl shadow-sm border border-slate-100",
                ),
                class_="flex-1 min-w-0 p-6 space-y-6 overflow-y-auto",
            ),
            class_="flex min-h-[calc(100vh-48px)]",
        ),
        StatusBar(
            Div(P("v2.4.1"), class_="text-xs"),
            Div(P("CPU 34%"), class_="text-xs"),
            Div(P("MEM 62%"), class_="text-xs"),
            Div(P("Latency 20ms"), class_="text-xs"),
            class_="px-4 py-1 bg-slate-800 text-slate-300 text-xs border-t border-slate-700",
        ),
        class_="max-w-7xl mx-auto",
    )


if __name__ == "__main__":
    app.run()
