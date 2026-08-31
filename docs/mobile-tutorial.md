# Mobile Tutorial: Build a Photo Share App

This tutorial walks you through building a complete mobile app with MikiUI.
By the end, you'll have a photo-sharing app with camera access, GPS location,
offline support, and push notifications.

## What We're Building

**PhotoShare** - A simple app where users can:
- Take photos with the camera
- Add location data to photos
- View photos offline
- Share photos with others
- Get notified when friends share photos

## Step 1: Create the Project

```bash
# Install MikiUI
pip install mikiui

# Create a new project
mikiui new photoshare && cd photoshare
```

## Step 2: Write the App

Replace `app.py` with:

```python
from mikiui import MikiApp, Div, H1, H2, P, Button, Card, Img
from mikiui.components import Form, Input, Tabs, Alert
from mikiui.app.mobile import MobileConfig

app = MikiApp(
    title="PhotoShare",
    mobile=MobileConfig(
        backend="cloud",
        api_base="https://photoshare-api.railway.app",
        target_platform="both",
        plugins=[
            "Camera",
            "Geolocation",
            "Push",
            "Share",
            "NetworkStatus",
            "StatusBar",
        ],
        app_id="com.example.photoshare",
        app_name="PhotoShare",
        background_color="#f8fafc",
    ),
)

# In-memory photo store (replace with database in production)
photos = []


@app.route("/", title="Home")
def home():
    return Div(
        H1("PhotoShare"),
        P("Share moments with friends."),
        Button("Take Photo", onclick="takePhoto()", class_="miki-btn-primary w-full"),
        Button("View Gallery", onclick="window.location='/gallery'", class_="miki-btn-secondary w-full mt-2"),
        Div(id="status", class="mt-4"),
        class_="p-4 space-y-4",
    )


@app.route("/gallery", title="Gallery")
def gallery():
    items = []
    for photo in reversed(photos[-20:]):  # Last 20 photos
        items.append(Card(
            Img(src=photo.get("thumbnail", ""), class="w-full rounded"),
            P(photo.get("caption", "No caption"), class="text-sm mt-2"),
            P(photo.get("location", "Unknown location"), class="text-xs text-gray-500"),
            Button("Share", onclick=f"sharePhoto('{photo['id']}')", class_="miki-btn-sm mt-2"),
            class="p-2",
        ))

    return Div(
        H1("Gallery"),
        P(f"{len(photos)} photos"),
        Div(*items, class="grid grid-cols-2 gap-4"),
        Button("Back", onclick="window.location='/'", class_="miki-btn-secondary mt-4"),
        class_="p-4",
    )


@app.route("/settings", title="Settings")
def settings():
    return Div(
        H1("Settings"),
        Tabs([
            ("General", Div(
                P("Notifications: On"),
                P("Dark Mode: Auto"),
                P("Location: On"),
                class_="p-4",
            )),
            ("Account", Div(
                P("Signed in as: user@example.com"),
                Button("Sign Out", class="miki-btn-secondary mt-2"),
                class_="p-4",
            )),
            ("About", Div(
                H2("PhotoShare"),
                P("Version 1.0.0"),
                P("Built with MikiUI"),
                class_="p-4",
            )),
        ]),
        Button("Back", onclick="window.location='/'", class="miki-btn-secondary mt-4"),
        class_="p-4",
    )


@app.post("/api/photos")
def add_photo(caption: str = "", location: str = "", thumbnail: str = ""):
    """Add a new photo."""
    import uuid
    photo = {
        "id": str(uuid.uuid4()),
        "caption": caption,
        "location": location,
        "thumbnail": thumbnail,
        "created_at": __import__("datetime").datetime.now().isoformat(),
    }
    photos.append(photo)
    return photo


@app.get("/api/photos")
def list_photos():
    """List all photos."""
    return photos


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "photos": len(photos)}
```

## Step 3: Add Mobile JavaScript

Create `mobile.js` in your project root:

```javascript
// PhotoShare Mobile Features

// Take a photo with camera
async function takePhoto() {
    try {
        // Check camera permission
        const granted = await MikiPermissions.request("camera");
        if (!granted) {
            alert("Camera permission is required to take photos.");
            return;
        }

        // Take the photo
        const photo = await MikiFeatures.takePhoto({
            quality: 80,
            allowEditing: true,
            resultType: "dataUrl"
        });

        // Get location
        let location = "Unknown location";
        try {
            const pos = await MikiFeatures.getCurrentPosition();
            location = `${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`;
        } catch (e) {
            console.log("Location not available:", e);
        }

        // Get caption
        const caption = prompt("Add a caption:");

        // Save to server
        await MikiBackend.post("/api/photos", {
            caption: caption || "",
            location: location,
            thumbnail: photo.dataUrl
        });

        // Haptic feedback
        MikiFeatures.hapticImpact("medium");

        // Show success
        alert("Photo saved!");
        window.location = "/gallery";

    } catch (err) {
        console.error("Failed to take photo:", err);
        alert("Failed to take photo: " + err.message);
    }
}

// Share a photo
async function sharePhoto(photoId) {
    try {
        const photos = await MikiBackend.get("/api/photos");
        const photo = photos.find(p => p.id === photoId);
        if (!photo) return;

        await MikiFeatures.shareContent({
            title: "Check out this photo!",
            text: photo.caption || "Shared from PhotoShare",
        });

        MikiFeatures.hapticSelection();
    } catch (err) {
        console.error("Failed to share:", err);
    }
}

// Update network status
function updateNetworkStatus() {
    const status = document.getElementById("status");
    if (!status) return;

    MikiFeatures.getNetworkStatus().then(s => {
        if (!s.connected) {
            status.innerHTML = '<div class="miki-alert miki-alert-warning">You are offline. Changes will sync when connected.</div>';
        }
    });
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    // Set status bar
    MikiFeatures.setStatusBarStyle("dark");

    // Check network
    updateNetworkStatus();
    MikiFeatures.onNetworkChange(s => updateNetworkStatus());

    // Register for push notifications (if supported)
    MikiFeatures.isNative().then(isNative => {
        if (isNative) {
            MikiFeatures.registerForPush()
                .then(() => MikiFeatures.getPushToken())
                .then(token => {
                    // Send token to backend
                    MikiBackend.post("/api/devices", { token });
                })
                .catch(err => console.log("Push not available:", err));
        }
    });
});
```

## Step 4: Build for Mobile

```bash
# Build the mobile project
mikiui mobile build

# Navigate to the output
cd dist_mobile

# Install dependencies
npm install

# Install Capacitor plugins
npm install @capacitor/camera @capacitor/geolocation @capacitor/push-notifications @capacitor/share @capacitor/network @capacitor/status-bar

# Sync plugins to native projects
npx cap sync
```

## Step 5: Run on Device

### Android

```bash
# Open in Android Studio
npx cap open android

# In Android Studio:
# 1. Wait for Gradle sync to complete
# 2. Connect your phone or start an emulator
# 3. Click the green "Run" button
```

### iOS (macOS only)

```bash
# Open in Xcode
npx cap open ios

# In Xcode:
# 1. Select your signing team
# 2. Connect your phone or select a simulator
# 3. Click the "Play" button
```

## Step 6: Add Offline Support

Update `mobile.js` to add offline support:

```javascript
// Offline support
async function savePhotoOffline(photoData) {
    // Queue for sync when online
    await MikiData.queue({
        type: "POST",
        url: "/api/photos",
        data: photoData
    });

    // Save locally
    await MikiData.append("pending_photos", photoData);
}

async function syncPhotos() {
    if (!navigator.onLine) return;

    const result = await MikiData.sync(async (operation) => {
        await fetch(operation.url, {
            method: operation.type,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(operation.data)
        });
    });

    if (result.synced > 0) {
        alert(`Synced ${result.synced} photos!`);
    }
}

// Enable auto-sync
MikiData.enableAutoSync(async (operation) => {
    const response = await fetch(operation.url, {
        method: operation.type,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(operation.data)
    });
    if (!response.ok) throw new Error("Sync failed");
}, 30000);  // Sync every 30 seconds
```

## Step 7: Deploy the Backend

### Option A: Railway (Easiest)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create a new project
railway init

# Deploy
railway up

# Get your URL
railway domain
```

### Option B: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Option C: Docker

```bash
cd dist_mobile/deploy
docker build -t photoshare-api .
docker run -p 8000:8000 photoshare-api
```

## Step 8: Update Backend URL

After deploying, update `capacitor.config.json`:

```json
{
  "appId": "com.example.photoshare",
  "appName": "PhotoShare",
  "webDir": "www",
  "server": {
    "url": "https://your-app.railway.app",
    "cleartext": false
  }
}
```

Then re-sync:

```bash
npx cap sync
```

## Step 9: Add Push Notifications

### Setup FCM (Android)

1. Go to https://console.firebase.google.com/
2. Create a new project
3. Add Android app with package `com.example.photoshare`
4. Download `google-services.json`
5. Place in `android/app/google-services.json`
6. Copy the Server key from Project Settings > Cloud Messaging

### Setup APNs (iOS)

1. Go to https://developer.apple.com/
2. Certificates, Identifiers & Profiles > Keys
3. Create key with APNs enabled
4. Download .p8 file
5. Note Key ID and Team ID

### Configure Backend

```bash
export FCM_SERVER_KEY="your_fcm_key"
export APNS_KEY_PATH="/path/to/AuthKey.p8"
export APNS_KEY_ID="YOUR_KEY_ID"
export APNS_TEAM_ID="YOUR_TEAM_ID"
```

## Step 10: Publish to Stores

### Android (Play Store)

```bash
# Generate signed bundle
cd dist_mobile
npx cap open android

# In Android Studio:
# Build > Generate Signed Bundle/APK > Android App Bundle
# Upload to https://play.google.com/console
```

### iOS (App Store)

```bash
cd dist_mobile
npx cap open ios

# In Xcode:
# Product > Archive > Distribute App
# Upload to https://appstoreconnect.apple.com
```

## Complete File Structure

```
photoshare/
├── app.py                 # Main app with routes
├── mobile.js              # Mobile-specific JavaScript
├── requirements.txt       # Python dependencies
├── dist_mobile/           # Generated mobile project
│   ├── capacitor.config.json
│   ├── package.json
│   ├── android/           # Android project
│   ├── ios/               # iOS project
│   ├── www/               # Web assets
│   │   ├── index.html
│   │   └── _miki/runtime/
│   │       ├── backend_bridge.js
│   │       ├── capacitor_features.js
│   │       ├── mobile_data.js
│   │       ├── mobile_app.js
│   │       └── mobile_permissions.js
│   └── deploy/            # Deployment configs
│       ├── vercel.json
│       ├── railway.json
│       └── Dockerfile
└── README.md
```

## Summary

You've built a complete mobile app with:
- Camera access for taking photos
- GPS location tagging
- Offline support with automatic sync
- Push notifications
- Share functionality
- Network status monitoring

## Next Steps

- [Mobile Guide](mobile.md) - Complete mobile documentation
- [API Reference](api-reference.md) - Full API docs
- [Plugins Guide](mobile.md#plugins-guide) - All available plugins
- [Push Notifications](mobile.md#push-notifications) - Detailed push setup
- [Offline Support](mobile.md#offline-support) - Offline-first patterns
