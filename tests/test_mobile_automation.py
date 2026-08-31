"""Tests for mobile automation features."""
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mikiui import MikiApp, Div
from mikiui.app.mobile import MobileConfig


class TestMobileAutomation:
    """Test MobileAutomation class."""

    def test_automation_init_with_config(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(title="Test", mobile=MobileConfig(backend="cloud"))
        automation = MobileAutomation(app, "/tmp/test")

        assert automation.config is not None
        assert automation.config.backend == "cloud"
        assert automation.out_dir == "/tmp/test"

    def test_automation_init_without_config(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(title="Test")
        automation = MobileAutomation(app, "/tmp/test")

        assert automation.config is not None
        assert automation.config.backend == "cloud"  # default

    def test_android_dir_property(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(title="Test")
        automation = MobileAutomation(app, "/tmp/test")

        assert automation.android_dir == os.path.join("/tmp/test", "android")

    def test_ios_dir_property(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(title="Test")
        automation = MobileAutomation(app, "/tmp/test")

        assert automation.ios_dir == os.path.join("/tmp/test", "ios")

    def test_www_dir_property(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(title="Test")
        automation = MobileAutomation(app, "/tmp/test")

        assert automation.www_dir == os.path.join("/tmp/test", "www")


class TestNativeProjectGeneration:
    """Test native project file generation."""

    def test_generate_android_native(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                app_id="com.test.app",
                app_name="Test App",
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(app, tmpdir)
            result = automation._generate_android_native()

            assert result["status"] == "ok"
            assert result["platform"] == "android"
            assert len(result["files"]) > 0

            # Check MainActivity.kt exists
            main_activity = Path(tmpdir) / "android" / "app" / "src" / "main" / "java" / "com" / "test" / "app" / "MainActivity.kt"
            assert main_activity.exists()

            # Check build.gradle exists
            build_gradle = Path(tmpdir) / "android" / "app" / "build.gradle"
            assert build_gradle.exists()

            # Check strings.xml exists
            strings = Path(tmpdir) / "android" / "app" / "src" / "main" / "res" / "values" / "strings.xml"
            assert strings.exists()

    def test_generate_ios_native(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="ios",
                app_id="com.test.app",
                app_name="Test App",
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(app, tmpdir)
            result = automation._generate_ios_native()

            assert result["status"] == "ok"
            assert result["platform"] == "ios"
            assert len(result["files"]) > 0

            # Check AppDelegate.swift exists
            app_delegate = Path(tmpdir) / "ios" / "App" / "App" / "AppDelegate.swift"
            assert app_delegate.exists()

            # Check Podfile exists
            podfile = Path(tmpdir) / "ios" / "Podfile"
            assert podfile.exists()

    def test_generate_native_projects_both_platforms(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="both",
                app_id="com.test.app",
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(app, tmpdir)
            results = automation.generate_native_projects()

            assert results["android"] is not None
            assert results["ios"] is not None
            assert results["android"]["status"] == "ok"
            assert results["ios"]["status"] == "ok"

    def test_main_activity_kt_content(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                app_id="com.test.myapp",
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(app, tmpdir)
            content = automation._generate_main_activity_kt()

            assert "package com.test.myapp" in content
            assert "class MainActivity" in content
            assert "BridgeActivity" in content
            # When no plugins, should have comment about no plugins
            assert "No additional plugins" in content or "registerPlugins" in content

    def test_main_activity_kt_with_plugins(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                app_id="com.test.myapp",
                plugins=["Camera", "Geolocation"],
            ),
        )

        automation = MobileAutomation(app, "/tmp/test")
        content = automation._generate_main_activity_kt()

        assert "CameraPlugin" in content
        assert "GeolocationPlugin" in content

    def test_android_build_gradle_content(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                app_id="com.test.myapp",
                min_sdk=23,
                target_sdk=34,
            ),
        )

        automation = MobileAutomation(app, "/tmp/test")
        content = automation._generate_android_build_gradle()

        assert "com.test.myapp" in content
        assert "compileSdk 34" in content
        assert "minSdk 23" in content
        assert "targetSdk 34" in content

    def test_android_strings_xml_content(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="My Awesome App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                app_id="com.test.myapp",
                app_name="My Awesome App",
            ),
        )

        automation = MobileAutomation(app, "/tmp/test")
        content = automation._generate_android_strings()

        assert "My Awesome App" in content
        assert "com.test.myapp" in content

    def test_ios_info_plist_content(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="My iOS App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="ios",
                app_id="com.test.myapp",
                app_name="My iOS App",
                plugins=["Camera"],
            ),
        )

        automation = MobileAutomation(app, "/tmp/test")
        content = automation._generate_ios_info_plist()

        assert "com.test.myapp" in content
        assert "My iOS App" in content
        assert "NSCameraUsageDescription" in content

    def test_ios_podfile_content(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="ios",
                app_id="com.test.myapp",
                plugins=["Camera", "Geolocation"],
            ),
        )

        automation = MobileAutomation(app, "/tmp/test")
        content = automation._generate_podfile()

        assert "Capacitor" in content
        assert "CapacitorCamera" in content
        assert "CapacitorGeolocation" in content

    def test_ondevice_generates_chaquopy_bridge(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="ondevice",
                target_platform="android",
                app_id="com.test.myapp",
                chaquopy_deps=["fastapi", "pydantic"],
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(app, tmpdir)
            result = automation._generate_android_native()

            assert result["status"] == "ok"

            # Check ChaquopyBridge.kt exists
            bridge_kt = Path(tmpdir) / "android" / "app" / "src" / "main" / "java" / "com" / "test" / "myapp" / "OnDeviceBridge.kt"
            assert bridge_kt.exists()

            content = bridge_kt.read_text()
            assert "OnDeviceBridge" in content
            assert "@JavascriptInterface" in content


class TestPluginInstallation:
    """Test automated plugin installation."""

    def test_install_plugins_dry_run(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                plugins=["Camera"],
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(app, tmpdir)

            # Create a minimal package.json to simulate existing project
            pkg_path = Path(tmpdir) / "package.json"
            pkg_path.write_text('{"name": "test"}')

            # Mock subprocess.run to avoid actual npm calls
            with patch("mikiui.build.mobile_automation.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="Success",
                    stderr="",
                )

                result = automation.install_plugins()

                assert result["npm_install"]["status"] == "ok"
                assert result["cap_sync"]["status"] == "ok"
                assert len(result["plugin_installs"]) > 0

    def test_install_plugins_missing_directory(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(title="Test")
        automation = MobileAutomation(app, "/nonexistent/path")

        result = automation.install_plugins()

        assert result["status"] == "error"
        assert "not found" in result["message"]


class TestDeviceTesting:
    """Test device testing automation."""

    def test_list_android_devices(self):
        from mikiui.build.mobile_automation import MobileAutomation

        automation = MobileAutomation(None, "")

        with patch("mikiui.build.mobile_automation.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="emulator-5554\ndevice1\n",
                stderr="",
            )

            result = automation._list_android_devices()

            assert result["status"] == "ok"
            assert result["platform"] == "android"

    def test_list_ios_devices(self):
        from mikiui.build.mobile_automation import MobileAutomation

        automation = MobileAutomation(None, "")

        with patch("mikiui.build.mobile_automation.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="iPhone 15 Pro (ABC123)\n",
                stderr="",
            )

            result = automation._list_ios_devices()

            assert result["status"] == "ok"
            assert result["platform"] == "ios"

    def test_run_on_android_missing_directory(self):
        from mikiui.build.mobile_automation import MobileAutomation
        import mikiui.build.mobile_automation as mod

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(None, tmpdir)

            with patch.object(mod.subprocess, "run") as mock_run:
                mock_run.side_effect = FileNotFoundError("npx not found")

                result = automation._run_on_android("emulator", None)

                assert result["status"] == "error"

    def test_run_on_ios_missing_directory(self):
        from mikiui.build.mobile_automation import MobileAutomation
        import mikiui.build.mobile_automation as mod

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(None, tmpdir)

            with patch.object(mod.subprocess, "run") as mock_run:
                mock_run.side_effect = FileNotFoundError("npx not found")

                result = automation._run_on_ios("simulator", None)

                assert result["status"] == "error"


class TestCodeSigning:
    """Test code signing automation."""

    def test_setup_android_signing_new_keystore(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                app_id="com.test.myapp",
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(app, tmpdir)

            # Create android/app directory
            android_app_dir = Path(tmpdir) / "android" / "app"
            android_app_dir.mkdir(parents=True)

            # Create a minimal build.gradle
            build_gradle = android_app_dir / "build.gradle"
            build_gradle.write_text("""
                android {
                    buildTypes {
                        release {
                            minifyEnabled false
                        }
                    }
                }
            """)

            with patch("mikiui.build.mobile_automation.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="",
                    stderr="",
                )

                result = automation._setup_android_signing(
                    None, "password", "release", "password"
                )

                assert result["status"] == "ok"
                assert "keystore_path" in result

    def test_setup_ios_signing(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="ios",
                app_id="com.test.myapp",
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(app, tmpdir)

            result = automation._setup_ios_signing("TEAM123", None)

            assert result["status"] == "ok"
            assert "export_options_path" in result

            # Check ExportOptions.plist was created
            export_options = Path(tmpdir) / "ios" / "ExportOptions.plist"
            assert export_options.exists()


class TestStoreSubmission:
    """Test store submission automation."""

    def test_prepare_android_submission(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                app_id="com.test.myapp",
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(app, tmpdir)

            with patch("mikiui.build.mobile_automation.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="BUILD SUCCESSFUL",
                    stderr="",
                )

                result = automation._prepare_android_submission()

                assert result["status"] == "ok"
                assert "next_steps" in result

    def test_prepare_ios_submission(self):
        from mikiui.build.mobile_automation import MobileAutomation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="ios",
                app_id="com.test.myapp",
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            automation = MobileAutomation(app, tmpdir)

            with patch("mikiui.build.mobile_automation.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="BUILD SUCCEEDED",
                    stderr="",
                )

                result = automation._prepare_ios_submission()

                assert result["status"] == "ok"
                assert "next_steps" in result


class TestFullAutomation:
    """Test full automation pipeline."""

    def test_run_full_automation(self):
        from mikiui.build.mobile_automation import run_full_automation

        app = MikiApp(
            title="Test App",
            mobile=MobileConfig(
                backend="cloud",
                target_platform="android",
                app_id="com.test.myapp",
            ),
        )

        @app.route("/")
        def home():
            return Div("Hello")

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("mikiui.build.mobile_automation.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="Success",
                    stderr="",
                )

                result = run_full_automation(app, tmpdir, "android", "emulator")

                assert result["build"]["status"] == "ok"
                assert result["native_files"]["android"]["status"] == "ok"
                assert result["plugins"]["npm_install"]["status"] == "ok"


class TestCLICommands:
    """Test new CLI commands."""

    def test_mobile_sync_command(self):
        from typer.testing import CliRunner
        from mikiui.cli.commands import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["mobile", "sync", "--help"])
        assert result.exit_code == 0

    def test_mobile_devices_command(self):
        from typer.testing import CliRunner
        from mikiui.cli.commands import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["mobile", "devices", "--help"])
        assert result.exit_code == 0

    def test_mobile_sign_command(self):
        from typer.testing import CliRunner
        from mikiui.cli.commands import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["mobile", "sign", "--help"])
        assert result.exit_code == 0

    def test_mobile_test_command(self):
        from typer.testing import CliRunner
        from mikiui.cli.commands import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["mobile", "test", "--help"])
        assert result.exit_code == 0

    def test_mobile_submit_command(self):
        from typer.testing import CliRunner
        from mikiui.cli.commands import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["mobile", "submit", "--help"])
        assert result.exit_code == 0

    def test_mobile_all_command(self):
        from typer.testing import CliRunner
        from mikiui.cli.commands import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["mobile", "all", "--help"])
        assert result.exit_code == 0
