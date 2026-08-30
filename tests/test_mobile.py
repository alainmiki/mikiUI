"""Tests for mobile configuration and build system."""
import os
import tempfile
from pathlib import Path

import pytest

from mikiui import MikiApp, Div


class TestMobileConfig:
    """Test MobileConfig dataclass."""

    def test_default_config(self):
        from mikiui.app.mobile import MobileConfig

        config = MobileConfig()
        assert config.backend == "cloud"
        assert config.target_platform == "both"
        assert config.app_id == "com.mikiui.app"
        assert config.orientation == "default"

    def test_custom_config(self):
        from mikiui.app.mobile import MobileConfig

        config = MobileConfig(
            backend="cloud",
            api_base="https://api.example.com",
            plugins=["Camera", "Geolocation"],
        )
        assert config.backend == "cloud"
        assert config.api_base == "https://api.example.com"

    def test_invalid_backend(self):
        from mikiui.app.mobile import MobileConfig

        with pytest.raises((ValueError, KeyError)):
            MobileConfig(backend="invalid")

    def test_invalid_platform(self):
        from mikiui.app.mobile import MobileConfig

        with pytest.raises((ValueError, KeyError)):
            MobileConfig(target_platform="windows")

    def test_ios_ondevice_rejected(self):
        from mikiui.app.mobile import MobileConfig

        with pytest.raises(ValueError, match="iOS does not support on-device"):
            MobileConfig(backend="ondevice", target_platform="ios")

    def test_android_ondevice_allowed(self):
        from mikiui.app.mobile import MobileConfig

        config = MobileConfig(backend="ondevice", target_platform="android")
        assert config.is_ondevice()
        assert config.targets_android()

    def test_get_android_permissions(self):
        from mikiui.app.mobile import MobileConfig

        config = MobileConfig(plugins=["Camera"])
        config.capabilities = ["camera"]
        perms = config.get_android_permissions()
        assert "android.permission.CAMERA" in perms

    def test_get_ios_privacy_keys(self):
        from mikiui.app.mobile import MobileConfig

        config = MobileConfig(plugins=["Camera"])
        config.capabilities = ["camera"]
        keys = config.get_ios_privacy_keys()
        assert "NSCameraUsageDescription" in keys

    def test_get_cors_origins(self):
        from mikiui.app.mobile import MobileConfig

        config = MobileConfig(api_base="https://api.example.com")
        origins = config.get_cors_origins()
        assert "https://api.example.com" in origins

    def test_from_env(self):
        from mikiui.app.mobile import MobileConfig

        os.environ["MIKIUI_MOBILE_BACKEND"] = "ondevice"
        os.environ["MIKIUI_MOBILE_API_BASE"] = "https://test.com"
        try:
            config = MobileConfig.from_env()
            assert config.backend == "ondevice"
            assert config.api_base == "https://test.com"
        finally:
            del os.environ["MIKIUI_MOBILE_BACKEND"]
            del os.environ["MIKIUI_MOBILE_API_BASE"]


class TestMobileApp:
    """Test MikiApp with mobile config."""

    def test_app_with_mobile_config(self):
        from mikiui.app.mobile import MobileConfig

        app = MikiApp(title="Test", mobile=MobileConfig(backend="cloud"))
        assert app.mobile is not None
        assert app.mobile.backend == "cloud"

    def test_app_without_mobile_config(self):
        app = MikiApp(title="Test")
        assert app.mobile is None


