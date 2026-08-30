"""Mobile example app — demonstrates mobile features.

Run with:
  mikiui dev
  # or
  mikiui mobile build --target android
"""
from mikiui import MikiApp, Div, H1, H2, P, Button, Card
from mikiui.components import Tabs, Form, Input
from mikiui.app.mobile import MobileConfig

app = MikiApp(
    title="Mobile Demo",
    mobile=MobileConfig(
        backend="cloud",
        api_base="https://api.example.com",
        target_platform="both",
        plugins=["Camera", "Geolocation"],
        app_id="com.example.mobile",
        app_name="Mobile Demo",
        orientation="default",
        background_color="#f8fafc",
    ),
)


@app.route("/", title="Home")
def home():
    return Div(
        H1("Mobile Demo"),
        P("This app demonstrates MikiUI's mobile capabilities."),
        Card(
            H2("Features"),
            Ul(
                Li("Cloud mode (Capacitor)"),
                Li("On-device mode (Chaquopy)"),
                Li("PWA support"),
                Li("Native camera access"),
                Li("Geolocation"),
                Li("Push notifications"),
                Li("Touch-optimized UI"),
            ),
        ),
        class_="p-4 space-y-4",
    )


@app.route("/camera", title="Camera")
def camera():
    return Div(
        H1("Camera"),
        P("Tap below to take a photo."),
        Button(
            "Take Photo",
            onclick="MikiFeatures.takePhoto().then(r => alert('Photo taken!'))",
        ),
        class_="p-4 space-y-4",
    )


@app.route("/location", title="Location")
def location():
    return Div(
        H1("Location"),
        P("Tap below to get your current location."),
        Button(
            "Get Location",
            onclick="MikiFeatures.getCurrentPosition().then(r => alert('Lat: ' + r.coords.lat))",
        ),
        class_="p-4 space-y-4",
    )


@app.route("/settings", title="Settings")
def settings():
    return Div(
        H1("Settings"),
        Tabs([
            ("General", Div(P("General settings"))),
            ("Security", Div(P("Security settings"))),
            ("About", Div(P("About this app"))),
        ]),
        class_="p-4",
    )


@app.route("/contact", title="Contact")
def contact():
    return Div(
        H1("Contact Us"),
        Form(
            Input(name="name", placeholder="Your name", aria_label="Name"),
            Input(name="email", placeholder="Your email", aria_label="Email"),
            Input(name="message", placeholder="Your message", aria_label="Message"),
            Button("Send", type="submit"),
            method="POST",
        ),
        class_="p-4 space-y-4",
    )


# Helper for list items
def Ul(*items):
    from mikiui.components import Ul as _Ul, Li
    return _Ul(*[Li(item) for item in items])


if __name__ == "__main__":
    app.run()
