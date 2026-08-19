# Mobile Build Plan — MikiUI

> **Status:** DESIGN DOC — NOT ACTIVE UNTIL WEB + DESKTOP ARE MATURE
>
> This document is frozen architecture. Mobile work begins only after:
> 1. All base HTML components are implemented and tested
> 2. All advanced widgets (DataGrid, MediaPlayer, DockablePanel, IDE Editor, etc.) are mature
> 3. Web build (`mikiui build --target web`) is stable and production-ready
> 4. Desktop build (`mikiui build --target desktop`) is stable and production-ready
> 5. Plugin system is security-reviewed and marketplace is functional
> 6. CI/CD passes on Linux, Windows, and macOS
>
> Agents must NOT begin mobile implementation until a human explicitly unblocks this phase.

---

## 1. Why Mobile Exists as a Separate Phase

MikiUI's core value proposition is: write Python once, render everywhere. The web and desktop targets already prove this. Mobile is the natural third target, but it introduces constraints (store policies, APK size, embedded interpreters) that do not apply to web or desktop.

Building mobile before web/desktop are mature would:
- Force premature optimization of the static export pipeline
- Risk store-rejection issues before the core framework is stable
- Split engineering effort before the component/widget surface is finalized
- Create bridging code that would need to change as the app/runtime evolves

**Rule:** Mobile is a deployment target, not a feature. It ships when the product is already shippable on web and desktop.

---

## 2. Target Architecture

### 2.1 High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MikiUI Application Layer                         │
│  (app.py — routes, widgets, state, plugins) — ZERO changes per target   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                     ▼
      ┌───────────────┐   ┌──────────────┐   ┌──────────────────────┐
      │   Cloud       │   │  Desktop     │   │  Mobile              │
      │   (web)       │   │  (native)    │   │  (Capacitor)         │
      │               │   │              │   │                      │
      │  Static HTML  │   │  pywebview   │   │  Capacitor WebView   │
      │  + FastAPI    │   │  + local     │   │  + JS Bridge         │
      │  anywhere     │   │  FastAPI     │   │  + Chaquopy (opt-in) │
      └───────────────┘   └──────────────┘   └──────────────────────┘
              ▲                    ▲                     ▲
              │                    │                     │
      ┌───────┴────────┐  ┌───────┴────────┐  ┌────────┴──────────────┐
      │ Browser JS     │  │ pywebview      │  │ Capacitor JS Bridge   │
      │ fetch / HTMX   │  │ evaluate_js    │  │ WebRTC (native)       │
      │ WebSocket      │  │ WebSocket      │  │ Capacitor Plugins     │
      │ Web APIs       │  │ Web APIs       │  │ Chaquopy (Android)    │
      └────────────────┘  └────────────────┘  └───────────────────────┘
