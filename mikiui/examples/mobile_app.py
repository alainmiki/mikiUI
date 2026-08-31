"""Complete mobile app example — demonstrates all major features.

Run with:
  mikiui dev --mobile
  # or
  mikiui mobile build
"""
from mikiui import MikiApp, Div, H1, H2, H3, P, Button, Card, Span
from mikiui.components import Tabs, Form, Input, Alert, Progress, Badge
from mikiui.app.mobile import MobileConfig

app = MikiApp(
    title="Mobile Demo",
    mobile=MobileConfig(
        backend="cloud",
        api_base="https://api.example.com",
        target_platform="both",
        plugins=[
            "Camera",
            "Geolocation",
            "Push",
            "Biometrics",
            "Device-Info",
            "Clipboard",
            "Share",
            "StatusBar",
            "Network-Status",
            "Haptics",
        ],
        app_id="com.example.mobile",
        app_name="Mobile Demo",
        background_color="#f8fafc",
    ),
)


@app.route("/", title="Home")
def home():
    return Div(
        H1("Mobile Demo"),
        P("Explore MikiUI's mobile capabilities."),
        Card(
            H2("Quick Actions"),
            Div(
                Button("📷 Take Photo", onclick="takePhoto()", class_="miki-btn miki-btn-primary w-full mb-2"),
                Button("📍 Get Location", onclick="getLocation()", class_="miki-btn miki-btn-secondary w-full mb-2"),
                Button("📋 Copy Text", onclick="copyText()", class_="miki-btn miki-btn-secondary w-full mb-2"),
                Button("📤 Share", onclick="shareContent()", class_="miki-btn miki-btn-secondary w-full mb-2"),
                Button("🔔 Notify", onclick="sendNotification()", class_="miki-btn miki-btn-secondary w-full mb-2"),
                Button("👆 Haptic", onclick="doHaptic()", class_="miki-btn miki-btn-secondary w-full mb-2"),
            ),
            class_="p-4",
        ),
        Card(
            H2("Device Info"),
            Div(id="device-info", class_="text-sm text-gray-600"),
            Button("Refresh", onclick="loadDeviceInfo()", class_="miki-btn miki-btn-sm mt-2"),
            class_="p-4 mt-4",
        ),
        Card(
            H2("Network Status"),
            Div(id="network-status", class="text-sm"),
            class_="p-4 mt-4",
        ),
        class_="p-4 space-y-4",
    )


@app.route("/camera", title="Camera")
def camera_page():
    return Div(
        H1("Camera"),
        P("Take photos or pick from gallery."),
        Card(
            Div(id="photo-preview", class_="mb-4"),
            Div(
                Button("📷 Take Photo", onclick="takePhoto()", class_="miki-btn miki-btn-primary mr-2"),
                Button("🖼️ Pick Image", onclick="pickImage()", class_="miki-btn miki-btn-secondary"),
            ),
            class_="p-4",
        ),
        class_="p-4",
    )


@app.route("/location", title="Location")
def location_page():
    return Div(
        H1("Geolocation"),
        P("Get your current location."),
        Card(
            Div(id="location-info", class_="text-sm text-gray-600"),
            Button("📍 Get Location", onclick="getLocation()", class_="miki-btn miki-btn-primary mt-2"),
            class_="p-4",
        ),
        class_="p-4",
    )


@app.route("/notifications", title="Notifications")
def notifications_page():
    return Div(
        H1("Notifications"),
        P("Schedule and manage notifications."),
        Card(
            H3("Local Notification"),
            Form(
                Input(name="title", placeholder="Notification title", aria_label="Title"),
                Input(name="body", placeholder="Notification body", aria_label="Body"),
                Button("Send", type="button", onclick="sendNotification()", class_="miki-btn miki-btn-primary"),
                class_="space-y-2",
            ),
            class_="p-4",
        ),
        Card(
            H3("Push Notifications"),
            P("Register for push notifications from your server."),
            Button("Register", onclick="registerPush()", class_="miki-btn miki-btn-secondary"),
            Div(id="push-token", class="mt-2 text-xs text-gray-500 break-all"),
            class_="p-4 mt-4",
        ),
        class_="p-4 space-y-4",
    )


@app.route("/biometrics", title="Biometrics")
def biometrics_page():
    return Div(
        H1("Biometric Authentication"),
        P("Use Face ID, Touch ID, or fingerprint to authenticate."),
        Card(
            Div(id="biometric-status", class_="mb-4"),
            Button("🔐 Authenticate", onclick="authenticate()", class_="miki-btn miki-btn-primary"),
            class_="p-4",
        ),
        class_="p-4",
    )


@app.route("/settings", title="Settings")
def settings_page():
    return Div(
        H1("Settings"),
        Tabs([
            ("General", Div(
                P("General settings go here."),
                Button("Clear Cache", onclick="alert('Cache cleared!')", class_="miki-btn miki-btn-secondary"),
                class_="p-4",
            )),
            ("About", Div(
                H3("Mobile Demo"),
                P("Built with MikiUI"),
                P("Version 1.0.0", class_="text-sm text-gray-500"),
                class_="p-4",
            )),
            ("Debug", Div(
                H3("Debug Info"),
                Div(id="debug-info", class="text-xs font-mono bg-gray-100 p-2 rounded"),
                Button("Load Debug Info", onclick="loadDebugInfo()", class_="miki-btn miki-btn-sm mt-2"),
                class_="p-4",
            )),
        ]),
        class_="p-4",
    )


