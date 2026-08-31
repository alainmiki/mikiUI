"""Mobile configuration for MikiUI applications.

Defines :class:`MobileConfig` which controls how an app is built for mobile
targets (cloud mode via Capacitor, or on-device mode via Chaquopy).

Usage::

    from mikiui import MikiApp
    from mikiui.app.mobile import MobileConfig

    app = MikiApp(
        title="My App",
        mobile=MobileConfig(
            backend="cloud",
            api_base="https://api.example.com",
            plugins=["Camera", "Geolocation"],
        ),
    )
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MobileBackend(StrEnum):
    """Mobile backend mode."""

    CLOUD = "cloud"
    ONDEVICE = "ondevice"


class MobilePlatform(StrEnum):
    """Target mobile platform."""

    ANDROID = "android"
    IOS = "ios"
    BOTH = "both"


# Mapping from Python capability names to Capacitor plugins + native permissions
CAPABILITY_MAP: dict[str, dict[str, Any]] = {
    "camera": {
        "capacitor_plugin": "@capacitor/camera",
        "android_permission": "android.permission.CAMERA",
        "ios_privacy_key": "NSCameraUsageDescription",
        "ios_privacy_description": "This app needs camera access to take photos and scan codes.",
    },
    "geolocation": {
        "capacitor_plugin": "@capacitor/geolocation",
        "android_permission": [
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
        ],
        "ios_privacy_key": "NSLocationWhenInUseUsageDescription",
        "ios_privacy_description": "This app needs location access to provide location-based features.",
    },
    "push": {
        "capacitor_plugin": "@capacitor/push-notifications",
        "android_permission": "android.permission.POST_NOTIFICATIONS",
        "ios_privacy_key": "UIBackgroundModes",
        "ios_privacy_description": None,  # Uses UIBackgroundModes array in plist
    },
    "local-notify": {
        "capacitor_plugin": "@capacitor/local-notifications",
        "android_permission": "android.permission.SCHEDULE_EXACT_ALARM",
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "haptics": {
        "capacitor_plugin": "@capacitor/haptics",
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "clipboard": {
        "capacitor_plugin": "@capacitor/clipboard",
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "filesystem": {
        "capacitor_plugin": "@capacitor/filesystem",
        "android_permission": [
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.WRITE_EXTERNAL_STORAGE",
        ],
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "share": {
        "capacitor_plugin": "@capacitor/share",
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "network-status": {
        "capacitor_plugin": "@capacitor/network",
        "android_permission": "android.permission.ACCESS_NETWORK_STATE",
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "status-bar": {
        "capacitor_plugin": "@capacitor/status-bar",
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "biometrics": {
        "capacitor_plugin": "@capacitor/biometrics",
        "android_permission": "android.permission.USE_BIOMETRIC",
        "ios_privacy_key": "NSFaceIDUsageDescription",
        "ios_privacy_description": "This app uses Face ID for secure authentication.",
    },
    "battery": {
        "capacitor_plugin": None,  # Uses browser Battery Status API
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "device-info": {
        "capacitor_plugin": "@capacitor/device",
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "keyboard": {
        "capacitor_plugin": "@capacitor/keyboard",
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "app-lifecycle": {
        "capacitor_plugin": None,  # Uses Capacitor App plugin (built-in)
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "deep-link": {
        "capacitor_plugin": None,  # Configured in capacitor.config.json
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "media-player": {
        "capacitor_plugin": "@capacitor-community/native-audio",
        "android_permission": "android.permission.WAKE_LOCK",
        "ios_privacy_key": "NSMicrophoneUsageDescription",
        "ios_privacy_description": "This app needs microphone access for audio recording.",
    },
    "video-capture": {
        "capacitor_plugin": "@capacitor/camera",
        "android_permission": "android.permission.CAMERA",
        "ios_privacy_key": "NSCameraUsageDescription",
        "ios_privacy_description": "This app needs camera access to record video.",
    },
    "audio-capture": {
        "capacitor_plugin": "@capacitor-community/native-audio",
        "android_permission": "android.permission.RECORD_AUDIO",
        "ios_privacy_key": "NSMicrophoneUsageDescription",
        "ios_privacy_description": "This app needs microphone access for audio recording.",
    },
    "sensors": {
        "capacitor_plugin": None,  # Uses Generic Sensor API
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "nfc": {
        "capacitor_plugin": "@capacitor-community/nfc",
        "android_permission": "android.permission.NFC",
        "ios_privacy_key": "NFCReaderUsageDescription",
        "ios_privacy_description": "This app uses NFC to read tags.",
    },
    "bluetooth": {
        "capacitor_plugin": None,  # Uses Web Bluetooth API
        "android_permission": [
            "android.permission.BLUETOOTH",
            "android.permission.BLUETOOTH_ADMIN",
            "android.permission.BLUETOOTH_CONNECT",
        ],
        "ios_privacy_key": "NSBluetoothAlwaysUsageDescription",
        "ios_privacy_description": "This app uses Bluetooth to connect to devices.",
    },
    "contacts": {
        "capacitor_plugin": "@capacitor-community/contacts",
        "android_permission": [
            "android.permission.READ_CONTACTS",
            "android.permission.WRITE_CONTACTS",
        ],
        "ios_privacy_key": "NSContactsUsageDescription",
        "ios_privacy_description": "This app needs contact access to sync your address book.",
    },
    "calendar": {
        "capacitor_plugin": "@capacitor-community/calendar",
        "android_permission": [
            "android.permission.READ_CALENDAR",
            "android.permission.WRITE_CALENDAR",
        ],
        "ios_privacy_key": "NSCalendarsUsageDescription",
        "ios_privacy_description": "This app needs calendar access to manage events.",
    },
    "sms": {
        "capacitor_plugin": None,  # Uses sms: URL scheme
        "android_permission": "android.permission.SEND_SMS",
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "call": {
        "capacitor_plugin": None,  # Uses tel: URL scheme
        "android_permission": "android.permission.CALL_PHONE",
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "vibration": {
        "capacitor_plugin": None,  # Uses Vibration API
        "android_permission": "android.permission.VIBRATE",
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "screen-orientation": {
        "capacitor_plugin": "@capacitor/screen-orientation",
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "safe-area": {
        "capacitor_plugin": "@capacitor/safe-area",
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "browser": {
        "capacitor_plugin": "@capacitor/browser",
        "android_permission": None,
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "in-app-purchase": {
        "capacitor_plugin": "@capacitor-community/purchases",
        "android_permission": "com.android.vending.BILLING",
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "file-picker": {
        "capacitor_plugin": "@capacitor-community/file-picker",
        "android_permission": "android.permission.READ_EXTERNAL_STORAGE",
        "ios_privacy_key": None,
        "ios_privacy_description": None,
    },
    "photo-gallery": {
        "capacitor_plugin": "@capacitor/camera",
        "android_permission": "android.permission.READ_MEDIA_IMAGES",
        "ios_privacy_key": "NSPhotoLibraryUsageDescription",
        "ios_privacy_description": "This app needs photo library access to save and select images.",
    },
}


@dataclass
class MobileConfig:
    """Configuration for mobile builds.

    :param backend: ``"cloud"`` (default) or ``"ondevice"`` (Android only).
    :param api_base: Base URL for the backend API (cloud mode).
    :param ws_base: Base URL for WebSocket connections (cloud mode).
    :param target_platform: ``"android"``, ``"ios"``, or ``"both"``.
    :param plugins: List of Capacitor plugin names to include.
    :param capabilities: Native capabilities required (auto-derived from plugins).
    :param app_id: Android application ID / iOS bundle ID.
    :param app_name: Display name for the mobile app.
    :param orientation: Default orientation (``"portrait"``, ``"landscape"``, ``"default"``).
    :param background_color: App background color (hex).
    :param splash_duration: Splash screen duration in milliseconds.
    :param chaquopy_deps: Python packages to bundle (on-device mode only).
    :param allow_cleartext: Allow cleartext traffic (on-device localhost only).
    :param min_sdk: Minimum Android SDK version.
    :param target_sdk: Target Android SDK version.
    """

    backend: str | MobileBackend = MobileBackend.CLOUD
    api_base: str | None = None
    ws_base: str | None = None
    target_platform: str | MobilePlatform = MobilePlatform.BOTH
    plugins: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    app_id: str = "com.mikiui.app"
    app_name: str | None = None
    orientation: str = "default"
    background_color: str = "#ffffff"
    splash_duration: int = 3000
    chaquopy_deps: list[str] = field(default_factory=list)
    allow_cleartext: bool = False
    min_sdk: int = 23
    target_sdk: int = 34

    def __post_init__(self) -> None:
        import re

        self.backend = (
            self.backend if isinstance(self.backend, MobileBackend)
            else MobileBackend(str(self.backend).lower())
        )
        self.target_platform = (
            self.target_platform if isinstance(self.target_platform, MobilePlatform)
            else MobilePlatform(str(self.target_platform).lower())
        )

        if self.backend not in ("cloud", "ondevice"):
            raise ValueError(f"Invalid backend: {self.backend!r}. Use 'cloud' or 'ondevice'.")

        if self.target_platform not in ("android", "ios", "both"):
            raise ValueError(
                f"Invalid target_platform: {self.target_platform!r}. "
                "Use 'android', 'ios', or 'both'."
            )

        # iOS does not support on-device mode
        if self.backend == "ondevice" and self.target_platform == "ios":
            raise ValueError(
                "iOS does not support on-device backend mode. "
                "Use backend='cloud' for iOS, or target_platform='android' for on-device."
            )

        # Validate app ID format (must be valid Java/Kotlin package name)
        if not re.match(r'^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)+$', self.app_id):
            raise ValueError(
                f"Invalid app ID: {self.app_id!r}. "
                "Must be a valid package name like 'com.example.myapp' "
                "(lowercase, dot separators, no special characters)."
            )

        # Validate app name
        if self.app_name and len(self.app_name) > 50:
            raise ValueError("App name must be 50 characters or fewer.")

        # Validate orientation
        if self.orientation not in ("portrait", "landscape", "default"):
            raise ValueError(
                f"Invalid orientation: {self.orientation!r}. "
                "Use 'portrait', 'landscape', or 'default'."
            )

        # Auto-derive capabilities from plugins
        for plugin in self.plugins:
            cap = plugin.lower().replace("-", "_").replace(" ", "_")
            if cap in CAPABILITY_MAP:
                entry = CAPABILITY_MAP[cap]
                for key in entry:
                    if entry[key] and key not in self.capabilities:
                        if key not in ("android_permission", "ios_privacy_key", "ios_privacy_description"):
                            continue

    def is_cloud(self) -> bool:
        return self.backend == "cloud"

    def is_ondevice(self) -> bool:
        return self.backend == "ondevice"

    def targets_android(self) -> bool:
        return self.target_platform in ("android", "both")

    def targets_ios(self) -> bool:
        return self.target_platform in ("ios", "both")

    def get_android_permissions(self) -> list[str]:
        """Return list of Android permissions required by enabled capabilities."""
        permissions: list[str] = []
        all_caps = list(self.capabilities)
        for plugin in self.plugins:
            cap = plugin.lower().replace("-", "_").replace(" ", "_")
            if cap in CAPABILITY_MAP and cap not in all_caps:
                all_caps.append(cap)
        for cap in all_caps:
            entry = CAPABILITY_MAP.get(cap)
            if entry and entry.get("android_permission"):
                perm = entry["android_permission"]
                # Permission can be a string or list of strings
                if isinstance(perm, list):
                    for p in perm:
                        if p not in permissions:
                            permissions.append(p)
                elif perm not in permissions:
                    permissions.append(perm)
        return permissions

    def get_ios_privacy_keys(self) -> dict[str, str]:
        """Return dict of iOS privacy keys and their descriptions."""
        keys: dict[str, str] = {}
        all_caps = list(self.capabilities)
        for plugin in self.plugins:
            cap = plugin.lower().replace("-", "_").replace(" ", "_")
            if cap in CAPABILITY_MAP and cap not in all_caps:
                all_caps.append(cap)
        for cap in all_caps:
            entry = CAPABILITY_MAP.get(cap)
            if entry and entry.get("ios_privacy_key") and entry.get("ios_privacy_description"):
                key = entry["ios_privacy_key"]
                if key not in keys:
                    keys[key] = entry["ios_privacy_description"]
        return keys

    def get_capacitor_plugins(self) -> list[str]:
        """Return list of Capacitor npm package names."""
        plugins: list[str] = []
        # Check both capabilities and plugins list
        all_caps = list(self.capabilities)
        # Auto-derive capabilities from plugins if not already set
        for plugin in self.plugins:
            cap = plugin.lower().replace("-", "_").replace(" ", "_")
            if cap in CAPABILITY_MAP and cap not in all_caps:
                all_caps.append(cap)
        for cap in all_caps:
            entry = CAPABILITY_MAP.get(cap)
            if entry and entry.get("capacitor_plugin"):
                plugin = entry["capacitor_plugin"]
                if plugin not in plugins:
                    plugins.append(plugin)
        return plugins

    def get_cors_origins(self) -> list[str]:
        """Return CORS origins that should be allowed for mobile."""
        origins = []
        if self.api_base:
            origins.append(self.api_base)
        if self.backend == "ondevice":
            origins.append("http://localhost:8080")
            origins.append("http://127.0.0.1:8080")
        return origins

    @classmethod
    def from_env(cls) -> MobileConfig:
        """Create a MobileConfig from environment variables."""
        return cls(
            backend=os.environ.get("MIKIUI_MOBILE_BACKEND", "cloud"),
            api_base=os.environ.get("MIKIUI_MOBILE_API_BASE"),
            ws_base=os.environ.get("MIKIUI_MOBILE_WS_BASE"),
            target_platform=os.environ.get("MIKIUI_MOBILE_PLATFORM", "both"),
            app_id=os.environ.get("MIKIUI_MOBILE_APP_ID", "com.mikiui.app"),
            orientation=os.environ.get("MIKIUI_MOBILE_ORIENTATION", "default"),
        )

    def collect_capabilities_from_plugins(self, plugins: list[Any]) -> None:
        """Auto-collect capabilities from registered plugins.

        Scans all registered plugins for their ``capabilities`` attribute
        and adds them to this config's capabilities list.
        """
        for plugin in plugins:
            plugin_caps = getattr(plugin, "capabilities", [])
            for cap in plugin_caps:
                cap_normalized = cap.lower().replace(":", "_").replace("-", "_").replace(" ", "_")
                if cap_normalized not in self.capabilities:
                    self.capabilities.append(cap_normalized)
            # Also check plugin name as a capability
            plugin_name = getattr(plugin, "name", "").lower().replace("-", "_")
            if plugin_name and plugin_name in CAPABILITY_MAP and plugin_name not in self.capabilities:
                self.capabilities.append(plugin_name)


__all__ = [
    "MobileConfig",
    "MobileBackend",
    "MobilePlatform",
    "CAPABILITY_MAP",
]