```

### 2.2 The Invariant

**One Python codebase. Three deployment wrappers. No platform-specific Python code.**

The same `app.py` produces a web build, a desktop build, and a mobile build. The only thing that changes is the native shell around the static web output.

---

## 3. Backend Modes

### 3.1 Cloud Backend (Default, All Platforms)

- **Frontend:** Static HTML + JS + CSS (from `build_web(mode="separate")`)
- **Backend:** Separately deployed FastAPI app (Railway, Render, Fly.io, Vercel, etc.)
- **Transport:** Standard HTTPS fetch + WebSocket
- **iOS:** Fully supported (no embedded Python)
- **Android:** Fully supported (no embedded Python)
- **APK/IPA size:** ~7-12MB
- **Store compliance:** Clean. No embedded interpreter, no listening sockets.

### 3.2 On-Device Backend (Android Only)

- **Frontend:** Same static HTML + JS + CSS
- **Backend:** Chaquopy embedded CPython inside the APK
- **Transport:** Direct Java→Python bridge via `@JavascriptInterface` (<1ms latency)
- **iOS:** NOT SUPPORTED. Build must fail with a clear error if user selects on-device for iOS.
- **APK size:** ~30-38MB (Chaquopy overhead + Python deps)
- **Store compliance:** Clean on Android when implemented correctly (no listening sockets).

### 3.3 Backend Mode Decision Matrix

| Criterion | Cloud | On-Device (Android) |
|-----------|-------|---------------------|
| APK size | ~8MB | ~33MB |
| Offline capable | No (unless PWA cached) | Yes |
| Python deps available | All (server-side) | Limited by APK size |
| iOS support | Yes | No |
| Store approval risk | None | Low (if no listening sockets) |
| Beginner-friendly | Yes (default) | Intermediate+ |
| Latency | Network-dependent | <1ms bridge |
| Cold start time | N/A (server always on) | 1-3s (Python init) |

**Default is cloud.** On-device is an explicit opt-in for advanced users who need offline capability.

---

## 4. The Bridge Architecture

### 4.1 Design Principle

The frontend must NEVER know which transport is active. The bridge is a transparent abstraction layer.

```javascript
// This single API works in browser, desktop, mobile-cloud, and mobile-ondevice
const users = await MikiBackend.call('GET', '/api/users');
await MikiBackend.call('POST', '/api/login', { username, password });
MikiBackend.subscribe('/ws/chat', (msg) => { ... });
```

### 4.2 Transport Selection Logic

```
MikiBackend.call(method, path, data)
    ├── IS_DESKTOP (pywebview detected)
    │   └── window.pywebview.api.backendCall(method, path, data)
    │       └── Direct Python function call (no HTTP)
    │
    ├── IS_NATIVE (Capacitor detected)
    │   ├── Chaquopy available?
    │   │   └── window.ChaquopyBridge.backendCall(method, path, data)
    │   │       └── @JavascriptInterface → Chaquopy Python
    │   └── No Chaquopy (cloud mode)
    │       └── Standard HTTPS fetch to window.__MIKI_CONFIG__.apiBase
    │
    └── WEB (browser)
        └── Standard HTTPS fetch to same origin
```

### 4.3 Required JS Runtime Files

| File | Purpose | Size |
|------|---------|------|
| `backend_bridge.js` | Unified transport: cloud/desktop/mobile selection | ~8KB |
| `capacitor_bridge.js` | Platform detection, Capacitor plugin initialization | ~15KB |
| `capacitor_features.js` | Capacitor plugin JS wrappers (Camera, Geo, etc.) | ~12KB |
| `websocket_bridge.js` | WebSocket URL selection per platform | ~4KB |
| `event_bridge.js` | Bidirectional JS ↔ Python event bus | ~6KB |

**Total bridge overhead:** ~45KB gzipped. Negligible.

### 4.4 Python Bridge (Chaquopy)

File: `mikiui/app/mobile/ch aquopy_bridge.py`

```python
class ChaquopyBridge:
    """Exposed to Android WebView via @JavascriptInterface."""
    
    def call(self, method: str, path: str, data_json: str) -> str:
        """Direct invocation of MikiApp route handlers.
        
        No HTTP parsing, no socket, no uvicorn.
        Resolves the route and invokes the handler directly.
        Returns JSON-encoded response.
        """
        data = json.loads(data_json) if data_json else None
        route = self._app.get_route(path)
        if route is None:
            return json.dumps({"error": f"No route: {path}", "status": 404})
        
        try:
            nodes, ctx = asyncio.get_event_loop().run_until_complete(
                self._app.invoke(route, request=None, path_params={})
            )
            html = render_fragment(nodes)
            return json.dumps({"html": html, "status": 200})
        except Exception as exc:
            return json.dumps({"error": str(exc), "status": 500})
```

**Kotlin side (auto-generated by build system):**

```kotlin
class MainActivity : BridgeActivity() {
    private lateinit var bridge: ChaquopyBridge
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize Chaquopy
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        
        // Load the user's MikiApp
        val pythonModule = Python.getInstance().getModule("app")
        val mikiApp = pythonModule.callAttr("get_app")
        bridge = ChaquopyBridge(mikiApp)
        