# JavaScript for mobile features
@app.on_render
def add_mobile_scripts(tree):
    """Add mobile feature scripts to every page."""
    script = """
    <script>
    // Camera
    async function takePhoto() {
        try {
            const photo = await MikiFeatures.takePhoto({ quality: 90 });
            alert('Photo taken! Path: ' + photo.path);
            const preview = document.getElementById('photo-preview');
            if (preview) preview.innerHTML = '<img src="' + photo.path + '" class="rounded-lg max-w-full">';
        } catch (err) {
            alert('Camera error: ' + err.message);
        }
    }

    async function pickImage() {
        try {
            const images = await MikiFeatures.pickImages({ limit: 1 });
            if (images.photos.length > 0) {
                alert('Selected: ' + images.photos[0].path);
            }
        } catch (err) {
            alert('Pick error: ' + err.message);
        }
    }

    // Geolocation
    async function getLocation() {
        try {
            const pos = await MikiFeatures.getCurrentPosition();
            const info = document.getElementById('location-info');
            if (info) {
                info.innerHTML = `
                    <p><strong>Latitude:</strong> ${pos.coords.latitude.toFixed(6)}</p>
                    <p><strong>Longitude:</strong> ${pos.coords.longitude.toFixed(6)}</p>
                    <p><strong>Accuracy:</strong> ${pos.coords.accuracy}m</p>
                `;
            }
            MikiFeatures.hapticImpact('light');
        } catch (err) {
            alert('Location error: ' + err.message);
        }
    }

    // Clipboard
    async function copyText() {
        try {
            await MikiFeatures.copyToClipboard('Hello from MikiUI!');
            alert('Copied to clipboard!');
            MikiFeatures.hapticSelection();
        } catch (err) {
            alert('Copy error: ' + err.message);
        }
    }

    // Share
    async function shareContent() {
        try {
            await MikiFeatures.shareContent({
                title: 'Check out Mobile Demo!',
                text: 'This app was built with Python and MikiUI.',
                url: 'https://github.com/alainmiki/mikiUI'
            });
        } catch (err) {
            alert('Share error: ' + err.message);
        }
    }

    // Notifications
    async function sendNotification() {
        try {
            await MikiFeatures.scheduleNotification({
                title: 'Hello!',
                body: 'This is a local notification from MikiUI',
                id: Date.now()
            });
            alert('Notification scheduled!');
            MikiFeatures.hapticImpact('medium');
        } catch (err) {
            alert('Notification error: ' + err.message);
        }
    }

    async function registerPush() {
        try {
            await MikiFeatures.registerForPush();
            alert('Registered for push notifications!');
        } catch (err) {
            alert('Push registration error: ' + err.message);
        }
    }

    // Haptics
    function doHaptic() {
        MikiFeatures.hapticImpact('medium');
    }

    // Device Info
    async function loadDeviceInfo() {
        try {
            const info = await MikiFeatures.getDeviceInfo();
            const battery = await MikiFeatures.getBatteryInfo();
            const div = document.getElementById('device-info');
            if (div) {
                div.innerHTML = `
                    <p><strong>Platform:</strong> ${info.platform}</p>
                    <p><strong>Model:</strong> ${info.model}</p>
                    <p><strong>OS:</strong> ${info.operatingSystem} ${info.osVersion}</p>
                    <p><strong>Manufacturer:</strong> ${info.manufacturer}</p>
                    <p><strong>Battery:</strong> ${Math.round(battery.batteryLevel * 100)}% ${battery.isCharging ? '(charging)' : ''}</p>
                    <p><strong>Language:</strong> ${info.languageCode || navigator.language}</p>
                    <p><strong>Emulator:</strong> ${info.isVirtual ? 'Yes' : 'No'}</p>
                `;
            }
        } catch (err) {
            console.error('Failed to load device info:', err);
        }
    }

    // Biometrics
    async function authenticate() {
        try {
            const available = await MikiFeatures.isBiometricsAvailable();
            const status = document.getElementById('biometric-status');
            if (!available) {
                if (status) status.innerHTML = '<p class="text-yellow-600">Biometrics not available on this device.</p>';
                return;
            }
            await MikiFeatures.authenticateWithBiometrics('Verify your identity');
            if (status) status.innerHTML = '<p class="text-green-600">Authentication successful!</p>';
            MikiFeatures.hapticImpact('light');
        } catch (err) {
            const status = document.getElementById('biometric-status');
            if (status) status.innerHTML = '<p class="text-red-600">Authentication failed or cancelled.</p>';
        }
    }

    // Debug Info
    async function loadDebugInfo() {
        const info = await MikiFeatures.getDeviceInfo();
        const battery = await MikiFeatures.getBatteryInfo();
        const network = await MikiFeatures.getNetworkStatus();
        const div = document.getElementById('debug-info');
        if (div) {
            div.textContent = JSON.stringify({ info, battery, network }, null, 2);
        }
    }

    // Network status monitoring
    MikiFeatures.onNetworkChange((status) => {
        const div = document.getElementById('network-status');
        if (div) {
            div.innerHTML = status.connected
                ? '<p class="text-green-600">🟢 Connected</p>'
                : '<p class="text-red-600">🔴 Offline</p>';
        }
    });

    // Load initial data
    document.addEventListener('DOMContentLoaded', () => {
        loadDeviceInfo();
        MikiFeatures.getNetworkStatus().then(status => {
            const div = document.getElementById('network-status');
            if (div) {
                div.innerHTML = status.connected
                    ? '<p class="text-green-600">🟢 Connected</p>'
                    : '<p class="text-red-600">🔴 Offline</p>';
            }
        });
    });
    </script>
    """
    # Insert before closing body tag
    if hasattr(tree, 'children'):
        from mikiui.components import Raw
        tree.children.append(Raw(script))


if __name__ == "__main__":
    app.run()
