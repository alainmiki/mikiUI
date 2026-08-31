# Mobile Guide

Build iOS and Android apps with MikiUI. This guide covers everything from
your first mobile build to publishing on the App Store and Play Store.

## Table of Contents

- [Quick Start](#quick-start)
- [Backend Modes](#backend-modes)
- [Configuration](#configuration)
- [Building](#building)
- [Running](#running)
- [Plugins and Native Features](#plugins-and-native-features)
- [Deployment](#deployment)
- [Publishing](#publishing)
- [Troubleshooting](#troubleshooting)
- [On-Device Mode (Advanced)](#on-device-mode-advanced)
- [API Reference](#api-reference)

---

## Quick Start

The fastest way to build a mobile app:

```bash
# 1. Create a new project
mikiui new myapp
cd myapp

# 2. Run the mobile setup wizard
mikiui mobile setup

# 3. Build for mobile
mikiui mobile build

# 4. Open in Android Studio or Xcode
cd dist_mobile
npm install
npx cap sync
npx cap open android  # or npx cap open ios
```

That's it! Your mobile app is ready to run.

---

## Backend Modes

MikiUI supports two backend modes for mobile apps:

### Cloud Mode (Default, Recommended)

Your app connects to a remote FastAPI backend server.

**Pros:**
- Smaller app size (~8-20MB)
- Works on both iOS and Android
- No embedded Python interpreter
- Easier to update backend without app store resubmission
- Full Python ecosystem available (any pip package)

**Cons:**
- Requires network connection
- Backend hosting costs

**Best for:** Most apps, beginners, apps that need server-side processing.

### On-Device Mode (Android Only)

Your app runs Python directly on the device using Chaquopy.

**Pros:**
- Works offline
- No server costs
- Ultra-low latency (<1ms bridge calls)

**Cons:**
- Larger app size (~33-40MB)
- Android only (iOS does not support embedded interpreters)
- Limited by APK size for Python dependencies

**Best for:** Offline-first apps, data-sensitive apps, low-latency requirements.

---

## Configuration

Add mobile configuration to your `app.py`:

```python
from mikiui import MikiApp, Div, H1
from mikiui.app.mobile import MobileConfig

app = MikiApp(
    title="My App",
    mobile=MobileConfig(
        backend="cloud",  # "cloud" (default) or "ondevice"
        api_base="https://myapp.railway.app",  # Your backend URL
        target_platform="both",  # "android", "ios", or "both"
        plugins=["Camera", "Geolocation"],  # Native features
        app_id="com.example.myapp",  # Unique app identifier
        app_name="My App",  # Display name
    ),
)

@app.route("/")
def home():
    return Div(H1("Welcome to My App"))
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backend` | `str` | `"cloud"` | `"cloud"` or `"ondevice"` |
| `api_base` | `str \| None` | `None` | Backend API URL (cloud mode) |
| `ws_base` | `str \| None` | `None` | WebSocket URL (cloud mode) |
| `target_platform` | `str` | `"both"` | `"android"`, `"ios"`, or `"both"` |
| `plugins` | `list[str]` | `[]` | Native plugins to include |
| `app_id` | `str` | `"com.mikiui.app"` | Bundle/Application ID |
| `app_name` | `str \| None` | `None` | Display name |
| `orientation` | `str` | `"default"` | `"portrait"`, `"landscape"`, or `"default"` |
| `background_color` | `str` | `"#"` | App background color |
| `splash_duration` | `int` | `3000` | Splash screen duration (ms) |
| `chaquopy_deps` | `list[str]` | `[]` | Python deps (on-device only) |
| `allow_cleartext` | `bool` | `False` | Allow HTTP traffic |
| `min_sdk` | `int` | `23` | Minimum Android SDK |
| `target_sdk` | `int` | `34` | Target Android SDK |

---

## Building

### Basic Build

```bash
# Build for both platforms (cloud mode)
mikiui mobile build

# Build for specific platform
mikiui mobile build --target android
mikiui mobile build --target ios

# Build with on-device backend
mikiui mobile build --target android --backend ondevice

# Specify output directory
mikiui mobile build --output my_mobile_app
```

### Build Output

```
dist_mobile/
├── capacitor.json          # Capacitor configuration
├── package.json            # Node.js dependencies
├── android/                # Android native project
│   ├── AndroidManifest.xml
│   ├── res/
│   │   ├── xml/network_security_config.xml
│   │   ├── values/colors.xml
│   │   └── mipmap-anydpi-v26/ic_launcher.xml
│   └── chaquopy.gradle     # (on-device only)
├── ios/                    # iOS native project
│   ├── Info.plist
│   └── PrivacyInfo.xcprivacy
├── bridge/                 # (on-device only)
│   ├── chaquopy_bridge.py
│   └── kotlin/
├── www/                    # Your static web app
│   ├── index.html
│   ├── manifest.webmanifest
│   └── _miki/runtime/...
└── deploy/                 # Deployment configs
    ├── vercel.json
    ├── railway.json
    ├── netlify.toml
    ├── Dockerfile
    └── docker-compose.yml
```

---

## Running

### Development with Live Reload

```bash
# Start dev server with mobile live reload
mikiui dev --mobile

# This rebuilds the mobile project when files change
```

### Run on Device/Emulator

```bash
# Build and run on Android
mikiui mobile run --target android

# Build and run on iOS
mikiui mobile run --target ios

# Open in IDE
mikiui mobile open --target android  # Android Studio
mikiui mobile open --target ios      # Xcode
```

### Manual Steps

```bash
cd dist_mobile

# Install dependencies
npm install

# Sync web assets to native projects
npx cap sync

# Run on device
npx cap run android
npx cap run ios

# Open in IDE
npx cap open android
npx cap open ios
```

---

## Plugins and Native Features

### Available Plugins

| Plugin | Description | Android Permission | iOS Privacy Key |
|--------|-------------|-------------------|-----------------|
| `Camera` | Take photos, scan codes | `CAMERA` | `NSCameraUsageDescription` |
| `Geolocation` | GPS location | `ACCESS_FINE_LOCATION` | `NSLocationWhenInUseUsageDescription` |
| `PushNotifications` | Push notifications | `POST_NOTIFICATIONS` | `UIBackgroundModes` |
| `LocalNotifications` | Local notifications | None | None |
| `Haptics` | Vibration feedback | None | None |
| `Clipboard` | Copy/paste | None | None |
| `Filesystem` | Read/write files | `READ/WRITE_EXTERNAL_STORAGE` | None |
| `Share` | System share sheet | None | None |
| `NetworkStatus` | Network monitoring | `ACCESS_NETWORK_STATE` | None |
| `StatusBar` | Status bar control | None | None |

### Using Plugins

```python
from mikiui.app.mobile import MobileConfig

config = MobileConfig(
    plugins=["Camera", "Geolocation"]
)
```

### JavaScript API

```javascript
// Take a photo
const photo = await MikiFeatures.takePhoto();

// Get location
const position = await MikiFeatures.getCurrentPosition();

// Haptic feedback
MikiFeatures.hapticImpact('medium');

// Copy to clipboard
await MikiFeatures.copyToClipboard('Hello!');

// Share content
await MikiFeatures.shareContent({
    title: 'Check this out!',
    text: 'My awesome app',
    url: 'https://example.com'
});

// Network status
const status = await MikiFeatures.getNetworkStatus();
if (!status.connected) {
    alert('No internet connection!');
}
```

---

## Deployment

### Cloud Mode Backend

Your cloud-mode backend needs to be hosted separately. MikiUI generates
deployment configs for popular platforms:

#### Vercel (Recommended for Beginners)

```bash
cd dist_mobile/deploy
vercel --prod
```

#### Railway

```bash
cd dist_mobile/deploy
railway up
```

#### Docker

```bash
cd dist_mobile/deploy
docker build -t myapp-backend .
docker run -p 8000:8000 myapp-backend
```

#### Docker Compose (Full Stack)

```bash
cd dist_mobile/deploy
docker compose up -d
```

### Updating the Backend URL

After deploying your backend, update `capacitor.config.json`:

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

## Publishing

### App Store (iOS)

1. **Build for release:**
   ```bash
   cd dist_mobile
   npx cap open ios
   ```

2. **In Xcode:**
   - Select "Any iOS Device" as target
   - Product → Archive
   - Distribute App → App Store Connect

3. **App Store Connect:**
   - Create new app record
   - Upload screenshots (required sizes: 6.5", 5.5", iPad Pro)
   - Fill in description, keywords, privacy policy
   - Submit for review

4. **Privacy Manifest:**
   - `PrivacyInfo.xcprivacy` is auto-generated from your plugins
   - Review it matches your actual data usage

### Play Store (Android)

1. **Build for release:**
   ```bash
   cd dist_mobile
   npx cap open android
   ```

2. **In Android Studio:**
   - Build → Generate Signed Bundle / APK
   - Select Android App Bundle (AAB)
   - Create or use existing keystore

3. **Play Console:**
   - Create new app
   - Upload AAB
   - Fill in store listing (screenshots, description)
   - Set up content rating
   - Submit for review

4. **Signing:**
   - Use Android Studio to generate upload key
   - Or use `keytool`:
     ```bash
     keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
     ```

---

## Troubleshooting

### Common Issues

#### "Node.js not found"

Install Node.js from https://nodejs.org/ (LTS version recommended).

#### "npx cap sync" fails

Make sure you ran `npm install` first:
```bash
cd dist_mobile
npm install
npx cap sync
```

#### "ANDROID_HOME not set"

Set the environment variable:
```bash
# Windows
set ANDROID_HOME=C:\Users\YourName\AppData\Local\Android\Sdk

# macOS/Linux
export ANDROID_HOME=$HOME/Android/Sdk
```

#### "Could not find Android Studio"

Install Android Studio from https://developer.android.com/studio

#### "Could not find Xcode" (macOS)

Install Xcode from the Mac App Store, then run:
```bash
xcode-select --install
sudo xcodebuild -license accept
```

#### App shows blank screen

1. Check `capacitor.config.json` has correct `webDir`
2. Run `npx cap sync` after building
3. Check browser console for errors

#### Network requests fail (cloud mode)

1. Verify `api_base` is correct in `capacitor.config.json`
2. Check CORS is configured on your backend
3. For development, you may need `cleartext: true`

#### Camera/Location not working

1. Verify plugin is in `MobileConfig.plugins`
2. Check permissions are granted in device settings
3. On Android, check `AndroidManifest.xml` has the permission

### Getting Help

```bash
# Check system readiness
mikiui mobile doctor

# Show current config
mikiui mobile info

# List available plugins
mikiui mobile plugins
```

---

## On-Device Mode (Advanced)

On-device mode runs your Python backend directly on the Android device
using Chaquopy. This enables offline functionality but requires additional
setup.

### Requirements

- Android Studio with NDK
- Minimum SDK 23 (Android 6.0)
- Target SDK 34 (Android 14) recommended

### Setup

```python
from mikiui.app.mobile import MobileConfig

config = MobileConfig(
    backend="ondevice",
    target_platform="android",
    chaquopy_deps=[
        "fastapi",
        "pydantic",
        "uvicorn",
        # Add your dependencies here
    ],
)
```

### Building

```bash
mikiui mobile build --target android --backend ondevice
cd dist_mobile
npm install
npx cap sync android
npx cap open android
```

### Important Notes

1. **No listening sockets** — On-device mode uses Chaquopy's
   `@JavascriptInterface` bridge, not HTTP sockets. This is required for
   Play Store compliance.

2. **APK size** — Each Python package adds to APK size. Keep dependencies
   minimal.

3. **Cold start** — Python initialization takes 1-3 seconds on first launch.

4. **iOS not supported** — Apple does not allow embedded interpreters.

### Template Generation

MikiUI generates a `bridge/` directory with:
- `chaquopy_bridge.py` — Python bridge module
- `kotlin/OnDeviceBridge.kt` — Kotlin bridge class

You need to add this to your `MainActivity.kt`:

```kotlin
package com.yourpackage.app

import android.os.Bundle
import com.getcapacitor.BridgeActivity

class MainActivity : BridgeActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        registerPlugin(OnDeviceBridge::class.java)
    }
}
```

---

## API Reference

### MobileConfig

```python
from mikiui.app.mobile import MobileConfig

config = MobileConfig(
    backend="cloud",
    api_base="https://api.example.com",
    target_platform="both",
    plugins=["Camera", "Geolocation"],
    app_id="com.example.app",
    app_name="My App",
)
```

### JavaScript Bridges

#### MikiBackend

```javascript
// Make API calls
const result = await MikiBackend.call('GET', '/api/users');
const created = await MikiBackend.call('POST', '/api/users', { name: 'Alice' });

// Platform detection
MikiBackend.isDesktop()    // pywebview detected
MikiBackend.isNative()     // Capacitor detected
MikiBackend.isChaquopy()   // Chaquopy detected
MikiBackend.transport()    // "web" | "desktop" | "cloud" | "ondevice"

// WebSocket
const ws = MikiBackend.subscribe('/ws/chat', (msg) => console.log(msg));
```

#### MikiFeatures

```javascript
// Camera
const photo = await MikiFeatures.takePhoto({ quality: 80 });

// Geolocation
const pos = await MikiFeatures.getCurrentPosition();

// Haptics
MikiFeatures.hikiFeatures.hapticImpact('medium');
MikiFeatures.hapticVibrate(300);

// Clipboard
await MikiFeatures.copyToClipboard('text');
const text = await MikiFeatures.readClipboard();

// Share
await MikiFeatures.shareContent({ title: 'Share', text: 'Hello' });

// Network
const status = await MikiFeatures.getNetworkStatus();
MikiFeatures.onNetworkChange((status) => {
    console.log('Connected:', status.connected);
});

// Notifications
await MikiFeatures.scheduleNotification({
    title: 'Hello',
    body: 'This is a notification',
    id: 1
});
```

#### MikiEvents

```javascript
// Listen for events from Python
MikiEvents.on('notification', (data) => {
    console.log('Notification:', data);
});

// Send events to Python
MikiEvents.emit('location_changed', { lat: 48.8566, lng: 2.3522 });
```

#### MikiCapacitor

```javascript
// Check platform
MikiCapacitor.isCapacitor()  // true if running in Capacitor
MikiCapacitor.getPlatform()  // "android" | "ios" | "web"

// Check plugin availability
MikiCapacitor.isPluginAvailable('Camera')

// Safe plugin access (returns no-op if unavailable)
const camera = MikiCapacitor.plugins.Camera
```

---

## Next Steps

- [Getting Started Guide](getting-started.md) — Build your first app
- [Deployment Guide](deployment.md) — Deploy your backend
- [Plugin System](plugins.md) — Create custom plugins
- [Security Guide](security.md) — Security best practices