        // Expose to JavaScript
        webView.addJavascriptInterface(object {
            @JavascriptInterface
            fun backendCall(method: String, path: String, dataJson: String): String {
                return bridge.call(method, path, dataJson)
            }
        }, "ChaquopyBridge")
    }
}
```

---

## 5. Backend Separation for Cloud Mode

### 5.1 The Static Export Is Already the Answer

`mikiui build --target web --mode separate` already produces a deployable static frontend:

```
dist/
├── index.html              ← pre-rendered page
├── about.html
├── _miki/
│   ├── runtime/
│   │   ├── htmx.min.js
│   │   ├── alpine.min.js
│   │   ├── miki_ui.js
│   │   ├── miki.css
│   │   └── ...
│   └── themes/
│       ├── light.css
│       └── dracula.css
└── manifest.json
```

All Python components and widgets execute on the server during the build. The mobile bundle contains only the rendered HTML. When the user navigates to `/data`, the WebView loads `data.html` directly from the local filesystem. Zero network request needed for the initial page.

### 5.2 What Still Needs the Backend at Runtime

| Need | How it works | Backend required? |
|------|-------------|-------------------|
| Initial page navigation | Loads pre-rendered `.html` from local files | No |
| HTMX partial updates | `hx-get="/toggle-theme"` → backend returns HTML fragment | Yes |
| Form submissions | `hx-post="/api/login"` → backend processes | Yes |
| WebSocket events | Real-time chat, notifications, live data | Yes |
| Dynamic routes | `/users/123` — not pre-rendered, must fetch from backend | Yes |
| File uploads | POST multipart to backend | Yes |
| Authentication | Session/JWT validation | Yes |

The backend is always a separately deployed FastAPI app. The mobile app never contains Python runtime in cloud mode.

### 5.3 Cloud Deployment Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Cloud (separate deploys)                      │
│                                                                      │
│  ┌──────────────────┐         ┌───────────────────────────────┐     │
│  │  Static Frontend │         │      FastAPI Backend           │     │
│  │  (Vercel/Netlify │         │  (Railway/Render/Fly.io)       │     │
│  │   Cloudflare)    │         │                               │     │
│  │                   │         │  All Python components/        │     │
│  │  dist/ contents   │         │  widgets run here              │     │
│  │  - HTML pages     │         │  - Route handlers              │     │
│  │  - JS runtime     │         │  - WebSocket managers          │     │
│  │  - CSS            │         │  - Plugins                     │     │
│  │                   │         │  - Database (PostgreSQL)       │     │
│  │  Served at:       │         │  - Redis (sessions/WS)         │     │
│  │  https://app.com  │         │                               │     │
│  └────────┬─────────┘         └───────────────────────────────┘     │
│           │                   │  API: https://api.app.com      │     │
│           │ same-origin       │  WS:   wss://api.app.com/ws    │     │
│           │ or CORS           │                               │     │
└───────────┼───────────────────────────────────────────────────────────┘
            │
            │ Capacitor loads from server.url
            ▼
┌───────────────────┐
│   Mobile App      │
│  ┌─────────────┐  │
│  │ Capacitor   │  │
│  │ WebView     │  │
│  │             │  │
│  │ • Loads     │  │
│  │   remote    │  │
│  │   HTML      │  │
│  │ • HTMX →    │  │
│  │   backend   │  │
│  │ • WS →      │  │
│  │   backend   │  │
│  │ • Capacitor │  │
│  │   plugins   │  │
│  └─────────────┘  │
└───────────────────┘
```

### 5.4 Two Cloud Deployment Options

**Option A: Single-origin (recommended for beginners)**

Deploy frontend and backend under one domain:
```
https://myapp.vercel.app/          ← static frontend
https://myapp.vercel.app/api/      ← proxied to FastAPI backend
https://myapp.vercel.app/ws/       ← proxied to FastAPI WebSocket
```

Vercel/Railway can proxy. No CORS needed. HTMX requests work with relative URLs.

**Option B: Separate origins**

```
https://app.vercel.app/             ← frontend
https://api.railway.app/            ← backend
```

Backend must allow CORS from the frontend origin. HTMX requests need absolute URLs (or a `<base>` tag).

For beginners, Option A is simpler. The MikiUI CLI can generate a `vercel.json` or `railway.json` to automate the proxy setup.

