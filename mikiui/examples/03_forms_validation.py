"""03_forms_validation.py — Event registration with real-time validation.

Demonstrates multi-field form, live validation feedback, and a success
confirmation with a registration stats chart.

Run with: mikiui dev --app mikiui.examples.03_forms_validation:app
"""

from __future__ import annotations

from mikiui import (
    Chart,
    Div,
    H1,
    H2,
    MikiApp,
    Navbar,
    P,
)
from mikiui.components import (
    Button,
    Checkbox,
    Form,
    Input,
    Label,
    Radio,
    Select,
    Textarea,
)
from mikiui.components.form import Option
from mikiui.validation import Choice, Email, Length, Pattern, Range, Required
from mikiui.validation.form import Field, FormValidator
from mikiui.widgets.layout_widgets import Hero

app = MikiApp(title="PyCon 2026 — Registration", lang="en")

validator = FormValidator(
    Field("full_name", Required(), Length(min=2, max=80)),
    Field("email", Required(), Email()),
    Field("phone", Required(), Pattern(r"^\+?[\d\s\-()]{7,20}$")),
    Field("ticket", Required(), Choice(["general", "vip", "student", "speaker"])),
    Field("agree", Required()),
)


def _error(field: str, message: str) -> Div:
    return Div(message, class_="text-red-500 text-sm mt-1", id=f"error-{field}", role="alert")


