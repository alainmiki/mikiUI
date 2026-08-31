# Mobile Development with MikiUI

Build **iOS and Android apps** entirely in Python. MikiUI generates a
Capacitor project that wraps your web app in a native shell — no Swift,
Kotlin, or JavaScript required.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Building Your App](#building-your-app)
5. [Running on Device](#running-on-device)
6. [Native Features](#native-features)
7. [Push Notifications](#push-notifications)
8. [Deployment](#deployment)
9. [Publishing to Stores](#publishing-to-stores)
10. [On-Device Mode](#on-device-mode)
11. [Troubleshooting](#troubleshooting)
12. [API Reference](#api-reference)

---

## Quick Start

```bash
# 1. Create a new project
mikiui new myapp && cd myapp

# 2. Add mobile config to app.py
cat > app.py << 'EOF'
from mikiui import MikiApp, Div, H1, P, Button
from mikiui.app.mobile import MobileConfig

app = MikiApp(
    title="My First Mobile App",
    mobile=MobileConfig(
        backend="cloud",
        api_base="https://my-api.railway.app",
        plugins=["Camera", "Geolocation"],
        app_id="com.example.myfirstapp",
    ),
)

@app.route("/")
def home():
    return Div(
        H1("Hello Mobile!"),
        P("This app was built with Python."),
        Button("Take Photo", onclick="MikiFeatures.takePhoto().then(r => alert('Photo taken!'))"),
        class_="p-4 text-center",
    )
EOF

# 3. Build for mobile
mikiui mobile build

# 4. Install dependencies and sync
cd dist_mobile && npm install && npx cap sync

# 5. Open in Android Studio or Xcode
npx cap open android  # or npx cap open ios
```

---

## Prerequisites

### All Platforms
- **Python 3.14+**
- **Node.js 18+** and **npm**

### Android Development
- **Android Studio** (latest)
- **Java 17+**
- **ANDROID_HOME** environment variable set

### iOS Development (macOS only)
- **Xcode** (latest)
- **Xcode Command Line Tools**
- **Apple Developer Account** ($99/year for publishing)

### Check Your System

```bash
mikiui mobile doctor
```

This checks all required tools and tells you what's missing.

---

## Configuration

Add mobile configuration to your `app.py`:

```python
from mikiui import MikiApp
from mikiui.app.mobile import MobileConfig

app = MikiApp(
    title="My App",
    mobile=MobileConfig(
        # Backend mode: "cloud" (default) or "ondevice" (Android only)
        backend="cloud",

        # Your backend API URL (cloud mode only)
        api_base="https://my-api.railway.app",

        # Target platforms
        target_platform="both",  # "android", "ios", or "both"

        # Native features (auto-generates permissions)
        plugins=["Camera", "Geolocation", "Push"],

        # App identifiers
        app_id="com.example.myapp",
        app_name="My App",

        # UI settings
        orientation="default",  # "portrait", "landscape", or "default"
        background_color="#ffffff",

        # On-device mode (Android only)
        chaquopy_deps=["fastapi", "pydantic"],
    ),
)
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backend` | `str` | `"cloud"` | `"cloud"` or `"ondevice"` |
| `api_base` | `str \| None` | `None` | Backend API URL |
| `ws_base` | `str \| None` | `None` | WebSocket URL |
| `target_platform` | `str` | `"both"` | `"android"`, `"ios"`, or `"both"` |
| `plugins` | `list[str]` | `[]` | Native plugins |
| `app_id` | `str` | `"com.mikiui.app"` | Bundle/Application ID |
| `app_name` | `str \| None` | `None` | Display name |
| `orientation` | `str` | `"default"` | Screen orientation |
| `background_color` | `str` | `"#"` | App background color |
| `splash_duration` | `int` | `3000` | Splash duration (ms) |
| `chaquopy_deps` | `list[str]` | `[]` | Python deps for on-device |
| `allow_cleartext` | `bool` | `False` | Allow HTTP traffic |
| `min_sdk` | `int` | `23` | Minimum Android SDK |
| `target_sdk` | `int` | `34` | Target Android SDK |

---

## Building Your App

### Basic Build

```bash
# Build for both platforms
mikiui mobile build

# Build for specific platform
mikiui mobile build --target android
mikiui mobile build --target ios

# Build with on-device backend
mikiui mobile build --target android --backend ondevice

# Custom output directory
mikiui mobile build --output my_mobile_app
```

### Build Output Structure

```
dist_mobile/
├── capacitor.config.json   # Capacitor configuration
├── package.json            # Node.js dependencies
├── android/                # Android project
├── ios/                    # iOS project
├── bridge/                 # (on-device only)
├── www/                    # Your web app
└── deploy/                 # Deployment configs
```

### After Building

```bash
cd dist_mobile
npm install
npx cap sync
npx cap open android  # or npx cap open ios
```

---

## Native Features

### Camera

```javascript
// Take a photo
const photo = await MikiFeatures.takePhoto({
    quality: 90,
    allowEditing: true,
    resultType: "uri"  // or "base64", "dataUrl"
});

// Pick multiple images from gallery
const images = await MikiFeatures.pickImages({ limit: 10 });

// Save to gallery (mobile only)
await Camera.saveToGallery({ path: photo.path });
```

### Geolocation

```javascript
// Get current position
const pos = await MikiFeatures.getCurrentPosition();
console.log(pos.coords.latitude, pos.coords.longitude);

// Watch position changes
const watchId = await MikiFeatures.watchPosition({}, (pos, err) => {
    if (pos) console.log('Moved to:', pos.coords);
});
```

### Notifications

```javascript
// Schedule a local notification
await MikiFeatures.scheduleNotification({
    title: "Reminder",
    body: "Don't forget!",
    id: 1,
    schedule: { at: new Date(Date.now() + 60000) }  // 1 minute from now
});

// Cancel a notification
await MikiFeatures.cancelNotification(1);

// Register for push notifications
await MikiFeatures.registerForPush();
MikiFeatures.onPushReceived((notification) => {
    console.log('Push received:', notification);
});
```

### Biometrics

```javascript
// Check if biometrics available
const available = await MikiFeatures.isBiometricsAvailable();
if (!available) {
    // Fall back to PIN/password
}

// Authenticate
try {
    await MikiFeatures.authenticateWithBiometrics('Verify your identity');
    // Success!
} catch (err) {
    // User cancelled or failed
}

// Store credentials securely
await MikiFeatures.setBiometricsCredentials('user', 'pass', 'myapp');
const creds = await MikiFeatures.getBiometricsCredentials('myapp');
```

### Device Info

```javascript
const info = await MikiFeatures.getDeviceInfo();
console.log(info.platform);      // "android" | "ios" | "web"
console.log(info.model);         // "Pixel 7" or "iPhone15,2"
console.log(info.osVersion);     // "14" or "17.2"
console.log(info.manufacturer);  // "Google" or "Apple"
console.log(info.isVirtual);     // true if simulator/emulator

const battery = await MikiFeatures.getBatteryInfo();
console.log(battery.batteryLevel);  // 0.0 to 1.0
console.log(battery.isCharging);    // true/false
```

### Media Player

```javascript
// Load audio asset (from app bundle or URL)
await MikiFeatures.loadAudioAsset('sounds/click.mp3', {
    id: 'click',
    audioChannelNum: 1
});

// Playback control
await MikiFeatures.playAudio('click');
await MikiFeatures.pauseAudio('click');
await MikiFeatures.resumeAudio('click');
await MikiFeatures.stopAudio('click');

// Volume and seeking
await MikiFeatures.setAudioVolume('click', 0.8);  // 0.0 to 1.0
await MikiFeatures.seekAudio('click', 30);  // seconds
const duration = await MikiFeatures.getAudioDuration('click');
const current = await MikiFeatures.getCurrentAudioTime('click');

// Cleanup
await MikiFeatures.unloadAudio('click');
```

### Clipboard

```javascript
await MikiFeatures.copyToClipboard('Hello World');
const text = await MikiFeatures.readClipboard();
```

### Share

```javascript
await MikiFeatures.shareContent({
    title: 'Check this out!',
    text: 'My awesome app',
    url: 'https://example.com',
    files: [photo.path]  // optional files
});
```

### Haptics

```javascript
MikiFeatures.hapticImpact('medium');  // 'light' | 'medium' | 'heavy'
MikiFeatures.hapticVibrate(300);       // milliseconds
MikiFeatures.hapticSelection();        // selection click
```

### Screen Orientation

```javascript
await MikiFeatures.lockOrientation('portrait');  // or 'landscape'
await MikiFeatures.unlockOrientation();
const orientation = await MikiFeatures.getOrientation();
```

### App Lifecycle

```javascript
MikiFeatures.onAppPause(() => {
    console.log('App going to background');
});

MikiFeatures.onAppResume(() => {
    console.log('App resumed');
});

MikiFeatures.onBackButton(() => {
    // Handle Android back button
    if (canGoBack) {
        window.history.back();
    } else {
        MikiFeatures.exitApp();
    }
});

MikiFeatures.onAppUrlOpen((data) => {
    console.log('Deep link opened:', data.url);
});
```

### Contacts

```javascript
const contacts = await MikiFeatures.getContacts();
const picked = await MikiFeatures.pickContact();
await MikiFeatures.createContact({
    firstName: 'John',
    lastName: 'Doe',
    phoneNumbers: [{ label: 'mobile', number: '+1234567890' }]
});
```

### Calendar

```javascript
await MikiFeatures.createCalendarEvent({
    title: 'Team Meeting',
    location: 'Office',
    notes: 'Weekly sync',
    startDate: new Date(),
    endDate: new Date(Date.now() + 3600000),
    isAllDay: false
});

const events = await MikiFeatures.getCalendarEvents(
    new Date('2024-01-01'),
    new Date('2024-12-31')
);
```

### File Picker

```javascript
const file = await MikiFeatures.pickFile({
    types: ['image/*', 'application/pdf'],
    multiple: false
});

const photos = await MikiFeatures.pickPhotos({ multiple: true });
const singlePhoto = await MikiFeatures.pickPhoto();
```

---

## Push Notifications

### Setup

1. Add `Push` to your plugins:
```python
MobileConfig(plugins=["Push"])
```

2. Deploy your backend with the push endpoint:
```bash
mikiui mobile build
# See deploy/push-setup.md for FCM/APNs configuration
```

### Sending Notifications (Python)

```python
from mikiui.backend import send_push_notification

# Send to Android (FCM)
send_push_notification(
    token="device_fcm_token",
    title="Hello!",
    body="You have a new message",
    fcm_server_key="your_fcm_server_key",
)

# Send to iOS (APNs)
send_push_notification(
    token="device_apns_token",
    title="Hello!",
    body="You have a new message",
    apns_key_path="/path/to/AuthKey.p8",
    apns_key_id="YOUR_KEY_ID",
    apns_team_id="YOUR_TEAM_ID",
    bundle_id="com.example.app",
)
```

### Receiving Notifications (JavaScript)

```javascript
// Register for push
await MikiFeatures.registerForPush();

// Get token for your backend
const token = await MikiFeatures.getPushToken();
await fetch('/api/devices/register', {
    method: 'POST',
    body: JSON.stringify({ token: token })
});

// Handle incoming notifications
MikiFeatures.onPushReceived((notification) => {
    console.log('Push:', notification.title, notification.body);
});
```

---

## Deployment

### Cloud Mode Backend

Your cloud-mode backend needs to be hosted separately. MikiUI generates
deployment configs for popular platforms:

#### Railway (Recommended)

```bash
cd dist_mobile/deploy
railway up
```

#### Vercel

```bash
cd dist_mobile/deploy
vercel --prod
```

#### Docker

```bash
cd dist_mobile/deploy
docker build -t myapp-backend .
docker run -p 8000:8000 myapp-backend
```

### Updating the Backend URL

After deploying, update `capacitor.config.json`:

```json
{
  "server": {
    "url": "https://myapp.railway.app",
    "cleartext": false
  }
}
```

Then re-sync:
```bash
npx cap sync
```

---

## Publishing to Stores

### App Store (iOS)

1. **Build for release:**
   ```bash
   cd dist_mobile && npx cap open ios
   ```
2. **In Xcode:** Product → Archive → Distribute App
3. **App Store Connect:** Create new app, upload screenshots, submit

### Play Store (Android)

1. **Build for release:**
   ```bash
   cd dist_mobile && npx cap open android
   ```
2. **In Android Studio:** Build → Generate Signed Bundle/APK
3. **Play Console:** Create new app, upload AAB, submit

---

## On-Device Mode

On-device mode runs Python directly on the Android device via Chaquopy.
No server needed — works offline.

### Setup

```python
MobileConfig(
    backend="ondevice",
    target_platform="android",  # iOS not supported
    chaquopy_deps=["fastapi", "pydantic", "uvicorn"],
)
```

### Important Notes

- **Android only** — iOS does not support embedded interpreters
- **No listening sockets** — Uses @JavascriptInterface bridge
- **APK size** — Each Python package adds ~2-10MB
- **Cold start** — Python init takes 1-3 seconds

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| `Node.js not found` | Install from https://nodejs.org/ |
| `ANDROID_HOME not set` | `export ANDROID_HOME=$HOME/Android/Sdk` |
| `npx cap sync` fails | Run `npm install` first |
| App shows blank screen | Run `npx cap sync`, check browser console |
| Network requests fail | Check `capacitor.config.json` URL |
| Camera not working | Verify plugin in `MobileConfig.plugins` |
| Push not received | Check FCM/APNs configuration |

### Getting Help

```bash
mikiui mobile doctor    # Check system readiness
mikiui mobile info      # Show current config
mikiui mobile plugins   # List available plugins
```

---

## API Reference

### MobileConfig

```python
from mikiui.app.mobile import MobileConfig, MobileBackend, MobilePlatform

config = MobileConfig(
    backend=MobileBackend.CLOUD,      # or ONDEVICE
    target_platform=MobilePlatform.BOTH,  # ANDROID, IOS, or BOTH
    plugins=["Camera", "Geolocation"],
    app_id="com.example.app",
    app_name="My App",
    api_base="https://api.example.com",
)
```

### JavaScript Bridges

| Bridge | Purpose |
|--------|---------|
| `MikiBackend` | Unified API calls (cloud/desktop/mobile) |
| `MikiFeatures` | Native device features |
| `MikiEvents` | Bidirectional event bus |
| `MikiCapacitor` | Platform detection |
| `MikiWebSocket` | WebSocket connections |
| `MikiConnection` | Network status monitoring |