---

## 6. WebRTC, Web APIs, and WebSockets

### 6.1 WebRTC

WebRTC runs entirely in the WebView JavaScript context. Python handles signaling only.

```python
# Python — signaling only (never touches media streams)
@app.websocket("/ws/webrtc/{room_id}")
async def webrtc_signaling(ws: WebSocket, room_id: str):
    await ws.accept()
    manager.connect(ws)
    async for raw in ws.iter_text():
        msg = json.loads(raw)
        await manager.broadcast_to_room(room_id, msg)
```

```javascript
// JavaScript — full WebRTC stack (works in all WebViews)
const pc = new RTCPeerConnection({
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
});
const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
stream.getTracks().forEach(t => pc.addTrack(t, stream));
```

**No Python bridge needed for media.** The WebView handles WebRTC natively. Python only relays JSON signaling messages.

**Signaling path by backend mode:**

| Mode | WebSocket URL | Notes |
|------|--------------|-------|
| Cloud | `wss://myapp.vercel.app/ws/webrtc/room1` | Standard STUN/TURN |
| Desktop | `ws://127.0.0.1:8000/ws/webrtc/room1` | Local network peers only |
| Mobile cloud | `wss://myapp.vercel.app/ws/webrtc/room1` | TURN required for cellular |
| Mobile on-device | `ws://127.0.0.1:8080/ws/webrtc/room1` | via Chaquopy bridge → local FastAPI |

For production WebRTC across NATs, TURN server is always required regardless of backend mode.

### 6.2 Web APIs (IoT, Sensors, etc.)

All standard Web APIs work natively in Capacitor's WebView:
- `navigator.geolocation`
- `navigator.mediaDevices`
- `Bluetooth` / `Web Bluetooth`
- `Serial` / `Web Serial`
- `Generic Sensor API`
- `WebUSB`
- `Vibration API`

No bridge code needed. The MikiUI frontend calls these directly from Alpine handlers or HTMX endpoints.

### 6.3 WebSockets

Unified via `MikiBackend.subscribe()`:

| Platform | WebSocket URL | Transport |
|----------|--------------|-----------|
| Web browser | `wss://api.example.com/ws/...` | Standard WebSocket |
| Desktop | `ws://127.0.0.1:8000/ws/...` | Local FastAPI |
| Mobile cloud | `wss://api.example.com/ws/...` | Standard WebSocket |
| Mobile on-device | `ws://127.0.0.1:8080/ws/...` | via Chaquopy bridge |

---

## 7. File Size Budgets

### 7.1 Cloud Mode (Recommended Default)

```
APK/IPA Content                     Size       Notes
─────────────────────────────────────────────────────────
Capacitor runtime (Android)         ~3MB       Standard Capacitor lib
WebView shell (Kotlin/Swift)        ~500KB     Minimal native code
Static frontend (HTML+JS+CSS)       ~5-15MB    Depends on route count
Icons + splash                      ~200KB     Generated by cap sync
─────────────────────────────────────────────────────────
Total (cloud, Android)              ~8-20MB    No Python runtime
Total (cloud, iOS)                  ~7-18MB    No Python runtime
```

### 7.2 On-Device Mode (Android Only)

```
APK Content                              Size       Notes
─────────────────────────────────────────────────────────────
Chaquopy Python 3.11 (stripped)         ~22MB      Minimum; cannot be removed
ChaquoPy runtime loader                 ~2MB       Required
FastAPI + pydantic core                 ~4MB       User's backend deps
uvicorn (minimal embedded)              ~1.5MB     Async server
mikiui runtime JS+CSS                   ~300KB     HTMX, Alpine, bridges
Capacitor runtime (Android)             ~3MB       Standard Capacitor lib
Native Activity shell                   ~500KB     Minimal Kotlin
Icons + splash                          ~200KB     Generated by cap sync
─────────────────────────────────────────────────────────────
Total (on-device, Android, minimal)     ~33MB      Within Play Store 150MB limit
Total (on-device, + pillow + numpy)     ~45MB      Still within limit
```

