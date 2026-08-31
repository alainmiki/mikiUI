# Mobile Automation Guide

MikiUI provides complete automation for building, testing, signing, and
publishing mobile apps. This guide covers all the automated workflows.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Native Project Generation](#native-project-generation)
3. [Plugin Installation & Sync](#plugin-installation--sync)
4. [Device Testing](#device-testing)
5. [Code Signing](#code-signing)
6. [Store Submission](#store-submission)
7. [Full Automation Pipeline](#full-automation-pipeline)

---

## Quick Start

The fastest way to get your mobile app running:

```bash
# One command to build, install plugins, and run on emulator
mikiui mobile all --platform android

# Or step by step:
mikiui mobile build
mikiui mobile sync
mikiui mobile test --platform android
```

---

## Native Project Generation

MikiUI automatically generates all native project files that Capacitor needs
but doesn't create by default.

### What Gets Generated

#### Android
```
android/
├── app/
│   ├── build.gradle              # App-level build config
│   └── src/main/
│       ├── AndroidManifest.xml   # Permissions, activities
│       ├── java/com/.../MainActivity.kt  # Main activity
│       └── res/
│           ├── values/
│           │   ├── strings.xml   # App name, package
│           │   └── colors.xml    # Theme colors
│           ├── xml/
│           │   └── network_security_config.xml
│           └── mipmap-anydpi-v26/
│               └── ic_launcher.xml  # Adaptive icon
└── chaquopy.gradle               # (on-device only)
```

#### iOS
```
ios/
├── App/
│   ├── App/
│   │   └── AppDelegate.swift     # App delegate
│   └── Info.plist                # Permissions, config
└── Podfile                       # CocoaPods dependencies
```

### Usage

```bash
# Build generates native files automatically
mikiui mobile build

# Or generate native files separately
mikiui mobile build --target android
```

### MainActivity.kt (Android)

The generated `MainActivity.kt` includes:
- Package declaration matching your `app_id`
- Capacitor `BridgeActivity` integration
- Plugin registration for all enabled capabilities
- Chaquopy initialization (on-device mode)

```kotlin
package com.example.myapp

import android.os.Bundle
import com.getcapacitor.BridgeActivity
import com.getcapacitor.Plugin

class MainActivity : BridgeActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        registerPlugins(arrayOf<Class<out Plugin>>(
            // Plugins auto-registered based on capabilities
        ))
    }
}
```

### AppDelegate.swift (iOS)

The generated `AppDelegate.swift` includes:
- UIApplicationDelegate methods
- Capacitor integration
- URL handling for deep links
- Status bar tap handling

---

## Plugin Installation & Sync

### Automatic Plugin Installation

MikiUI reads your `MobileConfig.plugins` and installs all required Capacitor
plugins automatically.

```bash
# Install all plugins and sync
mikiui mobile sync
```

This runs:
1. `npm install` - Base dependencies
2. `npm install @capacitor/plugin-name` - Each required plugin
3. `npx cap sync` - Sync to native projects

### Manual Plugin Installation

If you prefer to install plugins manually:

```bash
cd dist_mobile

# Install plugins
npm install @capacitor/camera
npm install @capacitor/geolocation
npm install @capacitor/push-notifications

# Sync to native projects
npx cap sync
```

### Plugin Mapping

| Capability | NPM Package |
|------------|-------------|
| Camera | `@capacitor/camera` |
| Geolocation | `@capacitor/geolocation` |
| Push | `@capacitor/push-notifications` |
| Local Notifications | `@capacitor/local-notifications` |
| Haptics | `@capacitor/haptics` |
| Clipboard | `@capacitor/clipboard` |
| Filesystem | `@capacitor/filesystem` |
| Share | `@capacitor/share` |
| Network | `@capacitor/network` |
| Status Bar | `@capacitor/status-bar` |
| Biometrics | `@capacitor/biometrics` |
| Keyboard | `@capacitor/keyboard` |
| Device | `@capacitor/device` |
| Screen Orientation | `@capacitor/screen-orientation` |
| Safe Area | `@capacitor/safe-area` |
| Browser | `@capacitor/browser` |
| Media Player | `@capacitor-community/native-audio` |
| NFC | `@capacitor-community/nfc` |
| Contacts | `@capacitor-community/contacts` |
| Calendar | `@capacitor-community/calendar` |
| File Picker | `@capacitor-community/file-picker` |
| Purchases | `@capacitor-community/purchases` |

---

## Device Testing

### List Available Devices

```bash
# List Android devices and emulators
mikiui mobile devices --platform android

# List iOS simulators and devices
mikiui mobile devices --platform ios
```

### Run on Emulator/Simulator

```bash
# Android emulator
mikiui mobile test --platform android --type emulator

# iOS simulator
mikiui mobile test --platform ios --type simulator
```

### Run on Physical Device

```bash
# Android device
mikiui mobile test --platform android --type device

# iOS device
mikiui mobile test --platform ios --type device
```

### Run on Specific Device

```bash
# List devices first
mikiui mobile devices --platform android

# Run on specific device
mikiui mobile test --platform android --device "emulator-5554"
```

### Live Reload During Development

```bash
# Start dev server with mobile live reload
mikiui dev --mobile --mobile-target android

# Or use Capacitor's live reload
cd dist_mobile
npx cap run android --livereload --external
```

---

## Code Signing

### Android Code Signing

#### Automatic Setup

```bash
# Generate keystore and configure signing
mikiui mobile sign --platform android
```

This:
1. Generates a release keystore (if not exists)
2. Configures `build.gradle` with signing config
3. Provides build instructions

#### Manual Setup

```bash
# Generate keystore manually
keytool -genkey -v \
  -keystore release.keystore \
  -keyalg RSA -keysize 2048 \
  -validity 10000 \
  -alias release

# Configure signing
mikiui mobile sign --platform android \
  --keystore release.keystore \
  --keystore-pass your_password \
  --key-alias release \
  --key-pass your_password
```

#### Build Release APK/AAB

```bash
cd dist_mobile/android

# Build release APK
./gradlew assembleRelease

# Build release AAB (for Play Store)
./gradlew bundleRelease
```

### iOS Code Signing

#### Automatic Setup

```bash
# Configure code signing
mikiui mobile sign --platform ios --team-id YOUR_TEAM_ID
```

This:
1. Creates `ExportOptions.plist`
2. Provides archive instructions

#### Manual Setup

1. Open Xcode: `npx cap open ios`
2. Select your signing team
3. Project → Signing & Capabilities → Team

#### Build Release IPA

```bash
cd dist_mobile/ios

# Build archive
xcodebuild -workspace App.xcworkspace \
  -scheme App \
  -configuration Release \
  -archivePath build/App.xcarchive \
  archive

# Export IPA
xcodebuild -exportArchive \
  -archivePath build/App.xcarchive \
  -exportPath build \
  -exportOptionsPlist ExportOptions.plist
```

---

## Store Submission

### Prepare for Submission

```bash
# Android
mikiui mobile submit --platform android

# iOS
mikiui mobile submit --platform ios
```

This:
1. Builds the release version
2. Generates store listing metadata
3. Creates screenshot templates
4. Provides submission instructions

### Android (Play Store)

1. **Prepare:**
   ```bash
   mikiui mobile submit --platform android
   ```

2. **Upload:**
   - Go to https://play.google.com/console
   - Create a new app or select existing
   - Upload the AAB file from `android/app/build/outputs/bundle/release/`

3. **Store Listing:**
   - See `dist_mobile/store/android/` for templates
   - Required screenshots: 1080x1920 (phone), 1024x1600 (7" tablet), 1200x1920 (10" tablet)
   - Feature graphic: 1024x500

4. **Submit for Review**

### iOS (App Store)

1. **Prepare:**
   ```bash
   mikiui mobile submit --platform ios
   ```

2. **Upload:**
   - Open Xcode Organizer
   - Select the archive
   - Click "Distribute App"
   - Select "App Store Connect"

3. **Store Listing:**
   - See `dist_mobile/store/ios/` for templates
   - Required screenshots: 1290x2796 (6.5"), 1284x2778 (5.5"), 2048x2732 (iPad)

4. **Submit for Review**

---

## Full Automation Pipeline

### One-Command Build & Run

```bash
# Build, install plugins, and run on emulator
mikiui mobile all --platform android

# Build, install plugins, and run on iOS simulator
mikiui mobile all --platform ios --type simulator

# Build for both platforms
mikiui mobile all --platform both
```

### What It Does

1. **Build** - Generates the mobile project
2. **Native Files** - Creates MainActivity.kt, AppDelegate.swift, etc.
3. **Plugins** - Installs all required Capacitor plugins
4. **Sync** - Runs `npx cap sync`
5. **Run** - Launches on the specified device/emulator

### CI/CD Integration

```yaml
# .github/workflows/mobile.yml
name: Mobile Build

on:
  push:
    branches: [main]

jobs:
  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
      - uses: actions/setup-node@v4
        with:
          node-version: "18"
      - run: pip install -e ".[build]"
      - run: mikiui mobile build --target android
      - run: cd dist_mobile && npm install && npx cap sync
      - run: cd dist_mobile/android && ./gradlew bundleRelease
      - uses: actions/upload-artifact@v4
        with:
          name: android-aab
          path: dist_mobile/android/app/build/outputs/bundle/release/*.aab

  build-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
      - uses: actions/setup-node@v4
        with:
          node-version: "18"
      - run: pip install -e ".[build]"
      - run: mikiui mobile build --target ios
      - run: cd dist_mobile && npm install && npx cap sync
      - run: |
          cd dist_mobile/ios
          xcodebuild -workspace App.xcworkspace \
            -scheme App \
            -configuration Release \
            -archivePath build/App.xcarchive \
            archive
```

---

## Troubleshooting

### Build Issues

| Problem | Solution |
|---------|----------|
| `npm install` fails | Check Node.js version (18+) |
| `npx cap sync` fails | Run `npm install` first |
| Gradle sync fails | Check Android Studio is installed |
| Xcode build fails | Check Xcode is installed |

### Device Issues

| Problem | Solution |
|---------|----------|
| No emulators listed | Create one in Android Studio |
| Device not detected | Enable USB debugging |
| App crashes on launch | Check `adb logcat` for errors |

### Signing Issues

| Problem | Solution |
|---------|----------|
| Keystore not found | Run `mikiui mobile sign --platform android` |
| Signing config error | Check `build.gradle` has `signingConfigs` |
| iOS signing failed | Select team in Xcode |

---

## Next Steps

- [Mobile Guide](mobile.md) - Complete mobile documentation
- [Mobile Tutorial](mobile-tutorial.md) - Step-by-step photo app tutorial
- [API Reference](api-reference.md) - Complete API docs
