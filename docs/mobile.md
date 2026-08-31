# Mobile Development with MikiUI

Build **iOS and Android apps** entirely in Python. MikiUI generates a
Capacitor project that wraps your web app in a native shell.

**No Swift, Kotlin, or JavaScript required** — just Python.

---

## Table of Contents

1. [Quick Start](#quick-start) - Get running in 5 minutes
2. [Prerequisites](#prerequisites) - What you need installed
3. [Installation](#installation) - Install MikiUI
4. [Configuration](#configuration) - Configure your app for mobile
5. [Building](#building) - Build your mobile project
6. [Running](#running) - Run on device or emulator
7. [Native Features](#native-features) - Camera, GPS, push, etc.
8. [Plugins Guide](#plugins-guide) - How to install Capacitor plugins
9. [Push Notifications](#push notifications) - Setup FCM and APNs
10. [Offline Support](#offline-support) - Work without internet
11. [Deployment](#deployment) - Deploy your backend
12. [Publishing](#publishing) - Submit to App Store and Play Store
13. [Troubleshooting](#troubleshooting) - Common issues and fixes
14. [API Reference](#api-reference) - Complete API docs

---

## Quick Start

Get a mobile app running in 5 minutes:

```bash
# 1. Install MikiUI
pip install mikiui

# 2. Create a new project
mikiui new myapp && cd myapp

# 3. Write your app
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
        P("This app was built entirely in Python."),
        Button("Take Photo", onclick="takePhoto()"),
        class_="p-4 text-center",
    )
EOF

# 4. Build for mobile
mikiui mobile build

# 5. Install Capacitor plugins
cd dist_mobile
npm install
npm install @capacitor/camera @capacitor/geolocation
npx cap sync

# 6. Open in Android Studio or Xcode
npx cap open android  # or npx cap open ios
```

---

## Prerequisites

### Required for All Platforms

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.14+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| npm | 9+ | Comes with Node.js |

### For Android Development

| Tool | Version | Download |
|------|---------|----------|
| Android Studio | Latest | https://developer.android.com/studio |
| Java JDK | 17+ | https://adoptium.net |
| Android SDK | API 23+ | Via Android Studio |

**Set ANDROID_HOME:**
```bash
# Windows
set ANDROID_HOME=C:\Users\YourName\AppData\Local\Android\Sdk

# macOS/Linux
export ANDROID_HOME=$HOME/Android/Sdk
```

### For iOS Development (macOS only)

| Tool | Version | Download |
|------|---------|----------|
| Xcode | Latest | Mac App Store |
| Xcode CLI Tools | Latest | `xcode-select --install` |
| Apple Developer Account | - | $99/year |

### Verify Your Setup

```bash
mikiui mobile doctor
```

This checks all required tools and tells you what's missing.

---

## Installation

### Install MikiUI

```bash
pip install mikiui
```

### Install Optional Extras

```bash
# For Tailwind CSS support
pip install mikiui[tailwind]

# For desktop app support
pip install mikiui[desktop]

# For all extras
pip install mikiui[dev,build,desktop,tailwind]
```

### Verify Installation

```bash
mikiui --version
```

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

        # WebSocket URL (optional)
        ws_base="wss://my-api.railway.app/ws",

        # Target platforms
        target_platform="both",  # "android", "ios", or "both"

        # Native features (auto-generates permissions)
        plugins=["Camera", "Geolocation", "Push", "Biometrics"],

        # App identifiers
        app_id="com.example.myapp",
        app_name="My App",

        # UI settings
        orientation="default",  # "portrait", "landscape", or "default"
        background_color="#ffffff",
        splash_duration=3000,

        # On-device mode (Android only)
        chaquopy_deps=["fastapi", "pydantic"],

        # Android settings
        min_sdk=23,
        target_sdk=34,
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
| `plugins` | `list[str]` | `[]` | Native plugins to include |
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

## Building

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

### What Gets Generated

```
dist_mobile/
├── capacitor.config.json   # Capacitor configuration
├── package.json            # Node.js dependencies
├── android/                # Android native project
│   ├── app/
│   │   └── src/main/
│   │       ├── AndroidManifest.xml
│   │       ├── res/xml/network_security_config.xml
│   │       └── java/.../MainActivity.kt
│   └── chaquopy.gradle     # (on-device only)
├── ios/                    # iOS native project
│   ├── App/
│   │   ├── Info.plist
│   │   └── PrivacyInfo.xcprivacy
│   └── Podfile
├── bridge/                 # (on-device only)
│   ├── chaquopy_bridge.py
│   └── kotlin/
├── www/                    # Your web app
│   ├── index.html
│   ├── manifest.webmanifest
│   └── _miki/runtime/
│       ├── backend_bridge.js
│       ├── capacitor_bridge.js
│       ├── capacitor_features.js
│       ├── websocket_bridge.js
│       ├── event_bridge.js
│       ├── mobile_data.js
│       ├── mobile_app.js
│       ├── mobile_permissions.js
│       └── mobile_deeplink.js
└── deploy/                 # Deployment configs
    ├── vercel.json
    ├── railway.json
    ├── netlify.toml
    ├── Dockerfile
    ├── docker-compose.yml
    ├── push_endpoint.py
    └── deeplink_handler.py
```

### After Building

```bash
cd dist_mobile

# Install npm dependencies
npm install

# Install Capacitor plugins (see Plugins Guide below)
npm install @capacitor/camera @capacitor/geolocation

# Sync web assets to native projects
npx cap sync

# Open in IDE
npx cap open android  # Android Studio
npx cap open ios      # Xcode
```

---

## Running

### Development with Live Reload

```bash
# Start dev server with mobile live reload
mikiui dev --mobile --mobile-target android
```

### Run on Device/Emulator

```bash
# Build and run
mikiui mobile run --target android
mikiui mobile run --target ios

# Run on specific device
mikiui mobile run --target android --device "emulator-5554"
```

### Manual Steps

```bash
cd dist_mobile

# Run on Android
npx cap run android

# Run on iOS
npx cap run ios

# Live reload during development
npx cap run android --livereload --external
```

---

## Native Features

### Available Plugins

| Plugin | Description | Android Permission | iOS Privacy Key |
|--------|-------------|-------------------|-----------------|
| `Camera` | Take photos, scan codes | `CAMERA` | Camera description |
| `Geolocation` | GPS location | Location permissions | Location description |
| `Push` | Push notifications | `POST_NOTIFICATIONS` | Background modes |
| `LocalNotifications` | Local notifications | Exact alarm | None |
| `Haptics` | Vibration feedback | None | None |
| `Clipboard` | Copy/paste | None | None |
| `Filesystem` | Read/write files | Storage permissions | None |
| `Share` | System share sheet | None | None |
| `NetworkStatus` | Network monitoring | Network state | None |
| `StatusBar` | Status bar control | None | None |
| `Biometrics` | Face ID, fingerprint | Biometric | Face ID description |
| `Keyboard` | Keyboard control | None | None |
| `MediaPlayer` | Audio playback | Wake lock | Microphone |
| `NFC` | NFC tag reading | NFC | NFC description |
| `Bluetooth` | Bluetooth LE | Bluetooth permissions | Bluetooth description |
| `Contacts` | Address book | Contact permissions | Contacts description |
| `Calendar` | Calendar events | Calendar permissions | Calendar description |
| `FilePicker` | File selection | Storage | None |
| `PhotoGallery` | Photo library | Media images | Photo library description |
| `InAppPurchase` | In-app purchases | Billing | None |

---

## Plugins Guide

### How to Install Capacitor Plugins

Capacitor plugins provide access to native device features. Each plugin you
list in `MobileConfig.plugins` requires the corresponding npm package.

### Step 1: Install the Plugin

```bash
cd dist_mobile

# Official Capacitor plugins
npm install @capacitor/camera
npm install @capacitor/geolocation
npm install @capacitor/push-notifications
npm install @capacitor/local-notifications
npm install @capacitor/haptics
npm install @capacitor/clipboard
npm install @capacitor/filesystem
npm install @capacitor/share
npm install @capacitor/network
npm install @capacitor/status-bar
npm install @capacitor/biometrics
npm install @capacitor/keyboard
npm install @capacitor/device
npm install @capacitor/screen-orientation
npm install @capacitor/safe-area
npm install @capacitor/browser

# Community plugins
npm install @capacitor-community/native-audio
npm install @capacitor-community/nfc
npm install @capacitor-community/contacts
npm install @capacitor-community/calendar
npm install @capacitor-community/file-picker
npm install @capacitor-community/purchases
npm install @capacitor-community/photos
```

### Step 2: Sync the Plugin

```bash
npx cap sync
```

### Step 3: Use in JavaScript

```javascript
// Camera
const photo = await MikiFeatures.takePhoto({ quality: 90 });

// Geolocation
const pos = await MikiFeatures.getCurrentPosition();

// Notifications
await MikiFeatures.scheduleNotification({
    title: "Hello!",
    body: "This is a notification",
    id: 1
});

// Biometrics
const available = await MikiFeatures.isBiometricsAvailable();
if (available) {
    await MikiFeatures.authenticateWithBiometrics('Verify your identity');
}
```

### Plugin Installation Quick Reference

```bash
# All official plugins (copy-paste ready)
npm install \
  @capacitor/camera \
  @capacitor/geolocation \
  @capacitor/push-notifications \
  @capacitor/local-notifications \
  @capacitor/haptics \
  @capacitor/clipboard \
  @capacitor/filesystem \
  @capacitor/share \
  @capacitor/network \
  @capacitor/status-bar \
  @capacitor/biometrics \
  @capacitor/keyboard \
  @capacitor/device \
  @capacitor/screen-orientation \
  @capacitor/safe-area \
  @capacitor/browser

# All community plugins (copy-paste ready)
npm install \
  @capacitor-community/native-audio \
  @capacitor-community/nfc \
  @capacitor-community/contacts \
  @capacitor-community/calendar \
  @capacitor-community/file-picker \
  @capacitor-community/purchases \
  @capacitor-community/photos
```

---

## Native Features in Detail

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

**Plugin:** `@capacitor/camera`

### Geolocation

```javascript
// Get current position
const pos = await MikiFeatures.getCurrentPosition();
console.log(pos.coords.latitude, pos.coords.longitude);

// Watch position changes
const watchId = await MikiFeatures.watchPosition({}, (pos, err) => {
    if (pos) console.log('Moved to:', pos.coords);
});

// Stop watching
await MikiFeatures.clearWatch(watchId);
```

**Plugin:** `@capacitor/geolocation`

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

// Get pending notifications
const pending = await MikiFeatures.getPendingNotifications();
```

**Plugin:** `@capacitor/local-notifications`

### Push Notifications

```javascript
// Register for push notifications
await MikiFeatures.registerForPush();

// Get device token (send this to your backend)
const token = await MikiFeatures.getPushToken();

// Listen for incoming notifications
MikiFeatures.onPushReceived((notification) => {
    console.log('Push received:', notification);
});

// Listen for notification actions (user tapped notification)
MikiFeatures.onPushAction((action) => {
    console.log('User tapped:', action);
});
```

**Plugin:** `@capacitor/push-notifications`

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

**Plugin:** `@capacitor/biometrics`

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

const language = await MikiFeatures.getDeviceLanguage();
console.log(language.value);  // "en-US"

const deviceId = await MikiFeatures.getDeviceId();
console.log(deviceId.identifier);  // Unique device ID
```

**Plugin:** `@capacitor/device`

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

// Check if playing
const isPlaying = await MikiFeatures.isAudioPlaying('click');

// Cleanup
await MikiFeatures.unloadAudio('click');
```

**Plugin:** `@capacitor-community/native-audio`

### Clipboard

```javascript
await MikiFeatures.copyToClipboard('Hello World');
const text = await MikiFeatures.readClipboard();
```

**Plugin:** `@capacitor/clipboard`

### Share

```javascript
await MikiFeatures.shareContent({
    title: 'Check this out!',
    text: 'My awesome app',
    url: 'https://example.com',
    files: [photo.path]  // optional files
});

// Check if sharing is available
const canShare = await MikiFeatures.canShare();
```

**Plugin:** `@capacitor/share`

### Haptics

```javascript
MikiFeatures.hapticImpact('medium');  // 'light' | 'medium' | 'heavy'
MikiFeatures.hapticVibrate(300);       // milliseconds
MikiFeatures.hapticSelection();        // selection click
```

**Plugin:** `@capacitor/haptics`

### Screen Orientation

```javascript
await MikiFeatures.lockOrientation('portrait');  // or 'landscape'
await MikiFeatures.unlockOrientation();
const orientation = await MikiFeatures.getOrientation();
```

**Plugin:** `@capacitor/screen-orientation`

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

**Plugin:** Built into Capacitor (no install needed)

### Contacts

```javascript
// Request permission first
const granted = await MikiFeatures.requestContactsPermission();
if (!granted) return;

// Get all contacts
const contacts = await MikiFeatures.getContacts();

// Pick a single contact
const picked = await MikiFeatures.pickContact();

// Create a new contact
await MikiFeatures.createContact({
    firstName: 'John',
    lastName: 'Doe',
    phoneNumbers: [{ label: 'mobile', number: '+1234567890' }]
});

// Delete a contact
await MikiFeatures.deleteContact(contactId);
```

**Plugin:** `@capacitor-community/contacts`

### Calendar

```javascript
// Request permission first
const granted = await MikiFeatures.requestCalendarPermission();
if (!granted) return;

// Create an event
await MikiFeatures.createCalendarEvent({
    title: 'Team Meeting',
    location: 'Office',
    notes: 'Weekly sync',
    startDate: new Date(),
    endDate: new Date(Date.now() + 3600000),
    isAllDay: false
});

// Get events in range
const events = await MikiFeatures.getCalendarEvents(
    new Date('2024-01-01'),
    new Date('2024-12-31')
);

// Delete an event
await MikiFeatures.deleteCalendarEvent(eventId);

// Open calendar app
await MikiFeatures.openCalendar(Date.now());
```

**Plugin:** `@capacitor-community/calendar`

### File Picker

```javascript
// Pick any file
const file = await MikiFeatures.pickFile({
    types: ['image/*', 'application/pdf'],
    multiple: false
});

// Pick photos
const photos = await MikiFeatures.pickPhotos({ multiple: true });
const singlePhoto = await MikiFeatures.pickPhoto();

// Pick videos
const videos = await MikiFeatures.pickVideos({ multiple: true });
const singleVideo = await MikiFeatures.pickVideo();
```

**Plugin:** `@capacitor-community/file-picker`

### NFC

```javascript
// Check if NFC is available
const available = await MikiFeatures.isNfcAvailable();
if (!available) return;

// Start scanning
const sub = await MikiFeatures.startNfcScan((tag) => {
    console.log('Tag scanned:', tag);
    sub.remove();  // Stop after first scan
});

// Read a tag
const tag = await MikiFeatures.readNfcTag();

// Write to a tag
await MikiFeatures.writeNfcTag({ message: 'Hello NFC' });

// Format a tag
await MikiFeatures.formatNfcTag({ message: 'Formatted' });
```

**Plugin:** `@capacitor-community/nfc`

### In-App Purchases

```javascript
// Configure with your Revenue Cat API key
await MikiFeatures.configurePurchases('your_revenuecat_api_key');

// Get available products
const products = await MikiFeatures.getProducts();

// Purchase a product
await MikiFeatures.purchaseProduct('premium_monthly');

// Purchase a package
await MikiFeatures.purchasePackage('premium_monthly_package');

// Restore purchases
await MikiFeatures.restorePurchases();

// Get customer info
const info = await MikiFeatures.getCustomerInfo();

// Sync purchases
await MikiFeatures.syncPurchases();
```

**Plugin:** `@capacitor-community/purchases`

### Bluetooth

```javascript
// Request a device
const device = await MikiFeatures.requestBluetoothDevice({
    filters: [{ services: ['battery_service'] }],
    optionalServices: ['battery_service']
});

// Connect
const server = await MikiFeatures.connectBluetoothDevice(device);

// Read a characteristic
const value = await MikiFeatures.readBluetoothCharacteristic(
    batteryService,
    'battery_level'
);

// Write a characteristic
await MikiFeatures.writeBluetoothCharacteristic(
    batteryService,
    'battery_level',
    new Uint8Array([100])
);

// Disconnect
await MikiFeatures.disconnectBluetoothDevice(device);
```

**Plugin:** Uses Web Bluetooth API (no install needed)

### SMS / Call / Email / Maps

```javascript
// Send SMS
await MikiFeatures.sendSms('+1234567890', 'Hello!');

// Make a phone call
await MikiFeatures.callPhoneNumber('+1234567890');

// Send email
await MikiFeatures.sendEmail('user@example.com', 'Subject', 'Body');

// Open maps
await MikiFeatures.openMaps('1600 Amphitheatre Parkway', 37.4221, -122.0841);
await MikiFeatures.openMaps('Google HQ');  // By address
```

**Plugin:** Uses URL schemes (no install needed)

### Dark Mode

```javascript
// Check if dark mode is active
const isDark = MikiFeatures.isDarkMode();

// Listen for dark mode changes
MikiFeatures.onDarkModeChange((isDark) => {
    document.body.classList.toggle('dark', isDark);
});

// Set background color (updates theme-color meta tag)
MikiFeatures.setBackgroundColor('#1a1a1a');
```

**Plugin:** Uses CSS media queries (no install needed)

---

## Push Notifications

### Overview

Push notifications require:
1. **FCM** (Firebase Cloud Messaging) for Android
2. **APNs** (Apple Push Notification service) for iOS
3. A server endpoint to send notifications

### Step 1: Add Push to Your App

```python
from mikiui.app.mobile import MobileConfig

app = MikiApp(
    title="My App",
    mobile=MobileConfig(
        plugins=["Push"],  # Add this
    ),
)
```

### Step 2: Build and Install Plugin

```bash
mikiui mobile build
cd dist_mobile
npm install @capacitor/push-notifications
npx cap sync
```

### Step 3: Configure FCM (Android)

1. Go to https://console.firebase.google.com/
2. Create a new project
3. Add an Android app with your package name
4. Download `google-services.json`
5. Place it in `android/app/google-services.json`
6. Go to Project Settings → Cloud Messaging
7. Copy the Server key

### Step 4: Configure APNs (iOS)

1. Go to https://developer.apple.com/
2. Certificates, Identifiers & Profiles → Keys
3. Create a new key with APNs enabled
4. Download the .p8 file
5. Note the Key ID and Team ID

### Step 5: Deploy Backend with Push Endpoint

```bash
# The push endpoint is auto-generated
cd dist_mobile/deploy
# Copy push_endpoint.py to your backend
cp push_endpoint.py /path/to/your/backend/api/push.py
```

### Step 6: Set Environment Variables

```bash
# FCM (Android)
export FCM_SERVER_KEY="your_fcm_server_key"

# APNs (iOS)
export APNS_KEY_PATH="/path/to/AuthKey_XXXXX.p8"
export APNS_KEY_ID="YOUR_KEY_ID"
export APNS_TEAM_ID="YOUR_TEAM_ID"
```

### Step 7: Register Device in JavaScript

```javascript
// Register for push
await MikiFeatures.registerForPush();

// Get token
const token = await MikiFeatures.getPushToken();

// Send token to your backend
await fetch('/api/push/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        token: token,
        platform: MikiApp.getPlatform()  // "android" or "ios"
    })
});

// Listen for notifications
MikiFeatures.onPushReceived((notification) => {
    console.log('Received:', notification.title, notification.body);
});
```

### Step 8: Send Notifications from Python

```python
from mikiui.backend import send_push_notification

# Send to Android
send_push_notification(
    token="device_fcm_token",
    title="Hello!",
    body="You have a new message",
    fcm_server_key="your_fcm_server_key",
)

# Send to iOS
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

---

## Offline Support

MikiUI includes an offline-first data layer (`MikiData`) that automatically
syncs when the connection is restored.

### Basic Usage

```javascript
// Store data locally
await MikiData.set('user', { name: 'John', age: 30 });

// Retrieve data
const user = await MikiData.get('user');

// Check if data exists
const hasUser = await MikiData.has('user');

// Delete data
await MikiData.delete('user');

// Clear all data
await MikiData.clear();
```

### Offline Queue

```javascript
// Queue an operation when offline
await MikiData.queue({
    type: 'POST',
    url: '/api/users',
    data: { name: 'John' }
});

// Get pending queue
const queue = await MikiData.getQueue();

// Clear queue
await MikiData.clearQueue();
```

### Sync When Online

```javascript
// Sync pending operations
const result = await MikiData.sync(async (operation) => {
    const response = await fetch(operation.url, {
        method: operation.type,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(operation.data)
    });
    if (!response.ok) throw new Error('Sync failed');
});

console.log(`Synced: ${result.synced}, Failed: ${result.failed}`);
```

### Auto-Sync

```javascript
// Enable automatic sync every 30 seconds
const stopSync = MikiData.enableAutoSync(async (operation) => {
    await fetch(operation.url, {
        method: operation.type,
        body: JSON.stringify(operation.data)
    });
}, 30000);

// Stop auto-sync
stopSync();
```

### Cache with Expiration

```javascript
// Cache data for 5 minutes
await MikiData.setCache('api_response', data, 5 * 60 * 1000);

// Get cached data (returns null if expired)
const cached = await MikiData.cache('api_response', 5 * 60 * 1000);
```

### Batch Operations

```javascript
// Get multiple keys
const data = await MikiData.getMany(['user', 'settings', 'posts']);

// Set multiple keys
await MikiData.setMany({
    user: { name: 'John' },
    settings: { theme: 'dark' },
    posts: []
});

// Increment a counter
const newCount = await MikiData.increment('view_count');

// Append to an array
const posts = await MikiData.append('posts', { title: 'New Post' });

// Remove from an array
const filtered = await MikiData.removeFromArray('posts', p => p.id === 123);
```

---

## Deployment

### Cloud Mode Backend

Your cloud-mode backend needs to be hosted separately. MikiUI generates
deployment configs for popular platforms:

#### Railway (Recommended for Beginners)

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

#### Docker Compose (Full Stack)

```bash
cd dist_mobile/deploy
docker compose up -d
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

## Publishing

### App Store (iOS)

1. **Build for release:**
   ```bash
   cd dist_mobile && npx cap open ios
   ```
2. **In Xcode:**
   - Select your signing team
   - Product → Archive
   - Distribute App → App Store Connect
3. **App Store Connect:**
   - Create new app record
   - Upload screenshots (required sizes: 6.5", 5.5", iPad Pro)
   - Fill in description, keywords, privacy policy
   - Submit for review

### Play Store (Android)

1. **Build for release:**
   ```bash
   cd dist_mobile && npx cap open android
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

### Using the Publish Command

```bash
# Prepare for publishing
mikiui mobile publish --platform android --release
mikiui mobile publish --platform ios --release
```

This generates:
- Store listing metadata
- Screenshot templates
- Step-by-step instructions

---

## On-Device Mode

On-device mode runs Python directly on the Android device via Chaquopy.
No server needed — works offline.

### Setup

```python
MobileConfig(
    backend="ondevice",
    target_platform="android",  # iOS not supported
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
| Build fails | Run `mikiui mobile doctor` |

### Plugin Not Working

If a native feature doesn't work:

1. **Verify the plugin is installed:**
   ```bash
   cd dist_mobile
   npm list @capacitor/plugin-name
   ```

2. **Re-sync after installing:**
   ```bash
   npx cap sync
   ```

3. **Check the plugin is in your config:**
   ```python
   MobileConfig(plugins=["PluginName"])
   ```

4. **Rebuild the project:**
   ```bash
   npx cap sync
   npx cap open android  # or ios
   ```

### Permission Denied

If a feature says "permission denied":

1. **Request permission first:**
   ```javascript
   const granted = await MikiFeatures.requestPermission('camera');
   if (!granted) {
       // Guide user to settings
       await MikiFeatures.openSettings();
   }
   ```

2. **Check the permission is in AndroidManifest.xml:**
   ```xml
   <uses-permission android:name="android.permission.CAMERA" />
   ```

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
| `MikiData` | Offline data persistence |
| `MikiApp` | App lifecycle management |
| `MikiPermissions` | Runtime permission requests |
| `MikiDeepLink` | Deep link routing |
| `MikiConnection` | Network status monitoring |

### Python Push API

```python
from mikiui.backend import send_push_notification, send_bulk_push_notifications

# Single notification
send_push_notification(
    token="device_token",
    title="Hello!",
    body="You have a message",
    fcm_server_key="...",  # For Android
)

# Bulk notifications
send_bulk_push_notifications(
    tokens=["token1", "token2"],
    title="Hello!",
    body="You have a message",
    fcm_server_key="...",
)
```