### 7.3 Size Optimization Rules

1. **APK splits:** Generate per-ABI APKs (`arm64-v8a`, `armeabi-v7a`). Do not ship universal APK.
2. **Chaquopy dependency selection:** Only include pip packages explicitly listed in `mobile.chaquopy_deps`. No auto-install.
3. **Static asset optimization:** Minify CSS, gzip JS, use content hashes for cache busting.
4. **Tree-shaking:** The web build already excludes unused routes. Ensure Capacitor only copies `www/` contents, not build tooling.

---

## 8. Store Compliance

### 8.1 Play Store (Android)

| Requirement | Implementation | Status |
|-------------|---------------|--------|
| APK ≤ 150MB | Cloud: ~8-20MB. On-device: ~33-45MB with ABI splits | ✅ |
| No hidden background services | Chaquopy runs on-demand via bridge calls. No foreground service. | ✅ |
| No listening ports on localhost | On-device uses Chaquopy bridge (direct function call). Cloud has no local server. | ✅ |
| Permissions declared | Auto-generated `AndroidManifest.xml` from `plugins` list | ✅ |
| Target API level | Build config targets API 34 (Android 14) | ✅ |
| 64-bit required | `arm64-v8a` ABI included by default | ✅ |

**CRITICAL: Never open a listening socket on Android.** Google Play flags this as a policy violation. The on-device backend must use the Chaquopy bridge exclusively.

### 8.2 App Store (iOS)

| Requirement | Implementation | Status |
|-------------|---------------|--------|
| No embedded scripting engines | Cloud mode only on iOS. No embedded Python. | ✅ |
| No downloading executable code | All code in IPA bundle or loaded from HTTPS | ✅ |
| Privacy manifest required | Auto-generated from `plugins` list | ✅ |
| Background modes declared | None by default; user opts in via `plugins` | ✅ |
| ATS compliance | Cloud mode uses HTTPS exclusively | ✅ |

**iOS and embedded Python:** Apple has rejected apps embedding Python interpreters. Cloud-only mode on iOS completely sidesteps this. Build must enforce this at the CLI level.

---

## 9. Plugin System and Mobile Integration

### 9.1 Capability Declaration

Python plugins declare what native features they need:

```python
class CameraPlugin(Plugin):
    name = "camera"
    capabilities = ["camera", "filesystem"]
```

### 9.2 Auto-Mapping to Capacitor Plugins

| Python Capability | Capacitor Plugin | Android Permission | iOS Privacy Key |
|------------------|------------------|-------------------|-----------------|
| `camera` | `Camera` | `CAMERA` | `NSCameraUsageDescription` |
| `geolocation` | `Geolocation` | `ACCESS_FINE_LOCATION` | `NSLocationWhenInUseUsageDescription` |
| `push` | `PushNotifications` | `POST_NOTIFICATIONS` | `UIBackgroundModes` |
| `local-notify` | `LocalNotifications` | None | None |
| `haptics` | `Haptics` | None | None |
| `clipboard` | `Clipboard` | None | None |
| `filesystem` | `Filesystem` | `READ/WRITE_EXTERNAL_STORAGE` | None |
| `share` | `Share` | None | None |
| `network-status` | `Network` | `ACCESS_NETWORK_STATE` | None |
| `status-bar` | `StatusBar` | None | None |

The mobile build scans all registered plugins, collects their `capabilities`, maps them to Capacitor plugins, and auto-generates:
- `capacitor.config.json` plugins section
- `AndroidManifest.xml` permissions
- `ios/App/Info.plist` privacy descriptions

**No manual native configuration needed.**

---

## 10. CLI Surface

### 10.1 New Commands

```bash
# Build mobile project (cloud mode, default)
mikiui build --target mobile

# Build with on-device backend (Android only)
mikiui build --target mobile --backend ondevice

# Build for specific platform
mikiui build --target mobile --target-platform android
mikiui build --target mobile --target-platform ios

# Build and run on connected device/emulator
mikiui mobile run --target android
mikiui mobile run --target ios

# Open native project in IDE
mikiui mobile open --target android   # Android Studio
mikiui mobile open --target ios      # Xcode

# List available Capacitor plugins
mikiui mobile plugins

# Show current mobile config
mikiui mobile info
```

