"""Mobile build system for MikiUI — generates Capacitor projects.

Supports two backend modes:
- **Cloud mode** (default): Static web frontend + remote FastAPI backend.
- **On-device mode** (Android only): Embedded CPython via Chaquopy.

The build process:
1. Generate static web frontend (via web_build).
2. Create Capacitor project structure.
3. Copy static assets to `www/`.
4. Generate `capacitor.config.json`.
5. Generate native project files (AndroidManifest.xml, Info.plist).
6. Map plugin capabilities to native permissions.
"""

from __future__ import annotations

import json
import os
import textwrap
from typing import Any

from ..app.mobile import CAPABILITY_MAP, MobileConfig


def build_mobile(
    app: Any,
    out_dir: str = "dist_mobile",
    backend: str | None = None,
    target_platform: str | None = None,
    mobile_config: MobileConfig | None = None,
) -> dict[str, Any]:
    """Build a mobile project from a MikiApp.

    :param app: The MikiApp instance.
    :param out_dir: Output directory for the mobile project.
    :param backend: Override backend mode (``"cloud"`` or ``"ondevice"``).
    :param target_platform: Override target platform (``"android"``, ``"ios"``, ``"both"``).
    :param mobile_config: Full mobile config (alternative to individual params).
    :returns: Build report dict.
    """
    # Resolve config
    config = mobile_config
    if config is None:
        config = getattr(app, "mobile", None)
        if config is None:
            from ..app.mobile import MobileConfig
            config = MobileConfig()

    if backend:
        config.backend = backend
    if target_platform:
        config.target_platform = target_platform

    # Validate
    _validate_config(config)

    # Step 0: Auto-collect capabilities from registered plugins
    registered_plugins = getattr(app, "plugins", [])
    if registered_plugins:
        config.collect_capabilities_from_plugins(registered_plugins)

    # Step 1: Generate static web frontend
    from .web_build import build_web

    web_out = os.path.join(out_dir, "www")
    web_report = build_web(
        app,
        mode="separate",
        out_dir=web_out,
        framework=getattr(app, "style_framework", "plain"),
        style_mode=getattr(app, "style_mode", "cdn"),
        theme=getattr(app, "theme", "light"),
        daisyui=getattr(app, "style_daisyui", False),
    )

    # Step 2: Generate Capacitor config
    capacitor_config = _generate_capacitor_config(app, config)
    config_path = os.path.join(out_dir, "capacitor.config.json")
    os.makedirs(out_dir, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(capacitor_config, f, indent=2)

    # Step 3: Generate package.json for Capacitor
    package_json = _generate_package_json(config)
    with open(os.path.join(out_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)

    # Step 4: Generate native project files
    if config.targets_android():
        _generate_android_project(config, out_dir)

    if config.targets_ios():
        _generate_ios_project(config, out_dir)

    # Step 5: Generate on-device bridge if needed
    if config.is_ondevice():
        _generate_ondevice_bridge(config, out_dir)

    # Step 6: Generate PWA manifest, mobile HTML template, icons, deployment, permissions, data, push, deeplink
    _generate_pwa_manifest(config, out_dir)
    _generate_mobile_html_template(config, out_dir)
    _generate_deployment_configs(config, out_dir)
    _generate_app_icons(config, out_dir)
    _generate_mobile_error_pages(config, out_dir)
    _generate_permission_helper(config, out_dir)
    _generate_data_layer(config, out_dir)
    _generate_push_endpoint(config, out_dir)
    _generate_deep_link_handler(config, out_dir)

    # Step 7: Security scan
    security_warnings = _security_scan(out_dir)

    # Step 8: Size budget check
    size_warnings = _check_size_budget(config, out_dir)
    security_warnings.extend(size_warnings)

    return {
        "status": "ok",
        "out_dir": os.path.abspath(out_dir),
        "backend": config.backend,
        "platforms": config.target_platform,
        "web_report": web_report,
        "capacitor_config": capacitor_config,
        "security_warnings": security_warnings,
    }


def _validate_config(config: MobileConfig) -> None:
    """Validate mobile config and raise on errors."""
    # Basic validation is done in MobileConfig.__post_init__
    # This function validates build-specific constraints
    if config.is_ondevice() and not config.targets_android():
        raise ValueError("On-device mode is only supported on Android.")


def _security_scan(out_dir: str) -> list[str]:
    """Scan generated files for security issues.

    Returns a list of warnings found.
    """
    import re

    warnings: list[str] = []
    dangerous_patterns = {
        r"ServerSocket\(": "Listening socket detected (ServerSocket)",
        r"ServerSocketChannel\(": "Listening socket detected (ServerSocketChannel)",
        r"\.bind\(\(InetAddress": "Socket bind detected",
        r"DatagramSocket\(": "Datagram socket detected",
        r"eval\(": "Dangerous eval() detected",
        r"exec\(": "Dangerous exec() detected",
        r"os\.system\(": "Dangerous os.system() detected",
        r"subprocess\.": "Subprocess usage detected",
    }

    for root, _dirs, files in os.walk(out_dir):
        for fname in files:
            if fname.endswith((".py", ".kt", ".java", ".js")):
                path = os.path.join(root, fname)
                try:
                    with open(path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    for pattern, description in dangerous_patterns.items():
                        if re.search(pattern, content):
                            warnings.append(f"{description} in {path}")
                except OSError:
                    pass

    return warnings


def _generate_capacitor_config(app: Any, config: MobileConfig) -> dict[str, Any]:
    """Generate capacitor.config.json content."""
    app_name = config.app_name or getattr(app, "title", "MikiUI App")
    app_id = config.app_id

    # Build plugins section from capabilities and plugins list
    plugins_section: dict[str, Any] = {}

    # First add from explicit capabilities
    for cap in config.capabilities:
        cap_info = CAPABILITY_MAP.get(cap)
        if cap_info:
            plugin_name = cap_info.get("capacitor_plugin", "").replace("@capacitor/", "")
            if plugin_name:
                plugins_section[plugin_name] = {}

    # Then add from plugins list (by name)
    for plugin_name in config.plugins:
        cap = plugin_name.lower().replace("-", "_").replace(" ", "_")
        cap_info = CAPABILITY_MAP.get(cap)
        if cap_info:
            plugin = cap_info.get("capacitor_plugin", "").replace("@capacitor/", "")
            if plugin and plugin not in plugins_section:
                plugins_section[plugin] = {}

    capacitor_config: dict[str, Any] = {
        "appId": app_id,
        "appName": app_name,
        "webDir": "www",
        "server": {},
        "plugins": {
            "SplashScreen": {
                "launchShowDuration": config.splash_duration,
                "backgroundColor": config.background_color,
                "showSpinner": True,
            },
            "StatusBar": {
                "style": "DEFAULT",
                "backgroundColor": config.background_color,
            },
        },
    }

    # Add capability-derived plugins
    capacitor_config["plugins"].update(plugins_section)

    # Deep linking configuration
    if "deep-link" in config.capabilities or "deep-link" in config.plugins:
        capacitor_config["server"]["allowNavigation"] = [
            config.api_base or "*",
        ]
        # Android: App Links
        # iOS: Universal Links
        capacitor_config["plugins"]["App"] = {
            "deepLinkConfig": {
                "schemes": [config.app_id.split(".")[-1]],
            }
        }

    # Server configuration for cloud mode
    if config.is_cloud():
        if config.api_base:
            capacitor_config["server"]["url"] = config.api_base
            capacitor_config["server"]["cleartext"] = config.api_base.startswith("http://")
        capacitor_config["server"]["androidScheme"] = "https"
    else:
        # On-device: allow cleartext for localhost bridge
        capacitor_config["server"]["cleartext"] = True
        capacitor_config["server"]["androidScheme"] = "http"

    # Orientation
    if config.orientation != "default":
        capacitor_config["server"]["orientation"] = config.orientation

    # Background color
    capacitor_config["backgroundColor"] = config.background_color

    return capacitor_config


def _generate_package_json(config: MobileConfig) -> dict[str, Any]:
    """Generate package.json for the Capacitor project."""
    dev_dependencies: dict[str, str] = {
        "@capacitor/cli": "^6.0.0",
        "@capacitor/core": "^6.0.0",
    }

    # Add platform-specific Capacitor packages
    if config.targets_android():
        dev_dependencies["@capacitor/android"] = "^6.0.0"
    if config.targets_ios():
        dev_dependencies["@capacitor/ios"] = "^6.0.0"

    # Add plugin packages
    for plugin in config.get_capacitor_plugins():
        dev_dependencies[plugin] = "latest"

    return {
        "name": config.app_id.split(".")[-1],
        "version": "1.0.0",
        "description": f"MikiUI mobile app ({config.backend} mode)",
        "private": True,
        "scripts": {
            "build": "npx cap sync",
            "android": "npx cap open android",
            "ios": "npx cap open ios",
        },
        "devDependencies": dev_dependencies,
    }


def _generate_android_project(config: MobileConfig, out_dir: str) -> None:
    """Generate Android native project files."""
    android_dir = os.path.join(out_dir, "android")
    os.makedirs(android_dir, exist_ok=True)

    # AndroidManifest.xml
    permissions = config.get_android_permissions()
    permission_lines = []
    for perm in permissions:
        permission_lines.append(f'    <uses-permission android:name="{perm}" />')

    # Add maxSdkVersion for WRITE_EXTERNAL_STORAGE (deprecated on API 29+)
    if "android.permission.WRITE_EXTERNAL_STORAGE" in permissions:
        permission_lines.append(
            '    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" '
            f'android:maxSdkVersion="{max(config.min_sdk, 28)}" />'
        )

    # On-device: add INTERNET and network permissions
    if config.is_ondevice():
        extra_perms = [
            "android.permission.INTERNET",
            "android.permission.ACCESS_NETWORK_STATE",
        ]
        for p in extra_perms:
            if p not in permissions:
                permission_lines.append(f'    <uses-permission android:name="{p}" />')

    # Camera: add features
    features_lines = []
    if "camera" in config.capabilities:
        features_lines.append(
            '    <uses-feature android:name="android.hardware.camera" '
            'android:required="false" />'
        )
        features_lines.append(
            '    <uses-feature android:name="android.hardware.camera.autofocus" '
            'android:required="false" />'
        )

    manifest = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <manifest xmlns:android="http://schemas.android.com/apk/res/android">
        {chr(10).join(permission_lines)}
        {chr(10).join(features_lines)}

            <application
                android:allowBackup="true"
                android:icon="@mipmap/ic_launcher"
                android:label="@string/app_name"
                android:roundIcon="@mipmap/ic_launcher_round"
                android:supportsRtl="true"
                android:theme="@style/AppTheme"
                android:usesCleartextTraffic="{'true' if config.allow_cleartext else 'false'}"
                android:networkSecurityConfig="@xml/network_security_config">

                <activity
                    android:configChanges="orientation|keyboardHidden|keyboard|screenSize|locale|smallestScreenSize|screenLayout|uiMode"
                    android:name=".MainActivity"
                    android:label="@string/app_name"
                    android:theme="@style/AppTheme.NoActionBarLaunch"
                    android:launchMode="singleTask"
                    android:exported="true">

                    <intent-filter>
                        <action android:name="android.intent.action.MAIN" />
                        <category android:name="android.intent.category.LAUNCHER" />
                    </intent-filter>

                </activity>

                <provider
                    android:name="androidx.core.content.FileProvider"
                    android:authorities="${{applicationId}}.fileprovider"
                    android:exported="false"
                    android:grantUriPermissions="true">
                    <meta-data
                        android:name="android.support.FILE_PROVIDER_PATHS"
                        android:resource="@xml/file_paths" />
                </provider>
            </application>
        </manifest>
    """)

    with open(os.path.join(android_dir, "AndroidManifest.xml"), "w", encoding="utf-8") as f:
        f.write(manifest)

    # Generate network security config for on-device mode
    if config.is_ondevice():
        _generate_network_security_config(config, android_dir)

    # Generate build.gradle additions for Chaquopy (on-device)
    if config.is_ondevice():
        _generate_chaquopy_gradle(config, android_dir)


def _generate_ios_project(config: MobileConfig, out_dir: str) -> None:
    """Generate iOS native project files."""
    ios_dir = os.path.join(out_dir, "ios")
    os.makedirs(ios_dir, exist_ok=True)

    # Info.plist privacy keys
    privacy_keys = config.get_ios_privacy_keys()
    plist_entries = []
    for key, description in privacy_keys.items():
        plist_entries.append(f"    <key>{key}</key>")
        plist_entries.append(f"    <string>{description}</string>")

    # Add UIBackgroundModes for push if needed
    if "push" in config.capabilities:
        plist_entries.append("    <key>UIBackgroundModes</key>")
        plist_entries.append("    <array>")
        plist_entries.append("        <string>remote-notification</string>")
        plist_entries.append("    </array>")

    plist = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>CFBundleDevelopmentRegion</key>
            <string>en</string>
            <key>CFBundleDisplayName</key>
            <string>{config.app_name or "MikiUI App"}</string>
            <key>CFBundleIdentifier</key>
            <string>{config.app_id}</string>
            <key>CFBundleVersion</key>
            <string>1</string>
            <key>LSRequiresIPhoneOS</key>
            <true/>
            <key>UILaunchStoryboardName</key>
            <string>LaunchScreen</string>
            <key>UIRequiredDeviceCapabilities</key>
            <array>
                <string>armv7</string>
            </array>
            <key>UISupportedInterfaceOrientations</key>
            <array>
                <string>UIInterfaceOrientationPortrait</string>
                <string>UIInterfaceOrientationLandscapeLeft</string>
                <string>UIInterfaceOrientationLandscapeRight</string>
            </array>
            <key>NSAppTransportSecurity</key>
            <dict>
                <key>NSAllowsArbitraryLoads</key>
                <{str(config.allow_cleartext).lower()}/>
            </dict>
        {chr(10).join(plist_entries)}
        </dict>
        </plist>
    """)

    with open(os.path.join(ios_dir, "Info.plist"), "w", encoding="utf-8") as f:
        f.write(plist)

    # Generate PrivacyInfo.xcprivacy (Apple privacy manifest)
    _generate_ios_privacy_manifest(config, ios_dir)


def _generate_pwa_manifest(config: MobileConfig, out_dir: str) -> None:
    """Generate PWA manifest.webmanifest for installable web apps."""
    manifest = {
        "name": config.app_name or "MikiUI App",
        "short_name": (config.app_name or "MikiUI")[:12],
        "description": f"{config.app_name or 'MikiUI'} mobile app",
        "start_url": "/",
        "display": "standalone",
        "background_color": config.background_color,
        "theme_color": config.background_color,
        "orientation": config.orientation if config.orientation != "default" else "any",
        "icons": [
            {
                "src": "/_miki/runtime/icons/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": "/_miki/runtime/icons/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ],
        "categories": ["productivity"],
        "prefer_related_applications": False,
    }

    manifest_path = os.path.join(out_dir, "www", "manifest.webmanifest")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def _generate_mobile_html_template(config: MobileConfig, out_dir: str) -> None:
    """Generate mobile-optimized index.html template with PWA support."""
    # This is injected into the existing index.html by adding mobile-specific meta tags
    mobile_meta = [
        '<meta name="mobile-web-app-capable" content="yes">',
        '<meta name="apple-mobile-web-app-capable" content="yes">',
        '<meta name="apple-mobile-web-app-status-bar-style" content="default">',
        '<meta name="apple-mobile-web-app-title" content="{}">'.format(
            config.app_name or "MikiUI"
        ),
        f'<meta name="theme-color" content="{config.background_color}">',
        '<link rel="manifest" href="/manifest.webmanifest">',
        '<link rel="apple-touch-icon" href="/_miki/runtime/icons/icon-192.png">',
        '<meta name="format-detection" content="telephone=no">',
        '<meta name="msapplication-tap-highlight" content="no">',
    ]

    # Write the mobile meta tags to a file that can be included
    meta_path = os.path.join(out_dir, "www", "_mobile_meta.html")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write("\n".join(mobile_meta))


def _generate_app_icons(config: MobileConfig, out_dir: str) -> None:
    """Generate placeholder app icons for the mobile project.

    Creates simple placeholder icons. Users should replace these with
    their own branded icons before publishing.
    """
    import base64

    # Simple 1x1 pixel PNG as placeholder (transparent)
    # Users should replace with proper icons
    placeholder_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )

    icons_dir = os.path.join(out_dir, "www", "_miki", "runtime", "icons")
    os.makedirs(icons_dir, exist_ok=True)

    # Generate placeholder icons at required sizes
    icon_sizes = {
        "icon-192.png": 192,
        "icon-512.png": 512,
    }

    for filename, size in icon_sizes.items():
        icon_path = os.path.join(icons_dir, filename)
        if not os.path.exists(icon_path):
            # Write placeholder (user should replace)
            with open(icon_path, "wb") as f:
                f.write(placeholder_png)

    # Generate adaptive icon background for Android
    adaptive_icon_dir = os.path.join(out_dir, "android", "res", "mipmap-anydpi-v26")
    os.makedirs(adaptive_icon_dir, exist_ok=True)

    # Create a simple adaptive icon XML
    adaptive_icon_xml = textwrap.dedent("""\
        <?xml version="1.0" encoding="utf-8"?>
        <!-- Auto-generated by MikiUI — replace with your own icon -->
        <adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
            <background android:drawable="@color/ic_launcher_background"/>
            <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
        </adaptive-icon>
    """)

    with open(os.path.join(adaptive_icon_dir, "ic_launcher.xml"), "w", encoding="utf-8") as f:
        f.write(adaptive_icon_xml)

    # Create colors.xml for adaptive icon
    colors_dir = os.path.join(out_dir, "android", "res", "values")
    os.makedirs(colors_dir, exist_ok=True)

    colors_xml = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <!-- Auto-generated by MikiUI — customize for your brand -->
        <resources>
            <color name="ic_launcher_background">{config.background_color}</color>
            <color name="ic_launcher_foreground">#FFFFFF</color>
        </resources>
    """)

    with open(os.path.join(colors_dir, "colors.xml"), "w", encoding="utf-8") as f:
        f.write(colors_xml)


def _generate_mobile_error_pages(config: MobileConfig, out_dir: str) -> None:
    """Generate mobile-specific error pages for offline/network error states.

    These pages are shown when the app encounters network issues or
    when running in cloud mode without a connection.
    """
    www_dir = os.path.join(out_dir, "www")
    os.makedirs(www_dir, exist_ok=True)

    # Offline error page
    offline_html = textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
            <title>Offline - {config.app_name or 'App'}</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: {config.background_color};
                    color: #333;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    min-height: 100dvh;
                    padding: 2rem;
                    text-align: center;
                }}
                .icon {{ font-size: 4rem; margin-bottom: 1rem; }}
                h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
                p {{ color: #666; margin-bottom: 1.5rem; max-width: 300px; }}
                button {{
                    background: #2563eb;
                    color: white;
                    border: none;
                    padding: 0.75rem 2rem;
                    border-radius: 0.5rem;
                    font-size: 1rem;
                    cursor: pointer;
                    min-height: 44px;
                }}
                button:active {{ opacity: 0.8; }}
                .status {{ margin-top: 2rem; font-size: 0.875rem; color: #999; }}
            </style>
        </head>
        <body>
            <div class="icon">📡</div>
            <h1>You're Offline</h1>
            <p>Please check your internet connection and try again.</p>
            <button onclick="window.location.reload()">Try Again</button>
            <div class="status" id="status">Waiting for connection...</div>
            <script>
                // Auto-retry when online
                window.addEventListener('online', () => {{
                    document.getElementById('status').textContent = 'Connection restored!';
                    setTimeout(() => window.location.reload(), 1000);
                }});

                // Check connection status
                if (navigator.onLine) {{
                    document.getElementById('status').textContent = 'Connection available. Tap to retry.';
                }}
            </script>
        </body>
        </html>
    """)

    with open(os.path.join(www_dir, "_offline.html"), "w", encoding="utf-8") as f:
        f.write(offline_html)

    # Network error page (for HTMX failed requests)
    network_error_js = textwrap.dedent("""\
        // Mobile network error handler — auto-generated by MikiUI
        // Shows offline page when network requests fail
        (function() {
            'use strict';

            let offlinePageShown = false;

            // Intercept HTMX errors
            document.addEventListener('htmx:responseError', function(evt) {
                if (!navigator.onLine && !offlinePageShown) {
                    offlinePageShown = true;
                    window.location.href = '/_offline.html';
                }
            });

            // Intercept fetch errors
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                return originalFetch.apply(this, args).catch(function(err) {
                    if (!navigator.onLine && !offlinePageShown) {
                        offlinePageShown = true;
                        window.location.href = '/_offline.html';
                    }
                    throw err;
                });
            };

            // Check connection on page load
            if (!navigator.onLine) {
                console.warn('[MikiUI] App loaded offline');
            }

            // Expose connection status API
            window.MikiConnection = {
                isOnline: function() { return navigator.onLine; },
                onOnline: function(cb) { window.addEventListener('online', cb); },
                onOffline: function(cb) { window.addEventListener('offline', cb); },
            };
        })();
    """)

    with open(os.path.join(www_dir, "_miki", "runtime", "mobile_connection.js"), "w", encoding="utf-8") as f:
        f.write(network_error_js)


def _generate_permission_helper(config: MobileConfig, out_dir: str) -> None:
    """Generate a permission helper JavaScript file.

    This provides a unified API for requesting permissions at runtime,
    which is required for camera, location, notifications, etc.
    """
    www_dir = os.path.join(out_dir, "www")
    os.makedirs(www_dir, exist_ok=True)

    permission_js = textwrap.dedent("""\
        // Mobile permission helper - auto-generated by MikiUI
        // Provides unified permission request API for all platforms
        (function() {
            "use strict";

            var PermissionHelper = {
                // Permission status constants
                GRANTED: "granted",
                DENIED: "denied",
                PROMPT: "prompt",
                RESTRICTED: "restricted",

                // Map feature names to permission names
                permissionMap: {
                    camera: { android: "camera", ios: "camera", web: "camera" },
                    photos: { android: "photos", ios: "photos", web: null },
                    location: { android: "geolocation", ios: "geolocation", web: "geolocation" },
                    notifications: { android: "notifications", ios: "notifications", web: "notifications" },
                    microphone: { android: "microphone", ios: "microphone", web: "microphone" },
                    contacts: { android: "contacts", ios: "contacts", web: null },
                    calendar: { android: "calendar", ios: "calendar", web: null },
                    storage: { android: "storage", ios: null, web: null },
                    bluetooth: { android: "bluetooth", ios: "bluetooth", web: null },
                    sensors: { android: "sensors", ios: "motion", web: null },
                },

                // Request permission for a feature
                request: function(feature) {
                    var map = this.permissionMap[feature];
                    if (!map) return Promise.resolve(true);

                    var platform = this.getPlatform();
                    var permissionName = map[platform];
                    if (!permissionName) return Promise.resolve(true);

                    return this.requestNativePermission(permissionName);
                },

                // Check permission status for a feature
                check: function(feature) {
                    var map = this.permissionMap[feature];
                    if (!map) return Promise.resolve("granted");

                    var platform = this.getPlatform();
                    var permissionName = map[platform];
                    if (!permissionName) return Promise.resolve("granted");

                    return this.checkNativePermission(permissionName);
                },

                // Request native permission
                requestNativePermission: function(name) {
                    if (typeof window.Capacitor !== "undefined" && window.Capacitor.isNativePlatform()) {
                        var plugin = window.Capacitor.Plugins.Permissions;
                        if (plugin && plugin[name]) {
                            return plugin[name].request().then(function(result) {
                                return result.state === "granted";
                            });
                        }
                    }
                    // Web fallback for notifications
                    if (name === "notifications" && "Notification" in window) {
                        if (Notification.permission === "granted") return Promise.resolve(true);
                        if (Notification.permission === "denied") return Promise.resolve(false);
                        return Notification.requestPermission().then(function(p) { return p === "granted"; });
                    }
                    return Promise.resolve(true);
                },

                // Check native permission
                checkNativePermission: function(name) {
                    if (typeof window.Capacitor !== "undefined" && window.Capacitor.isNativePlatform()) {
                        var plugin = window.Capacitor.Plugins.Permissions;
                        if (plugin && plugin[name]) {
                            return plugin[name].check().then(function(result) {
                                return result.state;
                            });
                        }
                    }
                    if (name === "notifications" && "Notification" in window) {
                        return Promise.resolve(Notification.permission);
                    }
                    return Promise.resolve("granted");
                },

                // Get current platform
                getPlatform: function() {
                    if (typeof window.Capacitor !== "undefined") {
                        try {
                            return window.Capacitor.getPlatform();
                        } catch (e) {}
                    }
                    return "web";
                },

                // Request multiple permissions at once
                requestMultiple: function(features) {
                    var self = this;
                    return Promise.all(features.map(function(f) {
                        return self.request(f);
                    })).then(function(results) {
                        var granted = {};
                        features.forEach(function(f, i) { granted[f] = results[i]; });
                        return granted;
                    });
                },

                // Check multiple permissions at once
                checkMultiple: function(features) {
                    var self = this;
                    return Promise.all(features.map(function(f) {
                        return self.check(f);
                    })).then(function(results) {
                        var status = {};
                        features.forEach(function(f, i) { status[f] = results[i]; });
                        return status;
                    });
                },

                // Open app settings (for when permission is denied)
                openSettings: function() {
                    if (typeof window.Capacitor !== "undefined" && window.Capacitor.isNativePlatform()) {
                        var app = window.Capacitor.Plugins.App;
                        if (app && app.openSettings) {
                            return app.openSettings();
                        }
                    }
                    return Promise.resolve();
                }
            };

            window.MikiPermissions = PermissionHelper;
        })();
    """)

    with open(os.path.join(www_dir, "_miki", "runtime", "mobile_permissions.js"), "w", encoding="utf-8") as f:
        f.write(permission_js)


def _generate_data_layer(config: MobileConfig, out_dir: str) -> None:
    """Generate offline data persistence layer and app lifecycle management."""
    import shutil

    www_dir = os.path.join(out_dir, "www")
    os.makedirs(www_dir, exist_ok=True)

    # Copy the mobile runtime JS files
    dst_dir = os.path.join(www_dir, "_miki", "runtime")
    os.makedirs(dst_dir, exist_ok=True)

    for js_file in ["mobile_data.js", "mobile_app.js"]:
        src_path = os.path.join(os.path.dirname(__file__), "..", "runtime", "js", js_file)
        dst_path = os.path.join(dst_dir, js_file)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)


def _generate_push_endpoint(config: MobileConfig, out_dir: str) -> None:
    """Generate push notification server endpoint.

    Creates a ready-to-use FastAPI endpoint for sending push notifications.
    """
    if "push" not in config.capabilities:
        return

    deploy_dir = os.path.join(out_dir, "deploy")
    os.makedirs(deploy_dir, exist_ok=True)

    push_endpoint = textwrap.dedent('''\
        """
        Push notification endpoint - auto-generated by MikiUI.

        This module provides FastAPI endpoints for sending push notifications
        to Android (FCM) and iOS (APNs) devices.

        Setup:
        1. Install dependencies: pip install requests httpx pyjwt cryptography
        2. Set environment variables:
           - FCM_SERVER_KEY: Your Firebase server key
           - APNS_KEY_PATH: Path to your .p8 key file
           - APNS_KEY_ID: Your APNs key ID
           - APNS_TEAM_ID: Your Apple Developer Team ID
        3. Include this module in your FastAPI app:
           from api.push import router
           app.include_router(router, prefix="/api/push")
        """

        import os
        from typing import Optional
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel

        router = APIRouter(tags=["push"])


        class PushRequest(BaseModel):
            """Request model for sending push notifications."""
            token: str
            title: str
            body: str
            data: Optional[dict] = None


        class BulkPushRequest(BaseModel):
            """Request model for sending bulk push notifications."""
            tokens: list[str]
            title: str
            body: str
            data: Optional[dict] = None


        class DeviceRegistration(BaseModel):
            """Request model for registering device tokens."""
            token: str
            platform: str  # "android" or "ios"
            user_id: Optional[str] = None


        # In-memory token store (replace with database in production)
        _device_tokens: dict[str, dict] = {}


        @router.post("/send")
        async def send_push(request: PushRequest):
            """Send a push notification to a single device."""
            from mikiui.backend import send_push_notification

            fcm_key = os.environ.get("FCM_SERVER_KEY")
            apns_path = os.environ.get("APNS_KEY_PATH")
            apns_key_id = os.environ.get("APNS_KEY_ID")
            apns_team_id = os.environ.get("APNS_TEAM_ID")

            result = send_push_notification(
                token=request.token,
                title=request.title,
                body=request.body,
                data=request.data,
                fcm_server_key=fcm_key,
                apns_key_path=apns_path,
                apns_key_id=apns_key_id,
                apns_team_id=apns_team_id,
                bundle_id="{app_id}",
            )

            if result.get("status") != "ok":
                raise HTTPException(status_code=400, detail=result.get("message", "Failed"))

            return result


        @router.post("/send-bulk")
        async def send_bulk_push(request: BulkPushRequest):
            """Send push notifications to multiple devices."""
            from mikiui.backend import send_bulk_push_notifications

            fcm_key = os.environ.get("FCM_SERVER_KEY")
            apns_path = os.environ.get("APNS_KEY_PATH")
            apns_key_id = os.environ.get("APNS_KEY_ID")
            apns_team_id = os.environ.get("APNS_TEAM_ID")

            result = send_bulk_push_notifications(
                tokens=request.tokens,
                title=request.title,
                body=request.body,
                data=request.data,
                fcm_server_key=fcm_key,
                apns_key_path=apns_path,
                apns_key_id=apns_key_id,
                apns_team_id=apns_team_id,
                bundle_id="{app_id}",
            )

            return result


        @router.post("/register")
        async def register_device(request: DeviceRegistration):
            """Register a device token for push notifications."""
            _device_tokens[request.token] = {{
                "platform": request.platform,
                "user_id": request.user_id,
                "registered_at": __import__("datetime").datetime.now().isoformat(),
            }}
            return {{"status": "ok", "message": "Device registered"}}


        @router.delete("/unregister/{{token}}")
        async def unregister_device(token: str):
            """Unregister a device token."""
            if token in _device_tokens:
                del _device_tokens[token]
            return {{"status": "ok", "message": "Device unregistered"}}


        @router.get("/devices")
        async def list_devices():
            """List all registered device tokens."""
            return {{"devices": list(_device_tokens.values())}}


        @router.get("/health")
        async def push_health():
            """Check push notification configuration."""
            return {{
                "fcm_configured": bool(os.environ.get("FCM_SERVER_KEY")),
                "apns_configured": bool(os.environ.get("APNS_KEY_PATH")),
                "registered_devices": len(_device_tokens),
            }}
    ''').format(app_id=config.app_id)

    with open(os.path.join(deploy_dir, "push_endpoint.py"), "w", encoding="utf-8") as f:
        f.write(push_endpoint)


def _generate_deep_link_handler(config: MobileConfig, out_dir: str) -> None:
    """Generate deep link handler for the mobile app.

    Creates:
    1. Android App Links / iOS Universal Links configuration
    2. JavaScript deep link router
    3. Python deep link handler endpoint
    """
    if "deep-link" not in config.capabilities and "deep-link" not in config.plugins:
        return

    deploy_dir = os.path.join(out_dir, "deploy")
    os.makedirs(deploy_dir, exist_ok=True)
    www_dir = os.path.join(out_dir, "www")
    os.makedirs(www_dir, exist_ok=True)

    # JavaScript deep link router
    deeplink_js = textwrap.dedent("""\
        // Deep link handler - auto-generated by MikiUI
        // Handles incoming deep links and routes to the correct page
        (function() {
            "use strict";

            var DeepLink = {
                routes: {},

                // Register a route handler
                on: function(pattern, handler) {
                    this.routes[pattern] = handler;
                    return this;
                },

                // Parse a URL and extract path + params
                parseUrl: function(url) {
                    var a = document.createElement("a");
                    a.href = url;
                    return {
                        protocol: a.protocol,
                        host: a.host,
                        pathname: a.pathname,
                        search: a.search,
                        hash: a.hash,
                        params: this.parseParams(a.search),
                    };
                },

                // Parse query parameters
                parseParams: function(search) {
                    var params = {};
                    if (!search) return params;
                    search.replace(/^\?/, "").split("&").forEach(function(pair) {
                        var parts = pair.split("=");
                        if (parts[0]) {
                            params[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1] || "");
                        }
                    });
                    return params;
                },

                // Match a URL against registered routes
                match: function(url) {
                    var parsed = this.parseUrl(url);
                    var path = parsed.pathname;

                    for (var pattern in this.routes) {
                        var regex = new RegExp("^" + pattern.replace(/:\w+/g, "([^/]+)") + "$");
                        var match = path.match(regex);
                        if (match) {
                            var paramNames = [];
                            pattern.replace(/:(\w+)/g, function(_, name) { paramNames.push(name); });
                            var params = {};
                            paramNames.forEach(function(name, i) { params[name] = match[i + 1]; });
                            return this.routes[pattern](Object.assign({}, parsed.params, params));
                        }
                    }
                    return null;
                },

                // Handle incoming deep link
                handle: function(url) {
                    try {
                        return this.match(url);
                    } catch (e) {
                        console.error("[DeepLink] Error handling URL:", e);
                        return null;
                    }
                },

                // Initialize deep link handling
                init: function() {
                    var self = this;

                    // Handle deep links from Capacitor
                    if (typeof window.Capacitor !== "undefined" && window.Capacitor.Plugins.App) {
                        window.Capacitor.Plugins.App.addListener("appUrlOpen", function(data) {
                            self.handle(data.url);
                        });
                    }

                    // Handle initial URL (app opened via deep link)
                    if (typeof window.Capacitor !== "undefined" && window.Capacitor.Plugins.App) {
                        window.Capacitor.Plugins.App.getLaunchUrl().then(function(result) {
                            if (result && result.url) self.handle(result.url);
                        });
                    }

                    // Handle hash-based deep links (web)
                    window.addEventListener("hashchange", function() {
                        var hash = window.location.hash;
                        if (hash.indexOf("#/") === 0) {
                            self.handle("myapp://" + hash.substring(1));
                        }
                    });
                },
            };

            // Initialize on load
            if (document.readyState === "complete") {
                DeepLink.init();
            } else {
                document.addEventListener("DOMContentLoaded", function() { DeepLink.init(); });
            }

            window.MikiDeepLink = DeepLink;
        })();
    """)

    with open(os.path.join(www_dir, "_miki", "runtime", "mobile_deeplink.js"), "w", encoding="utf-8") as f:
        f.write(deeplink_js)

    # Python deep link handler
    deeplink_py = textwrap.dedent('''\
        """
        Deep link handler - auto-generated by MikiUI.

        This module provides FastAPI endpoints for handling deep links
        and generating shareable URLs.

        Setup:
        1. Include this module in your FastAPI app:
           from api.deeplink import router, DeepLinkConfig
        2. Register your deep link routes:
           DeepLinkConfig.add_route("/products/{{id}}", "product_detail")
        3. Add to your capacitor.config.json:
           "server": {{ "allowNavigation": ["*"] }}
        """

        import re
        from typing import Optional, Callable
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel

        router = APIRouter(tags=["deeplink"])


        class DeepLinkRoute(BaseModel):
            """A registered deep link route."""
            pattern: str
            name: str
            handler: Optional[str] = None


        class DeepLinkConfig:
            """Configuration for deep link handling."""

            _routes: list[DeepLinkRoute] = []
            _app_scheme = "{app_scheme}"

            @classmethod
            def add_route(cls, pattern: str, name: str, handler: str = None):
                """Register a deep link route.

                Args:
                    pattern: URL pattern like "/products/:id"
                    name: Route name for reference
                    handler: Optional handler function name
                """
                cls._routes.append(DeepLinkRoute(pattern=pattern, name=name, handler=handler))

            @classmethod
            def set_scheme(cls, scheme: str):
                """Set the app URL scheme (e.g., "myapp")."""
                cls._app_scheme = scheme

            @classmethod
            def resolve(cls, url: str) -> Optional[dict]:
                """Resolve a URL to a registered route.

                Returns:
                    Dict with route info or None if no match
                """
                # Parse URL
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(url)
                path = parsed.path
                params = parse_qs(parsed.query)

                # Flatten single-value params
                flat_params = {{}}
                for k, v in params.items():
                    flat_params[k] = v[0] if len(v) == 1 else v

                # Match against routes
                for route in cls._routes:
                    # Convert pattern to regex
                    regex_pattern = re.sub(r'{{{{\\w+}}}}', r'([^/]+)', route.pattern)
                    regex_pattern = "^" + regex_pattern + "$"
                    match = re.match(regex_pattern, path)
                    if match:
                        # Extract named params
                        param_names = re.findall(r'{{(\\w+)}}', route.pattern)
                        named_params = {{}}
                        for i, name in enumerate(param_names):
                            named_params[name] = match.group(i + 1)
                        return {{
                            "route": route.name,
                            "params": {{**flat_params, **named_params}},
                        }}
                return None

            @classmethod
            def generate_url(cls, route_name: str, **kwargs) -> Optional[str]:
                """Generate a deep link URL for a route.

                Args:
                    route_name: Name of the registered route
                    **kwargs: URL parameters

                Returns:
                    Deep link URL or None if route not found
                """
                for route in cls._routes:
                    if route.name == route_name:
                        url = route.pattern
                        for key, value in kwargs.items():
                            url = url.replace("{{" + key + "}}", str(value))
                        return cls._app_scheme + "://" + url
                return None


        @router.get("/resolve")
        async def resolve_deeplink(url: str):
            """Resolve a deep link URL to route info."""
            result = DeepLinkConfig.resolve(url)
            if not result:
                raise HTTPException(status_code=404, detail="No matching route")
            return result


        @router.post("/generate")
        async def generate_deeplink(route: str, params: dict = None):
            """Generate a deep link URL for a route."""
            url = DeepLinkConfig.generate_url(route, **(params or {{}}))
            if not url:
                raise HTTPException(status_code=404, detail="Route not found")
            return {{"url": url}}


        @router.get("/routes")
        async def list_routes():
            """List all registered deep link routes."""
            return {{
                "routes": [
                    {{"pattern": r.pattern, "name": r.name}}
                    for r in DeepLinkConfig._routes
                ]
            }}
    ''').format(app_scheme=config.app_id.split(".")[-1])

    with open(os.path.join(deploy_dir, "deeplink_handler.py"), "w", encoding="utf-8") as f:
        f.write(deeplink_py)

    # Android App Links / iOS Universal Links config
    assetlinks = textwrap.dedent("""\
        [
          {{
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {{
              "namespace": "android_app",
              "package_name": "{app_id}",
              "sha256_cert_fingerprints": [
                "YOUR_SHA256_FINGERPRINT"
              ]
            }}
          }}
        ]
    """).format(app_id=config.app_id)

    with open(os.path.join(deploy_dir, "assetlinks.json"), "w", encoding="utf-8") as f:
        f.write(assetlinks)

    # iOS Apple App Site Association
    aasa = textwrap.dedent("""\
        {{
          "applinks": {{
            "apps": [],
            "details": [
              {{
                "appID": "{team_id}.{app_id}",
                "paths": ["*"]
              }}
            ]
          }}
        }}
    """).format(
        team_id="YOUR_TEAM_ID",
        app_id=config.app_id,
    )

    with open(os.path.join(deploy_dir, "apple-app-site-association"), "w", encoding="utf-8") as f:
        f.write(aasa)


def _generate_deployment_configs(config: MobileConfig, out_dir: str) -> None:
    """Generate deployment configuration files for various platforms.

    These files help beginners deploy their cloud-mode backend easily.
    """
    deploy_dir = os.path.join(out_dir, "deploy")
    os.makedirs(deploy_dir, exist_ok=True)

    # Vercel config (for single-origin deployment)
    vercel_config = {
        "version": 2,
        "builds": [
            {
                "src": "api/index.py",
                "use": "@vercel/python"
            }
        ],
        "routes": [
            {
                "src": "/api/(.*)",
                "dest": "api/index.py"
            },
            {
                "src": "/(.*)",
                "dest": "www/$1"
            }
        ]
    }
    with open(os.path.join(deploy_dir, "vercel.json"), "w", encoding="utf-8") as f:
        json.dump(vercel_config, f, indent=2)

    # Railway config
    railway_config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "uvicorn api.index:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health",
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    with open(os.path.join(deploy_dir, "railway.json"), "w", encoding="utf-8") as f:
        json.dump(railway_config, f, indent=2)

    # Netlify config
    netlify_config = textwrap.dedent("""\
        [build]
          command = "echo 'No build needed for static site'"
          publish = "www"

        [[redirects]]
          from = "/api/*"
          to = "https://your-backend.railway.app/api/:splat"
          status = 200
          force = true

        [[redirects]]
          from = "/*"
          to = "/index.html"
          status = 200

        [[headers]]
          for = "/*"
          [headers.values]
            Cache-Control = "public, max-age=3600"
    """)
    with open(os.path.join(deploy_dir, "netlify.toml"), "w", encoding="utf-8") as f:
        f.write(netlify_config)

    # Docker config for self-hosting
    dockerfile = textwrap.dedent("""\
        # MikiUI Cloud Backend — auto-generated
        # Build: docker build -t myapp-backend .
        # Run: docker run -p 8000:8000 myapp-backend
        FROM python:3.11-slim

        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        COPY . .

        EXPOSE 8000

        CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
    """)
    with open(os.path.join(deploy_dir, "Dockerfile"), "w", encoding="utf-8") as f:
        f.write(dockerfile)

    # Docker Compose for full stack
    docker_compose = textwrap.dedent("""\
        # MikiUI Full Stack — auto-generated
        # Run: docker compose up
        version: "3.8"

        services:
          backend:
            build:
              context: .
              dockerfile: deploy/Dockerfile
            ports:
              - "8000:8000"
            environment:
              - ENV=production
            restart: unless-stopped

          # Optional: Add nginx for serving static frontend
          frontend:
            image: nginx:alpine
            ports:
              - "80:80"
              - "443:443"
            volumes:
              - ./www:/usr/share/nginx/html:ro
            depends_on:
              - backend
            restart: unless-stopped
    """)
    with open(os.path.join(deploy_dir, "docker-compose.yml"), "w", encoding="utf-8") as f:
        f.write(docker_compose)

    # Push notification setup guide
    _generate_push_setup_guide(config, deploy_dir)

    # README for deployment
    deploy_readme = textwrap.dedent("""\
        # Deployment Guide

        Your MikiUI mobile app backend can be deployed to any of these platforms:

        ## Quick Start (Vercel — Easiest)

        1. Install Vercel CLI: `npm i -g vercel`
        2. Run: `vercel --prod`
        3. Your app is live!

        ## Railway

        1. Install Railway CLI: `npm i -g @railway/cli`
        2. Run: `railway up`
        3. Your backend is live!

        ## Netlify (Static Frontend Only)

        1. Install Netlify CLI: `npm i -g netlify-cli`
        2. Run: `netlify deploy --prod --dir=www`

        ## Docker (Self-Hosted)

        1. Build: `docker build -t myapp -f deploy/Dockerfile .`
        2. Run: `docker run -p 8000:8000 myapp`

        ## Full Stack with Docker Compose

        1. Run: `docker compose -f deploy/docker-compose.yml up -d`
        2. Your app is available at http://localhost

        ---

        Remember to update `capacitor.config.json` with your backend URL!

        See push-setup.md for push notification configuration.
    """)
    with open(os.path.join(deploy_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(deploy_readme)


def _generate_push_setup_guide(config: MobileConfig, deploy_dir: str) -> None:
    """Generate push notification setup guide.

    This guide helps beginners configure FCM (Android) and APNs (iOS)
    push notifications for their mobile app.
    """
    if "push" not in config.capabilities:
        return

    push_guide = textwrap.dedent(f"""\
        # Push Notification Setup Guide

        This guide walks you through setting up push notifications for your
        MikiUI mobile app.

        ## Overview

        Push notifications require:
        1. **FCM** (Firebase Cloud Messaging) for Android
        2. **APNs** (Apple Push Notification service) for iOS
        3. A server endpoint to send notifications

        ---

        ## Android Setup (FCM)

        ### Step 1: Create Firebase Project

        1. Go to https://console.firebase.google.com/
        2. Click "Add project"
        3. Enter your project name
        4. Follow the setup wizard

        ### Step 2: Register Android App

        1. In Firebase Console, click the Android icon to add an app
        2. Enter your package name: `{config.app_id}`
        3. Download `google-services.json`
        4. Place it in `android/app/google-services.json`

        ### Step 3: Get Server Key

        1. Go to Project Settings → Cloud Messaging
        2. Copy the "Server key" (legacy token)
        3. Save this for your backend

        ### Step 4: Configure Backend

        Add this to your FastAPI backend:

        ```python
        from mikiui.backend import send_push_notification

        @app.post("/api/push/send")
        def send_push(token: str, title: str, body: str):
            return send_push_notification(
                token=token,
                title=title,
                body=body,
                fcm_server_key="YOUR_FCM_SERVER_KEY",
            )
        ```

        ---

        ## iOS Setup (APNs)

        ### Step 1: Create Apple Developer Account

        1. Go to https://developer.apple.com/
        2. Enroll in the Apple Developer Program ($99/year)

        ### Step 2: Create APNs Key

        1. Go to Certificates, Identifiers & Profiles
        2. Keys → Create New Key
        3. Enable "Apple Push Notifications service (APNs)"
        4. Download the .p8 file
        5. Note the Key ID and Team ID

        ### Step 3: Configure Backend

        ```python
        from mikiui.backend import send_push_notification

        @app.post("/api/push/send")
        def send_push(token: str, title: str, body: str):
            return send_push_notification(
                token=token,
                title=title,
                body=body,
                apns_key_path="/path/to/AuthKey_XXXXX.p8",
                apns_key_id="YOUR_KEY_ID",
                apns_team_id="YOUR_TEAM_ID",
                bundle_id="{config.app_id}",
            )
        ```

        ---

        ## Testing Push Notifications

        ### Android (using Firebase Console)

        1. Go to Firebase Console → Cloud Messaging
        2. Click "Send your first message"
        3. Enter the device token from your app
        4. Send the message

        ### iOS (using simulator or device)

        iOS Simulator does not support push notifications. You need a real device.

        ---

        ## Troubleshooting

        ### "Registration token not received"

        - Check internet connection
        - Verify FCM/APNs configuration
        - Check app permissions

        ### "Notification received but not displayed"

        - Check notification channel (Android)
        - Verify app is in foreground or background
        - Check notification permissions

        ### "Server key invalid"

        - Regenerate the FCM server key
        - Ensure you're using the legacy server key
    """)

    with open(os.path.join(deploy_dir, "push-setup.md"), "w", encoding="utf-8") as f:
        f.write(push_guide)


def _generate_ios_privacy_manifest(config: MobileConfig, ios_dir: str) -> None:
    """Generate PrivacyInfo.xcprivacy for Apple App Store privacy requirements.

    Apple requires a privacy manifest file declaring what data types and
    APIs the app uses. This is auto-generated from the plugin capabilities.
    """
    # Map capabilities to Apple privacy API types
    privacy_apis: list[dict[str, str]] = []
    data_types: list[dict[str, str]] = []

    for cap in config.capabilities:
        if cap == "camera":
            privacy_apis.append({
                "api": "NSPrivacyAccessedAPICamera",
                "reason": "To capture photos for the app.",
            })
        elif cap == "geolocation":
            privacy_apis.append({
                "api": "NSPrivacyAccessedAPILocation",
                "reason": "To provide location-based features.",
            })
            data_types.append({
                "type": "NSPrivacyDataTypeLocation",
                "reason": "To determine user location.",
            })
        elif cap == "push":
            privacy_apis.append({
                "api": "NSPrivacyAccessedAPINotifications",
                "reason": "To deliver push notifications.",
            })
        elif cap == "clipboard":
            data_types.append({
                "type": "NSPrivacyDataTypeClipboard",
                "reason": "To copy and paste content.",
            })
        elif cap == "filesystem":
            privacy_apis.append({
                "api": "NSPrivacyAccessedAPIFileTimestamp",
                "reason": "To read and write files.",
            })

    # Build the XML
    api_entries = []
    for api in privacy_apis:
        api_entries.append(
            f"        <dict>\n"
            f"            <key>NSPrivacyAccessedAPIType</key>\n"
            f"            <string>{api['api']}</string>\n"
            f"            <key>NSPrivacyAccessedAPITypeReasons</key>\n"
            f"            <array>\n"
            f"                <string>{api['reason']}</string>\n"
            f"            </array>\n"
            f"        </dict>"
        )

    data_entries = []
    for dt in data_types:
        data_entries.append(
            f"        <dict>\n"
            f"            <key>NSPrivacyDataType</key>\n"
            f"            <string>{dt['type']}</string>\n"
            f"            <key>NSPrivacyDataTypesReasons</key>\n"
            f"            <array>\n"
            f"                <string>{dt['reason']}</string>\n"
            f"            </array>\n"
            f"        </dict>"
        )

    privacy_manifest = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>NSPrivacyAccessedAPITypes</key>
            <array>
        {chr(10).join(api_entries) if api_entries else "        <!-- No privacy APIs used -->"}
            </array>
            <key>NSPrivacyCollectedDataTypes</key>
            <array>
        {chr(10).join(data_entries) if data_entries else "        <!-- No data collected -->"}
            </array>
        </dict>
        </plist>
    """)

    with open(os.path.join(ios_dir, "PrivacyInfo.xcprivacy"), "w", encoding="utf-8") as f:
        f.write(privacy_manifest)


def _check_size_budget(config: MobileConfig, out_dir: str) -> list[str]:
    """Check if the build meets size budget requirements.

    Returns a list of warnings if budgets are exceeded.
    """
    warnings: list[str] = []

    # Calculate total size of www directory
    www_dir = os.path.join(out_dir, "www")
    total_size = 0
    if os.path.isdir(www_dir):
        for root, _dirs, files in os.walk(www_dir):
            for f in files:
                fp = os.path.join(root, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)

    # Size budgets (in bytes)
    if config.is_cloud():
        # Cloud mode: ~8-20MB target
        max_size = 25 * 1024 * 1024  # 25MB warning threshold
        if total_size > max_size:
            warnings.append(
                f"Cloud mode build size ({total_size / 1024 / 1024:.1f}MB) exceeds "
                f"recommended budget (25MB). Consider reducing static assets."
            )
    else:
        # On-device mode: ~33-40MB target
        max_size = 50 * 1024 * 1024  # 50MB warning threshold
        if total_size > max_size:
            warnings.append(
                f"On-device mode build size ({total_size / 1024 / 1024:.1f}MB) exceeds "
                f"recommended budget (50MB). Consider reducing chaquopy_deps or static assets."
            )

    # Check Chaquopy deps count
    if config.is_ondevice() and len(config.chaquopy_deps) > 10:
        warnings.append(
            f"Large number of Chaquopy dependencies ({len(config.chaquopy_deps)}). "
            "Each Python package adds to APK size. Consider minimizing deps."
        )

    return warnings


def _generate_network_security_config(config: MobileConfig, android_dir: str) -> None:
    """Generate network security config for on-device mode.

    This allows the app to communicate with the local Chaquopy backend
    without violating Android's network security policies.
    """
    # Create the XML directory
    xml_dir = os.path.join(android_dir, "res", "xml")
    os.makedirs(xml_dir, exist_ok=True)

    # Network security config — allow cleartext to localhost only
    network_security_config = textwrap.dedent("""\
        <?xml version="1.0" encoding="utf-8"?>
        <!-- Auto-generated by MikiUI — do not edit manually -->
        <network-security-config>
            <!-- Allow cleartext traffic to localhost for Chaquopy bridge -->
            <domain-config cleartextTrafficPermitted="true">
                <domain includeSubdomains="true">localhost</domain>
                <domain includeSubdomains="true">127.0.0.1</domain>
                <domain includeSubdomains="true">10.0.2.2</domain>
            </domain-config>

            <!-- Pin certificates for production (optional) -->
            <base-config cleartextTrafficPermitted="false">
                <trust-anchors>
                    <certificates src="system" />
                </trust-anchors>
            </base-config>
        </network-security-config>
    """)

    with open(os.path.join(xml_dir, "network_security_config.xml"), "w", encoding="utf-8") as f:
        f.write(network_security_config)


def _generate_chaquopy_gradle(config: MobileConfig, android_dir: str) -> None:
    """Generate Chaquopy Gradle configuration for on-device mode."""
    deps = config.chaquopy_deps or ["fastapi", "uvicorn", "pydantic"]
    dep_lines = []
    for dep in deps:
        dep_lines.append(f'            pip.install("{dep}")')

    gradle_config = textwrap.dedent(f"""\
        // Chaquopy configuration — auto-generated by MikiUI
        // This enables embedded Python in the Android APK.
        plugins {{
            id 'com.chaquo.python' version '15.0.1'
        }}

        python {{
            version "3.11"
            pip {{
{chr(10).join(dep_lines)}
            }}
        }}

        android {{
            defaultConfig {{
                python {{
                    buildPython "/usr/bin/python3"
                }}
            }}
        }}
    """)

    with open(os.path.join(android_dir, "chaquopy.gradle"), "w", encoding="utf-8") as f:
        f.write(gradle_config)


def _generate_ondevice_bridge(config: MobileConfig, out_dir: str) -> None:
    """Generate on-device bridge files (Chaquopy Python + Kotlin).

    Uses the production ChaquopyBridge from mikiui.app.mobile.chaquopy_bridge.
    """
    bridge_dir = os.path.join(out_dir, "bridge")
    os.makedirs(bridge_dir, exist_ok=True)

    # Copy the ChaquopyBridge from the framework
    import shutil

    import mikiui.app.mobile.chaquopy_bridge as bridge_module
    src_path = os.path.abspath(bridge_module.__file__)
    dst_path = os.path.join(bridge_dir, "chaquopy_bridge.py")
    shutil.copy2(src_path, dst_path)

    # Generate Kotlin bridge stub that uses the Python bridge
    kotlin_bridge = textwrap.dedent("""\
        package com.mikiui.app

        import android.webkit.JavascriptInterface
        import android.webkit.WebView

        /**
         * On-device bridge — auto-generated by MikiUI.
         * Connects JavaScript calls to embedded Python via Chaquopy.
         *
         * This file is auto-generated. Do not edit manually.
         */
        class OnDeviceBridge(private val webView: WebView) {

            private var bridgeInstance: Any? = null

            init {
                // Initialize Chaquopy
                if (!com.chaquo.python.Python.isStarted()) {
                    com.chaquo.python.Python.start(
                        com.chaquo.python.AndroidPlatform(webView.context)
                    )
                }
            }

            @JavascriptInterface
            fun backendCall(payloadJson: String): String {
                return try {
                    val python = com.chaquo.python.Python.getInstance()
                    val bridgeModule = python.getModule("bridge.chaquopy_bridge")
                    val getBridge = bridgeModule["get_bridge"]

                    // Get the app instance (user must define get_app() in their app module)
                    val appModule = python.getModule("app")
                    val getApp = appModule["get_app"]
                    val app = getApp()

                    val bridge = getBridge(app)
                    bridge.call(payloadJson) as String
                } catch (e: Exception) {
                    "{\\"error\\": \\"" + (e.message ?: "Unknown error") + "\\", \\"status\\": 500}"
                }
            }
        }
    """)

    kotlin_dir = os.path.join(bridge_dir, "kotlin", "com", "mikiui", "app")
    os.makedirs(kotlin_dir, exist_ok=True)
    with open(os.path.join(kotlin_dir, "OnDeviceBridge.kt"), "w", encoding="utf-8") as f:
        f.write(kotlin_bridge)

    # Generate the app.py template for on-device mode
    app_template = textwrap.dedent('''\
        """On-device app entry point for MikiUI.

        This file is auto-generated. Your routes are imported from the main app.
        The get_app() function returns the MikiApp instance for the bridge.
        """
        from {app_module} import app

        def get_app():
            """Return the MikiApp instance for the Chaquopy bridge."""
            return app
    ''')

    with open(os.path.join(bridge_dir, "_app_template.py"), "w", encoding="utf-8") as f:
        f.write(app_template)


__all__ = ["build_mobile"]
