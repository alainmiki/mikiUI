"""End-to-end tests for MikiUI using Playwright."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skipif(
    True,  # Set to False when Playwright is installed
    reason="Playwright not installed. Run: pip install playwright && playwright install",
)


class TestBrowserE2E:
    """Browser-based E2E tests."""

    def test_homepage_loads(self, page):
        page.goto("http://localhost:8000/")
        assert page.title() == "MikiUI App"
        assert page.content().count("Hello") > 0

    def test_navigation_works(self, page):
        page.goto("http://localhost:8000/")
        page.click("text=Data")
        page.wait_for_url("**/data")
        assert "Data" in page.content()

    def test_form_submission(self, page):
        page.goto("http://localhost:8000/forms")
        page.fill("input[name='name']", "Test User")
        page.click("button[type='submit']")
        page.wait_for_selector("text=Submitted")
        assert "Submitted" in page.content()


class TestDesktopE2E:
    """Desktop window E2E tests (requires pywebview)."""

    def test_desktop_window_opens(self):
        pytest.skip("Desktop E2E requires pywebview and is tested separately")


class TestReloadE2E:
    """Hot-reload E2E tests."""

    def test_reload_detects_changes(self, page):
        pytest.skip("Reload E2E requires watchfiles and file system setup")