### 10.2 Updated Existing Commands

```bash
# build command gains --target mobile
mikiui build --target web        # unchanged
mikiui build --target desktop    # unchanged
mikiui build --target mobile     # NEW

# dev command gains --mobile flag for Capacitor live reload
mikiui dev --mobile              # NEW: starts dev server + Capacitor live reload
```

---

## 11. CI/CD Integration

### 11.1 Required Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `mobile-build.yml` | PR touching `mikiui/build/mobile_*` or `mikiui/runtime/*bridge.js` | Smoke test: generate Capacitor project, verify structure |
| `mobile-android.yml` | Push to `main` (scheduled or manual) | Build debug APK, run unit tests via Chaquopy |
| `mobile-ios.yml` | Push to `main` (macOS runner only) | Build iOS simulator, run JS unit tests |

### 11.2 Mobile Build Smoke Test

```yaml
# .github/workflows/mobile-build.yml
- name: Mobile build smoke test
  run: |
    python -c "from mikiui.build.mobile_build import build_mobile; print('Mobile build import OK')"
    python -c "
      from mikiui import MikiApp, Div
      from mikiui.app.mobile import MobileConfig
      from mikiui.build.mobile_build import build_mobile
      
      app = MikiApp(title='Test', mobile=MobileConfig(backend='cloud'))
      @app.route('/')
      def home(): return Div('Hello')
      
      report = build_mobile(app, target='android', backend='cloud', out_dir='/tmp/mobile_test')
      assert report['status'] == 'ok'
      assert (Path('/tmp/mobile_test') / 'capacitor.config.json').exists()
      assert (Path('/tmp/mobile_test') / 'www' / 'index.html').exists()
    "
```

### 11.3 On-Device Build (Android)

Requires macOS or Linux runner with Android SDK. Uses `mobile-img` Docker or GitHub Actions `android-build` action.

```yaml
- name: Build Android APK (on-device mode)
  uses: reactivecircus/android-emulator-runner@v2
  with:
    api-level: 34
    script: |
      cd dist_mobile
      npx cap sync android
      cd android && ./gradlew assembleDebug
```

---

## 12. Security Model

### 12.1 Threat Model

| Threat | Mitigation |
|--------|-----------|
| Malicious plugin accesses device APIs without permission | Capability declaration required; build validates against `PluginSecurityConfig` |
| Chaquopy bridge exposed to malicious JS | `@JavascriptInterface` is annotation-gated; only exposed methods are callable |
| Man-in-the-middle on cloud backend | Enforce HTTPS. WSS for WebSockets. Certificate pinning optional (advanced). |
| Data exfiltration via Capacitor plugins | Plugins are opt-in via `plugins` list. No plugin is enabled by default. |
| Code injection via route handlers | Existing plugin validator + AST vetting covers this |
| Play Store policy violation | CI lint step checks: no `ServerSocket` in mobile build output, no listening ports in Kotlin code |

### 12.2 Security Guardrails for Mobile Build

1. **No listening sockets in on-device mode.** The build system must scan generated Kotlin code for `ServerSocket`, `ServerSocketChannel`, or `socket.bind` and fail the build if found.
2. **Capacitor plugins are opt-in.** No plugin is enabled unless explicitly listed in `MobileConfig.plugins` or required by a registered plugin's `capabilities`.
3. **HTTPS enforced for cloud mode.** The generated Capacitor config must not allow cleartext in cloud mode. Only on-device mode sets `cleartext: true` (and only for `localhost`).
4. **iOS on-device mode is a build error.** If `target` includes `ios` and `backend == "ondevice"`, the build must fail with a clear message before generating any files.
5. **Chaquopy dependencies are explicit.** No automatic pip install. The `chaquopy_deps` list is the sole source of truth for what gets bundled.

---

## 13. Testing Strategy

### 13.1 Unit Tests (Python)