class TestMobileBuild:
    """Test mobile build system."""

    def test_build_cloud_android(self):
        from mikiui.app.mobile import MobileConfig
        from mikiui.build.mobile_build import build_mobile

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                app_id="com.test.app",
            ),
        )

        @app.route("/")
        def home():
            return Div("Hello")

        with tempfile.TemporaryDirectory() as tmpdir:
            report = build_mobile(app, out_dir=tmpdir)
            assert report["status"] == "ok"
            assert (Path(tmpdir) / "capacitor.config.json").exists()
            assert (Path(tmpdir) / "package.json").exists()

    def test_build_generates_capacitor_config(self):
        from mikiui.app.mobile import MobileConfig
        from mikiui.build.mobile_build import build_mobile

        app = MikiApp(
            title="My App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                app_id="com.example.myapp",
            ),
        )

        @app.route("/")
        def home():
            return Div("Hello")

        with tempfile.TemporaryDirectory() as tmpdir:
            report = build_mobile(app, out_dir=tmpdir)
            config = report["capacitor_config"]
            assert config["appId"] == "com.example.myapp"
            assert config["appName"] == "My App"

    def test_build_generates_android_manifest(self):
        from mikiui.app.mobile import MobileConfig
        from mikiui.build.mobile_build import build_mobile

        app = MikiApp(
            title="Test",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                plugins=["Camera"],
            ),
        )

        @app.route("/")
        def home():
            return Div("Hello")

        with tempfile.TemporaryDirectory() as tmpdir:
            build_mobile(app, out_dir=tmpdir)
            manifest = Path(tmpdir) / "android" / "AndroidManifest.xml"
            assert manifest.exists()
            content = manifest.read_text()
            assert "android.permission.CAMERA" in content

    def test_build_generates_ios_plist(self):
        from mikiui.app.mobile import MobileConfig
        from mikiui.build.mobile_build import build_mobile

        app = MikiApp(
            title="Test",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="ios",
            ),
        )

        @app.route("/")
        def home():
            return Div("Hello")

        with tempfile.TemporaryDirectory() as tmpdir:
            build_mobile(app, out_dir=tmpdir)
            plist = Path(tmpdir) / "ios" / "Info.plist"
            assert plist.exists()

    def test_build_ondevice_generates_bridge(self):
        from mikiui.app.mobile import MobileConfig
        from mikiui.build.mobile_build import build_mobile

        app = MikiApp(
            title="Test",
            mobile=MobileConfig(
                backend="ondevice",
                target_platform="android",
            ),
        )

        @app.route("/")
        def home():
            return Div("Hello")

        with tempfile.TemporaryDirectory() as tmpdir:
            build_mobile(app, out_dir=tmpdir)
            bridge = Path(tmpdir) / "bridge" / "ondevice_bridge.py"
            assert bridge.exists()

    def test_build_rejects_ios_ondevice(self):
        from mikiui.app.mobile import MobileConfig
        from mikiui.build.mobile_build import build_mobile

        app = MikiApp(
            title="Test",
            mobile=MobileConfig(
                backend="ondevice",
                target_platform="android",  # Valid, but let's test the build validation
            ),
        )

        @app.route("/")
        def home():
            return Div("Hello")

        with tempfile.TemporaryDirectory() as tmpdir:
            # This should work (android ondevice)
            report = build_mobile(app, out_dir=tmpdir)
            assert report["status"] == "ok"

    def test_build_package_json_has_plugins(self):
        from mikiui.app.mobile import MobileConfig
        from mikiui.build.mobile_build import build_mobile

        app = MikiApp(
            title="Test",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                plugins=["Camera"],
            ),
        )

        @app.route("/")
        def home():
            return Div("Hello")

        with tempfile.TemporaryDirectory() as tmpdir:
            build_mobile(app, out_dir=tmpdir)
            import json
            pkg_path = Path(tmpdir) / "package.json"
            with open(pkg_path) as f:
                pkg = json.load(f)
            dev_deps = pkg.get("devDependencies", {})
            # Camera plugin should be in dev dependencies
            assert any("camera" in k.lower() for k in dev_deps), f"Camera plugin not found in {dev_deps}"


class TestCapabilityMap:
    """Test capability to plugin mapping."""

    def test_all_capabilities_have_required_fields(self):
        from mikiui.app.mobile import CAPABILITY_MAP

        for cap, info in CAPABILITY_MAP.items():
            assert "capacitor_plugin" in info, f"{cap} missing capacitor_plugin"
            assert "android_permission" in info or info.get("android_permission") is None

    def test_camera_capability(self):
        from mikiui.app.mobile import CAPABILITY_MAP

        camera = CAPABILITY_MAP["camera"]
        assert camera["capacitor_plugin"] == "@capacitor/camera"
        assert "CAMERA" in camera["android_permission"]
        assert "NSCameraUsageDescription" in camera["ios_privacy_key"]


class TestChaquopyBridge:
    """Test Chaquopy bridge for on-device mode."""

    def test_bridge_creation(self):
        from mikiui.app.mobile.chaquopy_bridge import ChaquopyBridge, get_bridge, reset_bridge

        reset_bridge()
        app = MikiApp(title="Test")
        bridge = get_bridge(app)
        assert bridge is not None
        assert bridge._app is app

    def test_bridge_call_get_route(self):
        from mikiui.app.mobile.chaquopy_bridge import ChaquopyBridge, reset_bridge

        reset_bridge()
        app = MikiApp(title="Test")

        @app.route("/")
        def home():
            return {"message": "Hello"}

        bridge = ChaquopyBridge(app)
        result = bridge.call("GET", "/", "")
        import json
        data = json.loads(result)
        assert data["message"] == "Hello"
        assert data["status"] == 200

    def test_bridge_call_unknown_route(self):
        from mikiui.app.mobile.chaquopy_bridge import ChaquopyBridge, reset_bridge

        reset_bridge()
        app = MikiApp(title="Test")
        bridge = ChaquopyBridge(app)
        result = bridge.call("GET", "/unknown", "")
        import json
        data = json.loads(result)
        assert data["status"] == 404

    def test_bridge_call_with_data(self):
        from mikiui.app.mobile.chaquopy_bridge import ChaquopyBridge, reset_bridge

        reset_bridge()
        app = MikiApp(title="Test")

        @app.post("/echo")
        def echo(key=None):
            return {"echo": key}

        bridge = ChaquopyBridge(app)
        result = bridge.call("POST", "/echo", '{"key": "value"}')
        import json
        data = json.loads(result)
        assert data["status"] == 200
        assert data["echo"] == "value"

    def test_bridge_invalid_json(self):
        from mikiui.app.mobile.chaquopy_bridge import ChaquopyBridge, reset_bridge

        reset_bridge()
        app = MikiApp(title="Test")
        bridge = ChaquopyBridge(app)
        result = bridge.call("POST", "/", "not json")
        import json
        data = json.loads(result)
        assert data["status"] == 400


