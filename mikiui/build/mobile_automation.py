"""Mobile automation for MikiUI — one-click build, test, sign, and publish.

This module provides:
1. Automated native project file generation (MainActivity.kt, AppDelegate.swift, etc.)
2. Automated plugin installation and sync
3. One-click device testing (simulator + real device)
4. Code signing automation
5. Store submission automation
"""

from __future__ import annotations

import os
import subprocess
import textwrap
from typing import Any

from ..app.mobile import MobileConfig


class MobileAutomation:
    """Automates mobile app build, test, sign, and publish workflows."""

    def __init__(self, app: Any, out_dir: str = "dist_mobile") -> None:
        self._app = app
        self._out_dir = out_dir
        _config = getattr(app, "mobile", None)
        if _config is None:
            self._config = MobileConfig()
        else:
            self._config = _config

    @property
    def config(self) -> MobileConfig:
        return self._config

    @property
    def out_dir(self) -> str:
        return self._out_dir

    @property
    def android_dir(self) -> str:
        return os.path.join(self._out_dir, "android")

    @property
    def ios_dir(self) -> str:
        return os.path.join(self._out_dir, "ios")

    @property
    def www_dir(self) -> str:
        return os.path.join(self._out_dir, "www")

    # ====================================================================
    # 1. NATIVE PROJECT FILE GENERATION
    # ====================================================================

    def generate_native_projects(self) -> dict[str, Any]:
        """Generate complete native project files for Android and iOS.

        This creates all necessary files that Capacitor needs but doesn't
        generate by default:
        - Android: MainActivity.kt, build.gradle, strings.xml, etc.
        - iOS: AppDelegate.swift, Podfile, etc.
        """
        results: dict[str, Any] = {"android": None, "ios": None}

        if self._config.targets_android():
            results["android"] = self._generate_android_native()

        if self._config.targets_ios():
            results["ios"] = self._generate_ios_native()

        return results

    def _generate_android_native(self) -> dict[str, Any]:
        """Generate Android native project files."""
        android_dir = self.android_dir
        app_dir = os.path.join(android_dir, "app")
        src_dir = os.path.join(app_dir, "src", "main")
        java_dir = os.path.join(src_dir, "java", *self._config.app_id.split("."))
        res_dir = os.path.join(src_dir, "res")
        values_dir = os.path.join(res_dir, "values")
        xml_dir = os.path.join(res_dir, "xml")
        mipmap_dir = os.path.join(res_dir, "mipmap-anydpi-v26")

        # Create directories
        for d in [java_dir, values_dir, xml_dir, mipmap_dir]:
            os.makedirs(d, exist_ok=True)

        generated_files = []

        # MainActivity.kt
        main_activity = self._generate_main_activity_kt()
        main_activity_path = os.path.join(java_dir, "MainActivity.kt")
        with open(main_activity_path, "w", encoding="utf-8") as f:
            f.write(main_activity)
        generated_files.append(main_activity_path)

        # build.gradle (app-level)
        build_gradle = self._generate_android_build_gradle()
        build_gradle_path = os.path.join(app_dir, "build.gradle")
        with open(build_gradle_path, "w", encoding="utf-8") as f:
            f.write(build_gradle)
        generated_files.append(build_gradle_path)

        # strings.xml
        strings_xml = self._generate_android_strings()
        strings_path = os.path.join(values_dir, "strings.xml")
        with open(strings_path, "w", encoding="utf-8") as f:
            f.write(strings_xml)
        generated_files.append(strings_path)

        # colors.xml (if not exists)
        colors_path = os.path.join(values_dir, "colors.xml")
        if not os.path.exists(colors_path):
            colors_xml = self._generate_android_colors()
            with open(colors_path, "w", encoding="utf-8") as f:
                f.write(colors_xml)
            generated_files.append(colors_path)

        # network_security_config.xml
        network_config_path = os.path.join(xml_dir, "network_security_config.xml")
        if not os.path.exists(network_config_path):
            network_config = self._generate_network_security_config()
            with open(network_config_path, "w", encoding="utf-8") as f:
                f.write(network_config)
            generated_files.append(network_config_path)

        # Adaptive icon
        ic_launcher_path = os.path.join(mipmap_dir, "ic_launcher.xml")
        if not os.path.exists(ic_launcher_path):
            ic_launcher = self._generate_adaptive_icon()
            with open(ic_launcher_path, "w", encoding="utf-8") as f:
                f.write(ic_launcher)
            generated_files.append(ic_launcher_path)

        # On-device: Chaquopy bridge
        if self._config.is_ondevice():
            bridge_files = self._generate_chaquopy_bridge(android_dir, java_dir)
            generated_files.extend(bridge_files)

        return {
            "status": "ok",
            "platform": "android",
            "files": generated_files,
            "main_activity": main_activity_path,
        }

    def _generate_main_activity_kt(self) -> str:
        """Generate MainActivity.kt for Android."""
        imports = [
            "package " + self._config.app_id,
            "",
            "import android.os.Bundle",
            "import com.getcapacitor.BridgeActivity",
            "import com.getcapacitor.Plugin",
        ]

        # Add on-device imports
        if self._config.is_ondevice():
            imports.extend([
                "import com.chaquo.python.Python",
                "import com.chaquo.python.AndroidPlatform",
            ])

        # Add plugin imports based on capabilities
        plugin_imports = self._get_android_plugin_imports()
        imports.extend(plugin_imports)

        class_body = [
            "",
            "class MainActivity : BridgeActivity() {",
            "    override fun onCreate(savedInstanceState: Bundle?) {",
            "        super.onCreate(savedInstanceState)",
            "",
            "        // Initialize on-device Python if needed",
        ]

        if self._config.is_ondevice():
            class_body.extend([
                "        if (!Python.isStarted()) {",
                "            Python.start(AndroidPlatform(this))",
                "        }",
                "",
            ])

        class_body.extend([
            "        // Register plugins",
            "        registerPlugins(arrayOf<Class<out Plugin>>(",
        ])

        # Add plugin registrations
        plugin_classes = self._get_android_plugin_classes()
        if plugin_classes:
            for plugin_class in plugin_classes:
                class_body.append(f"            {plugin_class}::class.java,")
            class_body.append("        ))")
        else:
            class_body[-1] = "        ))"

        class_body.extend([
            "    }",
            "}",
        ])

        return "\n".join(imports + class_body) + "\n"

    def _get_android_plugin_imports(self) -> list[str]:
        """Get Android plugin imports based on capabilities."""
        imports = []
        plugin_map = {
            "camera": "import com.capacitorjs.plugins.camera.CameraPlugin",
            "geolocation": "import com.capacitorjs.plugins.geolocation.GeolocationPlugin",
            "push": "import com.capacitorjs.plugins.pushnotifications.PushNotificationsPlugin",
            "local-notify": "import com.capacitorjs.plugins.localnotifications.LocalNotificationsPlugin",
            "biometrics": "import com.capacitorjs.plugins.biometrics.BiometricAuth",
        }
        for cap in self._config.capabilities:
            if cap in plugin_map:
                imports.append(plugin_map[cap])
        return imports

    def _get_android_plugin_classes(self) -> list[str]:
        """Get Android plugin class names for registration."""
        classes = []
        plugin_map = {
            "camera": "CameraPlugin",
            "geolocation": "GeolocationPlugin",
            "push": "PushNotificationsPlugin",
            "local-notify": "LocalNotificationsPlugin",
            "biometrics": "BiometricAuth",
        }
        for cap in self._config.capabilities:
            if cap in plugin_map:
                classes.append(plugin_map[cap])
        return classes

    def _generate_android_build_gradle(self) -> str:
        """Generate app/build.gradle for Android."""
        deps = [
            "implementation fileTree(dir: 'libs', include: ['*.jar'])",
            "implementation \"androidx.appcompat:appcompat:1.6.1\"",
            "implementation \"androidx.coordinatorlayout:coordinatorlayout:1.2.0\"",
            "implementation \"androidx.core:core-splashscreen:1.0.1\"",
            "implementation project(':capacitor-android')",
        ]

        # Add on-device dependencies
        if self._config.is_ondevice():
            deps.extend([
                "implementation \"com.chaquo.python:gradle:15.0.1\"",
            ])

        deps_str = "\n    ".join(deps)

        return textwrap.dedent(f"""\
            apply plugin: 'com.android.application'
            {"apply plugin: 'com.chaquo.python'" if self._config.is_ondevice() else ""}

            android {{
                namespace "{self._config.app_id}"
                compileSdk {self._config.target_sdk}

                defaultConfig {{
                    applicationId "{self._config.app_id}"
                    minSdk {self._config.min_sdk}
                    targetSdk {self._config.target_sdk}
                    versionCode 1
                    versionName "1.0"
                    multiDexEnabled true
                }}

                buildTypes {{
                    release {{
                        minifyEnabled false
                        proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
                    }}
                }}

                compileOptions {{
                    sourceCompatibility JavaVersion.VERSION_17
                    targetCompatibility JavaVersion.VERSION_17
                }}
            }}

            repositories {{
                flatDir {{
                    dirs '../capacitor-cordova-android-plugins/src/main/libs', 'libs'
                }}
            }}

            dependencies {{
                {deps_str}
            }}

            apply from: 'capacitor.build.gradle'

            try {{
                def servicesJSON = file('google-services.json')
                if (servicesJSON.text) {{
                    apply plugin: 'com.google.gms.google-services'
                }}
            }} catch(Exception e) {{
                logger.warn(
                    "google-services.json not found, "
                    "google-services plugin not applied. "
                    "Push Notifications won't work"
                )
            }}
        """)

    def _generate_android_strings(self) -> str:
        """Generate Android strings.xml."""
        app_name = self._config.app_name or self._config.app_id.split(".")[-1]
        return textwrap.dedent(f"""\
            <?xml version="1.0" encoding="utf-8"?>
            <resources>
                <string name="app_name">{app_name}</string>
                <string name="title_activity_main">{app_name}</string>
                <string name="package_name">{self._config.app_id}</string>
                <string name="custom_url_scheme">{self._config.app_id.split(".")[-1]}</string>
            </resources>
        """)

    def _generate_android_colors(self) -> str:
        """Generate Android colors.xml."""
        return textwrap.dedent(f"""\
            <?xml version="1.0" encoding="utf-8"?>
            <resources>
                <color name="ic_launcher_background">{self._config.background_color}</color>
                <color name="colorPrimary">#3F51B5</color>
                <color name="colorPrimaryDark">#303F9F</color>
                <color name="colorAccent">#FF4081</color>
            </resources>
        """)

    def _generate_network_security_config(self) -> str:
        """Generate network security config for Android."""
        return textwrap.dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <network-security-config>
                <base-config cleartextTrafficPermitted="false">
                    <trust-anchors>
                        <certificates src="system" />
                    </trust-anchors>
                </base-config>
            </network-security-config>
        """)

    def _generate_adaptive_icon(self) -> str:
        """Generate adaptive icon XML for Android."""
        return textwrap.dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
                <background android:drawable="@color/ic_launcher_background"/>
                <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
            </adaptive-icon>
        """)

    def _generate_chaquopy_bridge(self, android_dir: str, java_dir: str) -> list[str]:
        """Generate Chaquopy bridge files for on-device mode."""
        generated = []

        # OnDeviceBridge.kt
        bridge_kt = textwrap.dedent(f"""\
            package {self._config.app_id}

            import android.webkit.JavascriptInterface
            import android.webkit.WebView
            import com.chaquo.python.Python
            import com.chaquo.python.android.AndroidPlatform

            /**
             * On-device bridge - auto-generated by MikiUI.
             * Connects JavaScript calls to embedded Python via Chaquopy.
             */
            class OnDeviceBridge(private val webView: WebView) {{

                private var bridgeInstance: Any? = null

                init {{
                    // Initialize Chaquopy
                    if (!Python.isStarted()) {{
                        Python.start(AndroidPlatform(webView.context))
                    }}
                }}

                @JavascriptInterface
                fun call(method: String, path: String, dataJson: String): String {{
                    return try {{
                        val python = Python.getInstance()
                        val bridgeModule = python.getModule("bridge.chaquopy_bridge")
                        val getBridge = bridgeModule["get_bridge"]
                        val appModule = python.getModule("app")
                        val getApp = appModule["get_app"]
                        val app = getApp()
                        val bridge = getBridge(app)
                        bridge.call(method, path, dataJson)
                    }} catch (e: Exception) {{
                        "{{\\"error\\": \\"" + (e.message ?: "Unknown error") + "\\", \\"status\\": 500}}"
                    }}
                }}
            }}
        """)

        bridge_path = os.path.join(java_dir, "OnDeviceBridge.kt")
        with open(bridge_path, "w", encoding="utf-8") as f:
            f.write(bridge_kt)
        generated.append(bridge_path)

        return generated

    def _generate_ios_native(self) -> dict[str, Any]:
        """Generate iOS native project files."""
        ios_dir = self.ios_dir
        app_dir = os.path.join(ios_dir, "App")
        app_src_dir = os.path.join(app_dir, "App")

        os.makedirs(app_src_dir, exist_ok=True)

        generated_files = []

        # AppDelegate.swift
        app_delegate = self._generate_app_delegate_swift()
        app_delegate_path = os.path.join(app_src_dir, "AppDelegate.swift")
        with open(app_delegate_path, "w", encoding="utf-8") as f:
            f.write(app_delegate)
        generated_files.append(app_delegate_path)

        # Podfile
        podfile = self._generate_podfile()
        podfile_path = os.path.join(ios_dir, "Podfile")
        with open(podfile_path, "w", encoding="utf-8") as f:
            f.write(podfile)
        generated_files.append(podfile_path)

        # Info.plist (enhanced)
        info_plist = self._generate_ios_info_plist()
        info_plist_path = os.path.join(app_dir, "Info.plist")
        with open(info_plist_path, "w", encoding="utf-8") as f:
            f.write(info_plist)
        generated_files.append(info_plist_path)

        return {
            "status": "ok",
            "platform": "ios",
            "files": generated_files,
        }

    def _generate_app_delegate_swift(self) -> str:
        """Generate AppDelegate.swift for iOS."""
        return textwrap.dedent('''\
            import UIKit
            import Capacitor

            @UIApplicationMain
            class AppDelegate: UIResponder, UIApplicationDelegate {

                var window: UIWindow?

                func application(
                    _ application: UIApplication,
                    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
                ) -> Bool {
                    return true
                }

                func applicationWillResignActive(_ application: UIApplication) {}

                func applicationDidEnterBackground(_ application: UIApplication) {}

                func applicationWillEnterForeground(_ application: UIApplication) {}

                func applicationDidBecomeActive(_ application: UIApplication) {}

                func applicationWillTerminate(_ application: UIApplication) {}

                func application(
                    _ app: UIApplication,
                    open url: URL,
                    options: [UIApplication.OpenURLOptionsKey: Any] = [:]
                ) -> Bool {
                    return ApplicationDelegateProxy.shared.application(app, open: url, options: options)
                }

                func application(
                    _ application: UIApplication,
                    continue userActivity: NSUserActivity,
                    restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void
                ) -> Bool {
                    return ApplicationDelegateProxy.shared.application(
                        application, continue: userActivity, restorationHandler: restorationHandler
                    )
                }

                override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
                    super.touchesBegan(touches, with: event)
                    statusBarTouchesBegan(touches, with: event)
                }

                private func statusBarTouchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
                    if let touch = touches.first, touch.tapCount == 1, touch.phase == .began {
                        NotificationCenter.default.post(name: .capacitorStatusBarTouchesBegan, object: nil)
                    }
                }
            }
        ''')

    def _generate_podfile(self) -> str:
        """Generate Podfile for iOS."""
        pods = [
            "  pod 'Capacitor'",
            "  pod 'CapacitorCordova'",
        ]

        # Add plugin pods
        pod_map = {
            "camera": "  pod 'CapacitorCamera'",
            "geolocation": "  pod 'CapacitorGeolocation'",
            "push": "  pod 'CapacitorPushNotifications'",
            "local-notify": "  pod 'CapacitorLocalNotifications'",
            "haptics": "  pod 'CapacitorHaptics'",
            "clipboard": "  pod 'CapacitorClipboard'",
            "filesystem": "  pod 'CapacitorFilesystem'",
            "share": "  pod 'CapacitorShare'",
            "network-status": "  pod 'CapacitorNetwork'",
            "status-bar": "  pod 'CapacitorStatusBar'",
            "biometrics": "  pod 'CapacitorBiometrics'",
            "keyboard": "  pod 'CapacitorKeyboard'",
            "device-info": "  pod 'CapacitorDevice'",
            "screen-orientation": "  pod 'CapacitorScreenOrientation'",
            "safe-area": "  pod 'CapacitorSafeArea'",
            "browser": "  pod 'CapacitorBrowser'",
        }

        for cap in self._config.capabilities:
            if cap in pod_map:
                pods.append(pod_map[cap])

        pods_str = "\n".join(pods)

        return textwrap.dedent(f'''\
            require_relative '../../node_modules/@capacitor/ios/scripts/pod_helpers'

            platform :ios, '14.0'
            use_frameworks!

            # Add your Pods here
            {pods_str}

            target 'App' do
              capacitor_pods
            end

            post_install do |installer|
              installer.pods_project.targets.each do |target|
                target.build_configurations.each do |config|
                  config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '14.0'
                end
              end
            end
        ''')

    def _generate_ios_info_plist(self) -> str:
        """Generate enhanced Info.plist for iOS."""
        # Get privacy keys
        privacy_keys = self._config.get_ios_privacy_keys()
        privacy_entries = []
        for key, description in privacy_keys.items():
            privacy_entries.append(f"    <key>{key}</key>")
            privacy_entries.append(f"    <string>{description}</string>")

        # Add UIBackgroundModes for push
        background_modes = []
        if "push" in self._config.capabilities:
            background_modes.append("        <string>remote-notification</string>")

        background_modes_str = ""
        if background_modes:
            background_modes_str = f"""\
            <key>UIBackgroundModes</key>
            <array>
{chr(10).join(background_modes)}
            </array>"""

        privacy_entries_str = "\n".join(privacy_entries) if privacy_entries else ""

        return textwrap.dedent(f'''\
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>CFBundleDevelopmentRegion</key>
                <string>en</string>
                <key>CFBundleDisplayName</key>
                <string>{self._config.app_name or self._config.app_id.split(".")[-1]}</string>
                <key>CFBundleExecutable</key>
                <string>$(EXECUTABLE_NAME)</string>
                <key>CFBundleIdentifier</key>
                <string>{self._config.app_id}</string>
                <key>CFBundleInfoDictionaryVersion</key>
                <string>6.0</string>
                <key>CFBundleName</key>
                <string>{self._config.app_name or self._config.app_id.split(".")[-1]}</string>
                <key>CFBundlePackageType</key>
                <string>APPL</string>
                <key>CFBundleShortVersionString</key>
                <string>1.0</string>
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
                <key>UISupportedInterfaceOrientations~ipad</key>
                <array>
                    <string>UIInterfaceOrientationPortrait</string>
                    <string>UIInterfaceOrientationPortraitUpsideDown</string>
                    <string>UIInterfaceOrientationLandscapeLeft</string>
                    <string>UIInterfaceOrientationLandscapeRight</string>
                </array>
                <key>NSAppTransportSecurity</key>
                <dict>
                    <key>NSAllowsArbitraryLoads</key>
                    <{str(self._config.allow_cleartext).lower()}/>
                </dict>
                {privacy_entries_str}
                {background_modes_str}
            </dict>
            </plist>
        ''')

    # ====================================================================
    # 2. AUTOMATED PLUGIN INSTALLATION AND SYNC
    # ====================================================================

    def install_plugins(self) -> dict[str, Any]:
        """Automatically install all required Capacitor plugins.

        This runs:
        1. npm install (base dependencies)
        2. npm install for each required plugin
        3. npx cap sync
        """
        results: dict[str, Any] = {
            "npm_install": None,
            "plugin_installs": [],
            "cap_sync": None,
        }

        # Check if we're in the right directory
        if not os.path.exists(self._out_dir):
            return {"status": "error", "message": f"Output directory not found: {self._out_dir}"}

        # Step 1: npm install
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=self._out_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            results["npm_install"] = {
                "status": "ok" if result.returncode == 0 else "error",
                "output": result.stdout[-500:] if result.stdout else "",
                "error": result.stderr[-500:] if result.returncode != 0 and result.stderr else None,
            }
        except Exception as e:
            results["npm_install"] = {"status": "error", "message": str(e)}

        # Step 2: Install plugins
        plugins = self._config.get_capacitor_plugins()
        for plugin in plugins:
            try:
                result = subprocess.run(
                    ["npm", "install", plugin],
                    cwd=self._out_dir,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                results["plugin_installs"].append({
                    "plugin": plugin,
                    "status": "ok" if result.returncode == 0 else "error",
                    "error": result.stderr[-200:] if result.returncode != 0 and result.stderr else None,
                })
            except Exception as e:
                results["plugin_installs"].append({
                    "plugin": plugin,
                    "status": "error",
                    "message": str(e),
                })

        # Step 3: npx cap sync
        try:
            result = subprocess.run(
                ["npx", "cap", "sync"],
                cwd=self._out_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            results["cap_sync"] = {
                "status": "ok" if result.returncode == 0 else "error",
                "output": result.stdout[-500:] if result.stdout else "",
                "error": result.stderr[-500:] if result.returncode != 0 and result.stderr else None,
            }
        except Exception as e:
            results["cap_sync"] = {"status": "error", "message": str(e)}

        return results

    # ====================================================================
    # 3. ONE-CLICK DEVICE TESTING
    # ====================================================================

    def run_on_device(
        self,
        platform: str,
        device_type: str = "emulator",
        device_id: str | None = None,
    ) -> dict[str, Any]:
        """Run the app on a device or emulator with one command.

        Args:
            platform: "android" or "ios"
            device_type: "emulator", "simulator", or "device"
            device_id: Specific device ID (optional)
        """
        if not os.path.exists(self._out_dir):
            return {"status": "error", "message": f"Output directory not found: {self._out_dir}"}

        if platform == "android":
            return self._run_on_android(device_type, device_id)
        elif platform == "ios":
            return self._run_on_ios(device_type, device_id)
        else:
            return {"status": "error", "message": f"Unsupported platform: {platform}"}

    def _run_on_android(self, device_type: str, device_id: str | None) -> dict[str, Any]:
        """Run on Android device or emulator."""
        # First, ensure plugins are synced
        sync_result = subprocess.run(
            ["npx", "cap", "sync", "android"],
            cwd=self._out_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if sync_result.returncode != 0:
            return {
                "status": "error",
                "message": "Failed to sync Android project",
                "error": sync_result.stderr[-500:] if sync_result.stderr else None,
            }

        # Build the command
        cmd = ["npx", "cap", "run", "android"]

        if device_id:
            cmd.extend(["--target", device_id])
        elif device_type == "emulator":
            cmd.append("--emulator")

        # Run
        try:
            result = subprocess.run(
                cmd,
                cwd=self._out_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )
            return {
                "status": "ok" if result.returncode == 0 else "error",
                "platform": "android",
                "device_type": device_type,
                "output": result.stdout[-1000:] if result.stdout else "",
                "error": result.stderr[-500:] if result.returncode != 0 and result.stderr else None,
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Build timed out after 5 minutes"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _run_on_ios(self, device_type: str, device_id: str | None) -> dict[str, Any]:
        """Run on iOS device or simulator."""
        # First, ensure plugins are synced
        sync_result = subprocess.run(
            ["npx", "cap", "sync", "ios"],
            cwd=self._out_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if sync_result.returncode != 0:
            return {
                "status": "error",
                "message": "Failed to sync iOS project",
                "error": sync_result.stderr[-500:] if sync_result.stderr else None,
            }

        # Build the command
        cmd = ["npx", "cap", "run", "ios"]

        if device_id:
            cmd.extend(["--target", device_id])
        elif device_type == "simulator":
            cmd.append("--simulator")

        # Run
        try:
            result = subprocess.run(
                cmd,
                cwd=self._out_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )
            return {
                "status": "ok" if result.returncode == 0 else "error",
                "platform": "ios",
                "device_type": device_type,
                "output": result.stdout[-1000:] if result.stdout else "",
                "error": result.stderr[-500:] if result.returncode != 0 and result.stderr else None,
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Build timed out after 5 minutes"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_devices(self, platform: str) -> dict[str, Any]:
        """List available devices for a platform."""
        if platform == "android":
            return self._list_android_devices()
        elif platform == "ios":
            return self._list_ios_devices()
        else:
            return {"status": "error", "message": f"Unsupported platform: {platform}"}

    def _list_android_devices(self) -> dict[str, Any]:
        """List available Android devices and emulators."""
        devices: dict[str, Any] = {"emulators": [], "physical": []}

        # List emulators
        try:
            result = subprocess.run(
                ["emulator", "-list-avds"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                devices["emulators"] = [
                    line.strip() for line in result.stdout.split("\n") if line.strip()
                ]
        except Exception:
            pass

        # List connected devices
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n")[1:]:
                    if line.strip() and "\tdevice" in line:
                        device_id = line.split("\t")[0]
                        devices["physical"].append(device_id)
        except Exception:
            pass

        return {"status": "ok", "platform": "android", "devices": devices}

    def _list_ios_devices(self) -> dict[str, Any]:
        """List available iOS devices and simulators."""
        devices: dict[str, Any] = {"simulators": [], "physical": []}

        # List simulators
        try:
            result = subprocess.run(
                ["xcrun", "simctl", "list", "devices", "available"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "(" in line and ")" in line and "iPhone" in line or "iPad" in line:
                        name = line.split("(")[0].strip()
                        if name:
                            devices["simulators"].append(name)
        except Exception:
            pass

        # List connected devices
        try:
            result = subprocess.run(
                ["xcrun", "simctl", "list", "devices", "booted"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "Booted" in line:
                        name = line.split("(")[0].strip()
                        if name:
                            devices["physical"].append(name)
        except Exception:
            pass

        return {"status": "ok", "platform": "ios", "devices": devices}

    # ====================================================================
    # 4. CODE SIGNING AUTOMATION
    # ====================================================================

    def setup_code_signing(
        self,
        platform: str,
        keystore_path: str | None = None,
        keystore_password: str | None = None,
        key_alias: str | None = None,
        key_password: str | None = None,
        team_id: str | None = None,
        bundle_id: str | None = None,
    ) -> dict[str, Any]:
        """Set up code signing for Android or iOS.

        Args:
            platform: "android" or "ios"
            keystore_path: Path to Android keystore file
            keystore_password: Keystore password
            key_alias: Key alias
            key_password: Key password
            team_id: Apple Developer Team ID (iOS only)
            bundle_id: Bundle identifier (iOS only)
        """
        if platform == "android":
            return self._setup_android_signing(
                keystore_path, keystore_password, key_alias, key_password
            )
        elif platform == "ios":
            return self._setup_ios_signing(team_id, bundle_id)
        else:
            return {"status": "error", "message": f"Unsupported platform: {platform}"}

    def _setup_android_signing(
        self,
        keystore_path: str | None,
        keystore_password: str | None,
        key_alias: str | None,
        key_password: str | None,
    ) -> dict[str, Any]:
        """Set up Android code signing."""
        android_dir = self.android_dir
        app_dir = os.path.join(android_dir, "app")

        # Generate keystore if not provided
        if not keystore_path:
            keystore_path = os.path.join(android_dir, "release.keystore")
            if not os.path.exists(keystore_path):
                result = subprocess.run(
                    [
                        "keytool", "-genkey", "-v",
                        "-keystore", keystore_path,
                        "-keyalg", "RSA", "-keysize", "2048",
                        "-validity", "10000",
                        "-alias", key_alias or "release",
                        "-storepass", keystore_password or "password",
                        "-keypass", key_password or "password",
                        "-dname", f"CN={self._config.app_id}, OU=MikiUI, O=MikiUI, L=Unknown, S=Unknown, C=US",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    return {"status": "error", "message": f"Failed to generate keystore: {result.stderr}"}

        # Create signing config in build.gradle
        signing_config = textwrap.dedent(f"""\
            signingConfigs {{
                release {{
                    storeFile file('{os.path.basename(keystore_path)}')
                    storePassword '{keystore_password or "password"}'
                    keyAlias '{key_alias or "release"}'
                    keyPassword '{key_password or "password"}'
                }}
            }}
        """)

        # Update build.gradle
        build_gradle_path = os.path.join(app_dir, "build.gradle")
        if os.path.exists(build_gradle_path):
            with open(build_gradle_path, encoding="utf-8") as f:
                content = f.read()

            # Add signing config before buildTypes
            if "signingConfigs" not in content:
                content = content.replace(
                    "buildTypes {",
                    signing_config + "\n            buildTypes {"
                )

            # Update release build type to use signing
            content = content.replace(
                "release {\n                    minifyEnabled false",
                "release {\n                    signingConfig "
                "signingConfigs.release\n                    minifyEnabled false"
            )

            with open(build_gradle_path, "w", encoding="utf-8") as f:
                f.write(content)

        return {
            "status": "ok",
            "platform": "android",
            "keystore_path": keystore_path,
            "message": "Android code signing configured. Build with: cd android && ./gradlew bundleRelease",
        }

    def _setup_ios_signing(self, team_id: str | None, bundle_id: str | None) -> dict[str, Any]:
        """Set up iOS code signing."""
        ios_dir = self.ios_dir

        # Create export options plist
        export_options = {
            "method": "app-store",
            "teamID": team_id or "YOUR_TEAM_ID",
            "uploadBitcode": False,
            "uploadSymbols": True,
        }

        export_options_path = os.path.join(ios_dir, "ExportOptions.plist")
        with open(export_options_path, "w", encoding="utf-8") as f:
            # Write plist XML
            plist_content = ['<?xml version="1.0" encoding="UTF-8"?>']
            plist_content.append('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">')
            plist_content.append('<plist version="1.0">')
            plist_content.append("<dict>")
            for key, value in export_options.items():
                if isinstance(value, bool):
                    plist_content.append(f"    <key>{key}</key>")
                    plist_content.append(f"    <{'true' if value else 'false'}/>")
                else:
                    plist_content.append(f"    <key>{key}</key>")
                    plist_content.append(f"    <string>{value}</string>")
            plist_content.append("</dict>")
            plist_content.append("</plist>")
            f.write("\n".join(plist_content))

        return {
            "status": "ok",
            "platform": "ios",
            "export_options_path": export_options_path,
            "message": "iOS code signing configured. Archive in Xcode and use ExportOptions.plist",
        }

    # ====================================================================
    # 5. STORE SUBMISSION AUTOMATION
    # ====================================================================

    def prepare_for_submission(self, platform: str) -> dict[str, Any]:
        """Prepare the app for store submission.

        This:
        1. Builds the release version
        2. Generates required metadata
        3. Creates screenshot templates
        4. Provides submission instructions
        """
        if platform == "android":
            return self._prepare_android_submission()
        elif platform == "ios":
            return self._prepare_ios_submission()
        else:
            return {"status": "error", "message": f"Unsupported platform: {platform}"}

    def _prepare_android_submission(self) -> dict[str, Any]:
        """Prepare Android app for Play Store submission."""
        android_dir = self.android_dir

        # Build release AAB
        build_result = subprocess.run(
            ["./gradlew", "bundleRelease"],
            cwd=android_dir,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if build_result.returncode != 0:
            return {
                "status": "error",
                "message": "Failed to build release bundle",
                "error": build_result.stderr[-1000:] if build_result.stderr else None,
            }

        # Find the AAB file
        aab_path = None
        for root, dirs, files in os.walk(os.path.join(android_dir, "app", "build", "outputs", "bundle", "release")):
            for f in files:
                if f.endswith(".aab"):
                    aab_path = os.path.join(root, f)
                    break

        return {
            "status": "ok",
            "platform": "android",
            "aab_path": aab_path,
            "message": f"Release bundle built: {aab_path}",
            "next_steps": [
                "Go to https://play.google.com/console",
                "Create a new app or select existing",
                "Upload the AAB file",
                "Fill in store listing",
                "Submit for review",
            ],
        }

    def _prepare_ios_submission(self) -> dict[str, Any]:
        """Prepare iOS app for App Store submission."""
        ios_dir = self.ios_dir

        # Build archive
        build_result = subprocess.run(
            [
                "xcodebuild", "-workspace", "App.xcworkspace",
                "-scheme", "App",
                "-configuration", "Release",
                "-archivePath", "build/App.xcarchive",
                "archive",
            ],
            cwd=ios_dir,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if build_result.returncode != 0:
            return {
                "status": "error",
                "message": "Failed to build archive",
                "error": build_result.stderr[-1000:] if build_result.stderr else None,
            }

        return {
            "status": "ok",
            "platform": "ios",
            "archive_path": os.path.join(ios_dir, "build", "App.xcarchive"),
            "message": "Archive built successfully",
            "next_steps": [
                "Open Xcode Organizer",
                "Select the archive",
                "Click 'Distribute App'",
                "Select 'App Store Connect'",
                "Upload",
            ],
        }


def run_full_automation(
    app: Any,
    out_dir: str = "dist_mobile",
    platform: str = "both",
    device_type: str = "emulator",
) -> dict[str, Any]:
    """Run the full mobile automation pipeline.

    This is the one-click solution that:
    1. Builds the mobile project
    2. Generates native project files
    3. Installs plugins
    4. Syncs with Capacitor
    5. Runs on device/emulator
    """
    automation = MobileAutomation(app, out_dir)
    results: dict[str, Any] = {
        "build": None,
        "native_files": None,
        "plugins": None,
        "run": None,
    }

    # Step 1: Build
    from .mobile_build import build_mobile
    results["build"] = build_mobile(app, out_dir=out_dir)

    # Step 2: Generate native files
    results["native_files"] = automation.generate_native_projects()

    # Step 3: Install plugins
    results["plugins"] = automation.install_plugins()

    # Step 4: Run on device
    if platform == "both":
        results["run"] = {
            "android": automation.run_on_device("android", device_type),
            "ios": automation.run_on_device("ios", "simulator" if device_type == "emulator" else device_type),
        }
    else:
        results["run"] = automation.run_on_device(platform, device_type)

    return results


__all__ = ["MobileAutomation", "run_full_automation"]