| Module | Tests Required |
|--------|---------------|
| `mikiui/build/mobile_build.py` | Cloud mode output structure, on-device mode output structure, iOS on-device rejection, plugin mapping |
| `mikiui/app/mobile.py` | `MobileConfig` validation, default values |
| `mikiui/runtime/backend_bridge.js` | Transport selection logic, fallback paths |
| `mikiui/runtime/capacitor_features.js` | Plugin API wrappers, fallback to Web APIs |

### 13.2 Integration Tests

| Test | How |
|------|----|
| Cloud mobile build | Generate project, verify `capacitor.config.json`, verify `www/` contents, verify permissions in `AndroidManifest.xml` |
| On-device mobile build | Generate project, verify `mobile_backend.py` exists, verify Chaquopy bridge Kotlin code, verify no listening sockets |
| iOS cloud build | Generate project, verify `Info.plist` permissions match `plugins` list |
| WebRTC signaling | WebSocket relay test: two clients connect, exchange SDP/ICE, verify no Python media handling |
| Bridge latency | On-device: measure JS→Chaquopy→JS round-trip. Target: <5ms p99 |
| Large project static export | Build app with 100+ routes, verify all pages rendered, verify build time < 60s |

### 13.3 E2E Tests (Playwright)

Run against Capacitor's `@capacitor/browser` or a real device farm (BrowserStack/Sauce Labs):

- App launches and loads initial page
- Navigation between pre-rendered pages works offline
- HTMX partial updates work (cloud mode)
- WebSocket chat works (cloud mode)
- Camera plugin opens and returns photo (native device)
- Push notification permission request works (native device)

---

## 14. Migration Path from Web/Desktop

### 14.1 For Existing MikiUI Apps

Existing apps need zero code changes to build for mobile:

```python
# app.py — unchanged
from mikiui import MikiApp, Div, DataGrid

app = MikiApp(title="My App")

@app.route("/")
def home():
    return Div(DataGrid(...))
```

The user adds mobile config:

```python
from mikiui.app.mobile import MobileConfig

app = MikiApp(
    title="My App",
    mobile=MobileConfig(
        backend="cloud",  # or "ondevice"
        plugins=["Camera"],  # optional
    ),
)
```

Then builds:

```bash
mikiui build --target mobile
```

### 14.2 Progressive Enhancement

1. **Phase 1:** Cloud mode works. App is a web wrapper.
2. **Phase 2:** User adds `plugins=["Camera"]`. Next build auto-includes Capacitor Camera plugin and native permissions.
3. **Phase 3:** User switches to `backend="ondevice"`. Next build includes Chaquopy and embedded Python. No route handler changes needed.

---

## 15. Dependencies and Prerequisites

### 15.1 Build-Time (User's Machine)

| Dependency | Required For | Version | Notes |
|-----------|-------------|---------|-------|
| Node.js | All mobile builds | >= 18 | Installs Capacitor, syncs native projects |
| npm | All mobile builds | >= 9 | Comes with Node.js |
| Android Studio | Android native build | Latest | Only needed for native compilation |
| Xcode | iOS native build | Latest | macOS only |
| Chaquopy | Android on-device | Latest | Auto-installed by Gradle plugin |

### 15.2 Runtime (Mobile App)

| Dependency | Cloud Mode | On-Device Mode |
|-----------|-----------|---------------|
| Capacitor runtime | ~3MB | ~3MB |
| Chaquopy Python | 0MB | ~24MB |
| User's pip deps | 0MB | Variable (~2-10MB each) |

### 15.3 No New Python Dependencies

Mobile build adds no required Python dependencies to `pyproject.toml`. All mobile-specific tooling is Node.js-based (Capacitor) or Gradle-based (Chaquopy).

Optional dependency group:

```toml
[project.optional-dependencies]
mobile = [
    # No Python deps required for cloud mode.
    # On-device mode uses Chaquopy (installed via Gradle, not pip).
]
```

---