@app.route("/")
def home() -> Div:
    return Div(
        Navbar(
            brand="PyCon 2026",
            links=[
                ("Schedule", "#schedule"),
                ("Speakers", "#speakers"),
                ("Venue", "#venue"),
                ("Register", "/"),
            ],
            dark=True,
        ),
        Div(
            Hero(
                "PyCon 2026",
                subtitle="May 12–15 · Lisbon, Portugal",
                image="https://picsum.photos/seed/pycon/1200/450",
                align="center",
            ),
            Div(
                Div(
                    H1("Register Now", class_="text-3xl font-bold text-slate-900 mb-2"),
                    P("Secure your spot at Europe's largest Python conference.", class_="text-slate-600 mb-8"),
                    Form(
                        Div(
                            Div(
                                Label("Full Name", for_="full_name"),
                                Input(
                                    type="text",
                                    id="full_name",
                                    name="full_name",
                                    placeholder="Guido van Rossum",
                                    class_="w-full rounded border-slate-300",
                                    aria_describedby="error-full_name",
                                ),
                                _error("full_name", "Please enter your full name (2-80 characters)."),
                                class_="mb-4",
                            ),
                            Div(
                                Label("Email Address", for_="email"),
                                Input(
                                    type="email",
                                    id="email",
                                    name="email",
                                    placeholder="you@example.com",
                                    class_="w-full rounded border-slate-300",
                                    aria_describedby="error-email",
                                ),
                                _error("email", "Please enter a valid email address."),
                                class_="mb-4",
                            ),
                            Div(
                                Label("Phone Number", for_="phone"),
                                Input(
                                    type="tel",
                                    id="phone",
                                    name="phone",
                                    placeholder="+1 (555) 000-0000",
                                    class_="w-full rounded border-slate-300",
                                    aria_describedby="error-phone",
                                ),
                                _error("phone", "Enter a valid phone number (min 7 digits)."),
                                class_="mb-4",
                            ),
                            Div(
                                Label("Ticket Type", for_="ticket"),
                                Select(
                                    Option("Select ticket type", value="", selected=True, disabled=True),
                                    Option("General — €299", value="general"),
                                    Option("VIP — €599", value="vip"),
                                    Option("Student — €99", value="student"),
                                    Option("Speaker", value="speaker"),
                                    id="ticket",
                                    name="ticket",
                                    class_="w-full rounded border-slate-300",
                                ),
                                _error("ticket", "Please select a ticket type."),
                                class_="mb-4",
                            ),
                            Div(
                                Label("Dietary Preferences", class_="font-semibold text-slate-700"),
                                Div(
                                    Div(
                                        Checkbox(id="diet-vegetarian", name="diet", value="vegetarian"),
                                        Label("Vegetarian", for_="diet-vegetarian", class_="ml-2"),
                                        class_="flex items-center",
                                    ),
                                    Div(
                                        Checkbox(id="diet-vegan", name="diet", value="vegan"),
                                        Label("Vegan", for_="diet-vegan", class_="ml-2"),
                                        class_="flex items-center",
                                    ),
                                    Div(
                                        Checkbox(id="diet-gluten", name="diet", value="gluten_free"),
                                        Label("Gluten-free", for_="diet-gluten", class_="ml-2"),
                                        class_="flex items-center",
                                    ),
                                    class_="space-y-2",
                                ),
                                class_="mb-4",
                            ),
                            Div(
                                Label("Session Preference", class_="font-semibold text-slate-700"),
                                Div(
                                    Div(
                                        Radio(id="session-morning", name="session", value="morning"),
                                        Label("Morning (9 AM – 12 PM)", for_="session-morning", class_="ml-2"),
                                        class_="flex items-center",
                                    ),
                                    Div(
                                        Radio(id="session-afternoon", name="session", value="afternoon"),
                                        Label("Afternoon (1 PM – 5 PM)", for_="session-afternoon", class_="ml-2"),
                                        class_="flex items-center",
                                    ),
                                    class_="space-y-2",
                                ),
                                class_="mb-4",
                            ),
                            Div(
                                Label("Special Requests", for_="requests"),
                                Textarea(
                                    id="requests",
                                    name="requests",
                                    placeholder="Accessibility needs, workshop interests, etc.",
                                    rows=3,
                                    class_="w-full rounded border-slate-300",
                                ),
                                class_="mb-4",
                            ),
                            Div(
                                Checkbox(id="agree", name="agree", value="yes"),
                                Label("I agree to the code of conduct and cancellation policy.", for_="agree", class_="ml-2 text-sm text-slate-600"),
                                class_="mb-6",
                            ),
                            _error("agree", "You must agree to the terms to continue."),
                            Button("Complete Registration", type="submit", variant="primary", class_="w-full py-3 text-lg"),
                            hx_post="/register",
                            hx_target="#result",
                            hx_swap="innerHTML",
                            class_="space-y-4",
                        )
                    ),
                    Div(id="result", class_="mt-6"),
                    class_="max-w-xl mx-auto bg-white p-8 rounded-2xl shadow-lg border border-slate-100",
                ),
                class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12",
            ),
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/register", methods=["POST"])
async def register(ctx) -> Div:
    data = await ctx.form()
    errors = validator.validate(data)
    if errors:
        return Div(
            P("Please fix the errors below:", class_="font-semibold text-red-600 mb-2"),
            *[P(f"{field}: {msg}", class_="text-red-500") for field, msg in errors.items()],
            class_="p-4 border border-red-200 rounded-lg bg-red-50",
        )

    name = data.get("full_name", "Attendee")
    stats = [
        ("Registered", "2,847", "+320 today"),
        ("VIP", "412", "12% of total"),
        ("Speakers", "86", "18 countries"),
        ("Workshops", "24", "6 tracks"),
    ]
    stat_cards = []
    for label, value, note in stats:
        stat_cards.append(
            Card(
                P(value, class_="text-2xl font-bold text-slate-800"),
                P(label, class_="text-sm text-slate-500"),
                P(note, class_="text-xs text-slate-400 mt-1"),
                class_="p-4 text-center",
            )
        )

    return Div(
        Div(
            P("Registration confirmed!", class_="text-2xl font-bold text-emerald-600 mb-1"),
            P(f"Welcome, {name}. Check your email for ticket details.", class_="text-slate-600 mb-6"),
            Div(
                P("Registration Stats", class_="text-lg font-semibold text-slate-700 mb-4"),
                Div(*stat_cards, class_="grid grid-cols-2 md:grid-cols-4 gap-4"),
                class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100",
            ),
            class_="max-w-3xl mx-auto",
        ),
        class_="py-12",
    )


if __name__ == "__main__":
    app.run()
