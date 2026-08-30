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

from ..app.mobile import MobileConfig


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

    # Step 6: Generate PWA manifest and mobile HTML template
    _generate_pwa_manifest(config, out_dir)
    _generate_mobile_html_template(config, out_dir)

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

    capacitor_config: dict[str, Any] = {
        "appId": app_id,
        "appName": app_name,
        "webDir": "www",
        "server": {},
        "plugins": {},
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

    # Splash screen
    capacitor_config["plugins"]["SplashScreen"] = {
        "launchShowDuration": config.splash_duration,
        "backgroundColor": config.background_color,
        "showSpinner": True,
    }

    # Status bar
    capacitor_config["plugins"]["StatusBar"] = {
        "style": "DEFAULT",
        "backgroundColor": config.background_color,
    }

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

    # On-device: add INTERNET and network permissions
    if config.is_ondevice():
        extra_perms = [
            "android.permission.INTERNET",
            "android.permission.ACCESS_NETWORK_STATE",
        ]
        for p in extra_perms:
            if p not in permissions:
                permission_lines.append(f'    <uses-permission android:name="{p}" />')

    manifest = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="utf-8"?>
        <manifest xmlns:android="http://schemas.android.com/apk/res/android">
        {chr(10).join(permission_lines)}

            <application
                android:allowBackup="true"
                android:icon="@mipmap/ic_launcher"
                android:label="@string/app_name"
                android:roundIcon="@mipmap/ic_launcher_round"
                android:supportsRtl="true"
                android:theme="@style/AppTheme"
                android:usesCleartextTraffic="{'true' if config.allow_cleartext else 'false'}">

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


def _generate_chaquopy_gradle(config: MobileConfig, android_dir: str) -> None:
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
    """Generate on-device bridge files (Chaquopy Python + Kotlin)."""
    bridge_dir = os.path.join(out_dir, "bridge")
    os.makedirs(bridge_dir, exist_ok=True)

    # Python bridge module
    python_bridge = textwrap.dedent("""\
        \"\"\"On-device Python bridge for MikiUI.

        This module is loaded by Chaquopy inside the Android WebView.
        It exposes a backendCall() method via @JavascriptInterface.
        \"\"\"

        import json
        import asyncio
        from typing import Any


        class OnDeviceBridge:
            \"\"\"Direct route invocation without HTTP.\"\"\"

            def __init__(self, app: Any) -> None:
                self._app = app

            def backendCall(self, payload_json: str) -> str:
                \"\"\"Handle a backend call from JavaScript.

                payload_json: JSON string with 'method', 'path', 'data'
                Returns: JSON string response
                \"\"\"
                try:
                    payload = json.loads(payload_json)
                    method = payload.get("method", "GET")
                    path = payload.get("path", "/")
                    data = payload.get("data")

                    route = self._app.get_route(path)
                    if route is None:
                        return json.dumps({"error": f"No route: {path}", "status": 404})

                    # Build kwargs
                    kwargs = {}
                    if route.accepts_ctx:
                        from mikiui.app.routes import Ctx
                        ctx = Ctx(None, self._app, dict(route.path_params))
                        params = list(route.handler.__code__.co_varnames)
                        if params:
                            kwargs[params[0]] = ctx

                    # Invoke handler
                    if asyncio.iscoroutinefunction(route.handler):
                        loop = asyncio.new_event_loop()
                        result = loop.run_until_complete(route.handler(**kwargs))
                        loop.close()
                    else:
                        result = route.handler(**kwargs)

                    if isinstance(result, tuple):
                        body, status_code = result if len(result) == 2 else (result[0], 200)
                    else:
                        body = result
                        status_code = 200

                    return json.dumps({"data": body, "status": status_code})

                except Exception as exc:
                    return json.dumps({"error": str(exc), "status": 500})


        _bridge_instance: OnDeviceBridge | None = None


        def get_bridge(app: Any) -> OnDeviceBridge:
            \"\"\"Get or create the singleton bridge instance.\"\"\"
            global _bridge_instance
            if _bridge_instance is None:
                _bridge_instance = OnDeviceBridge(app)
            return _bridge_instance
    """)

    with open(os.path.join(bridge_dir, "ondevice_bridge.py"), "w", encoding="utf-8") as f:
        f.write(python_bridge)

    # Kotlin bridge stub
    kotlin_bridge = textwrap.dedent("""\
        package com.mikiui.app

        import android.webkit.JavascriptInterface
        import android.webkit.WebView

        /**
         * On-device bridge — auto-generated by MikiUI.
         * Connects JavaScript calls to embedded Python via Chaquopy.
         */
        class OnDeviceBridge(private val webView: WebView) {

            private var pythonModule: Any? = null

            init {
                // Initialize Chaquopy
                if (!com.chaquo.python.Python.isStarted()) {
                    com.chaquo.python.Python.start(com.chaquo.python.AndroidPlatform(webView.context))
                }
            }

            @JavascriptInterface
            fun backendCall(payloadJson: String): String {
                return try {
                    val python = com.chaquo.python.Python.getInstance()
                    val module = python.getModule("bridge.ondevice_bridge")
                    val getBridge = module["get_bridge"]
                    // Get the app instance from the module
                    val appModule = python.getModule("app")
                    val app = appModule["app"]
                    val bridge = getBridge(app)
                    bridge.backendCall(payloadJson)
                } catch (e: Exception) {
                    "{\\"error\\": \\"" + e.message + "\\", \\"status\\": 500}"
                }
            }
        }
    """)

    kotlin_dir = os.path.join(bridge_dir, "kotlin", "com", "mikiui", "app")
    os.makedirs(kotlin_dir, exist_ok=True)
    with open(os.path.join(kotlin_dir, "OnDeviceBridge.kt"), "w", encoding="utf-8") as f:
        f.write(kotlin_bridge)


__all__ = ["build_mobile"]