## 16. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Google Play rejects on-device APK | Low | High | Never use listening sockets. Use Chaquopy bridge only. Test with internal app sharing before production. |
| Apple rejects app (cloud mode) | Very Low | High | Cloud mode has no embedded interpreter. Follow standard Capacitor practices. |
| APK size exceeds 150MB | Medium | High | Enforce ABI splits. Warn at build time if size > 100MB. Document `chaquopy_deps` impact per package. |
| WebRTC doesn't work in WKWebView | Low | Medium | Test on real devices. Both WKWebView (iOS 15+) and Android WebView support WebRTC natively. |
| Bridge latency causes UI jank | Low | Medium | Benchmark p99 latency. Keep Python handlers async. Avoid blocking calls in Chaquopy bridge. |
| Capacitor plugin version conflicts | Medium | Low | Pin Capacitor and plugin versions in generated `package.json`. Document upgrade path. |
| iOS cloud mode CORS issues | Low | Low | Enforce single-origin deployment or auto-configure CORS in generated FastAPI setup. |

---

## 17. Guardrails — When Mobile Work Can Begin

Mobile implementation is **blocked** until all of the following are true:

- [ ] All base HTML components are implemented and tested
- [ ] All advanced widgets are mature (DataGrid, MediaPlayer, DockablePanel, IDE Editor)
- [ ] `mikiui build --target web` is stable and production-ready
- [ ] `mikiui build --target desktop` is stable and production-ready
- [ ] Plugin system is security-reviewed and marketplace is functional
- [ ] CI/CD passes on Linux, Windows, and macOS
- [ ] No critical bugs open against web/desktop builds

**Agents must check this list before starting any mobile work. If any item is unchecked, stop and report back.**

---

## 18. Implementation Order (Once Unblocked)

1. **`mikiui/runtime/backend_bridge.js`** — unified transport layer
2. **`mikiui/runtime/websocket_bridge.js`** — WebSocket URL selection
3. **`mikiui/app/mobile.py`** — `MobileConfig` dataclass
4. **`mikiui/build/mobile_build.py`** — Capacitor project generation (cloud mode first)
5. **`mikiui/build/mobile_cli.py`** — `mobile build/run/open` commands
6. **`mikiui/runtime/capacitor_bridge.js`** — platform detection
7. **`mikiui/runtime/capacitor_features.js`** — Capacitor plugin wrappers
8. **`mikiui/app/mobile/ch aquopy_bridge.py`** — Chaquopy Python bridge
9. **`mikiui/build/mobile_build.py`** — on-device mode (after cloud is stable)
10. **`mikiui/backend/server.py`** — Capacitor CORS origins
11. **`mikiui/cli/commands.py`** — register `mobile_cli`
12. **Docs + examples + CI workflows**

---

## 19. Success Metrics

| Metric | Target |
|--------|--------|
| Cloud mode APK size | < 12MB |
| On-device mode APK size | < 40MB |
| Bridge latency (on-device) | < 5ms p99 |
| Build time (mobile, cloud) | < 30s |
| Build time (mobile, on-device) | < 120s (includes Chaquopy) |
| Store approval rate | 100% first submission |
| Beginner setup time | < 5 minutes from `mikiui new` to `mikiui build --target mobile` |
| Plugin capability coverage | 100% of common Capacitor plugins mapped |

---

## 20. Open Questions (To Resolve Before Implementation)

1. **Should we support offline-first cloud mode?** (local HTML + remote API, with service worker caching) — defer to post-MVP.
2. **Should we auto-deploy the backend?** (`mikiui deploy` command) — defer to post-MVP.
3. **Should we support Windows on-device?** (not Chaquopy, but maybe a separate bridge) — defer; research needed.
4. **Should we bundle a TURN server?** — No. Users bring their own TURN (standard WebRTC practice).
5. **Should we support push notifications in cloud mode?** — Yes, via Capacitor PushNotifications plugin. No Python bridge needed.

---

## 21. References

- Capacitor docs: https://capacitorjs.com/docs
- Chaquopy docs: https://chaquo.com/chaquopy/doc/current/
- Android APK size limits: https://developer.android.com/google/play/requirements
- iOS App Store guidelines: https://developer.apple.com/app-store/review/guidelines/
- WebRTC in WebView: https://webrtc.org/testing