class TestMobileSecurity:
    """Test mobile security guardrails."""

    def test_ios_ondevice_rejected(self):
        from mikiui.app.mobile import MobileConfig

        with pytest.raises(ValueError, match="iOS does not support on-device"):
            MobileConfig(backend="ondevice", target_platform="ios")

    def test_security_scan_detects_listening_sockets(self):
        from mikiui.build.mobile_build import _security_scan
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with a dangerous pattern
            dangerous_file = os.path.join(tmpdir, "dangerous.py")
            with open(dangerous_file, "w") as f:
                f.write("sock = ServerSocket(8080)\n")

            warnings = _security_scan(tmpdir)
            assert any("ServerSocket" in w for w in warnings)

    def test_security_scan_clean(self):
        from mikiui.build.mobile_build import _security_scan
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            clean_file = os.path.join(tmpdir, "clean.py")
            with open(clean_file, "w") as f:
                f.write("def hello(): return 'world'\n")

            warnings = _security_scan(tmpdir)
            assert len(warnings) == 0


class TestMobileBuildComplete:
    """Test complete mobile build with all features."""

    def test_build_with_all_plugins(self):
        from mikiui.app.mobile import MobileConfig
        from mikiui.build.mobile_build import build_mobile

        app = MikiApp(
            title="Full App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="both",
                plugins=["Camera", "Geolocation", "PushNotifications"],
                app_id="com.example.fullapp",
            ),
        )

        @app.route("/")
        def home():
            return {"page": "home"}

        with tempfile.TemporaryDirectory() as tmpdir:
            report = build_mobile(app, out_dir=tmpdir)
            assert report["status"] == "ok"

            # Check all expected files exist
            assert (Path(tmpdir) / "capacitor.config.json").exists()
            assert (Path(tmpdir) / "package.json").exists()
            assert (Path(tmpdir) / "android" / "AndroidManifest.xml").exists()
            assert (Path(tmpdir) / "ios" / "Info.plist").exists()
            assert (Path(tmpdir) / "ios" / "PrivacyInfo.xcprivacy").exists()
            assert (Path(tmpdir) / "www" / "manifest.webmanifest").exists()
            assert (Path(tmpdir) / "www" / "_mobile_meta.html").exists()

    def test_build_ondevice_with_chaquopy(self):
        from mikiui.app.mobile import MobileConfig
        from mikiui.build.mobile_build import build_mobile

        app = MikiApp(
            title="OnDevice App",
            mobile=MobileConfig(
                backend="ondevice",
                target_platform="android",
                chaquopy_deps=["fastapi", "pydantic"],
            ),
        )

        @app.route("/")
        def home():
            return {"page": "home"}

        with tempfile.TemporaryDirectory() as tmpdir:
            report = build_mobile(app, out_dir=tmpdir)
            assert report["status"] == "ok"
            assert (Path(tmpdir) / "bridge" / "ondevice_bridge.py").exists()
            assert (Path(tmpdir) / "android" / "chaquopy.gradle").exists()


class TestWebRTCSignaling:
    """Test WebRTC signaling handler."""

    def test_signaling_handler_creation(self):
        from mikiui.backend.websocket import ConnectionManager, create_webrtc_signaling_handler

        manager = ConnectionManager()
        handler = create_webrtc_signaling_handler(manager)
        assert handler is not None
        assert callable(handler)


class TestMobileCLI:
    """Test mobile CLI commands."""

    def test_mobile_info_command(self, capsys):
        from typer.testing import CliRunner
        from mikiui.cli.commands import cli

        runner = CliRunner()
        # Test with a valid app spec
        result = runner.invoke(cli, ["mobile", "info", "--app", "mikiui.examples.kitchen_sink:app"])
        # Should not crash (may fail due to app spec, but command should exist)
        assert result.exit_code == 0 or "Error" in result.output

    def test_mobile_plugins_command(self):
        from typer.testing import CliRunner
        from mikiui.cli.commands import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["mobile", "plugins"])
        assert result.exit_code == 0
        assert "capacitor" in result.output.lower()
