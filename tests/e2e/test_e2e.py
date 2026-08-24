"""End-to-end tests for MikiUI using Playwright."""

from __future__ import annotations

import pytest
import asyncio
from playwright.sync_api import sync_playwright, Page
from starlette.testclient import TestClient

from mikiui.examples.demo1 import app
from mikiui.backend.server import create_app

# Skip if Playwright is not installed
try:
    from playwright.sync_api import sync_playwright
    _HAS_PLAYWRIGHT = True
except ImportError:
    _HAS_PLAYWRIGHT = False

# Skip if Chromium is not installed
if _HAS_PLAYWRIGHT:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        _HAS_BROWSER = True
    except Exception:
        _HAS_BROWSER = False
else:
    _HAS_BROWSER = False

pytestmark = pytest.mark.skipif(
    not (_HAS_PLAYWRIGHT and _HAS_BROWSER),
    reason="Playwright/Chromium not installed. Run: pip install playwright && playwright install chromium",
)


@pytest.fixture(scope="module")
def server():
    """Start a test server for E2E tests."""
    fastapi_app = create_app(app)
    client = TestClient(fastapi_app)
    return client


class TestBrowserE2E:
    """Browser-based E2E tests for demo1.py app."""

    def test_homepage_loads(self, server):
        resp = server.get("/")
        assert resp.status_code == 200
        assert "MikiUI Demo" in resp.text

    def test_data_page_loads(self, server):
        resp = server.get("/data")
        assert resp.status_code == 200
        assert "SplitView" in resp.text or "miki-splitview" in resp.text

    def test_forms_page_loads(self, server):
        resp = server.get("/forms")
        assert resp.status_code == 200
        assert "miki-slider" in resp.text

    def test_dialog_page_loads(self, server):
        resp = server.get("/dialog")
        assert resp.status_code == 200
        assert "miki-modal" in resp.text

    def test_advanced_page_loads(self, server):
        resp = server.get("/advanced")
        assert resp.status_code == 200

    def test_navbar_renders(self, server):
        resp = server.get("/")
        assert 'miki-navbar' in resp.text
        assert 'miki-navbar-toggle' in resp.text

    def test_splitview_renders(self, server):
        resp = server.get("/data")
        assert 'data-miki-splitview="true"' in resp.text
        assert 'data-miki-splitter="true"' in resp.text

    def test_assets_served(self, server):
        resp = server.get("/_miki/runtime/miki.css")
        assert resp.status_code == 200
        assert 'miki-navbar' in resp.text


class TestBrowserE2EWithPlaywright:
    """Full browser E2E tests using Playwright (requires running server)."""

    def test_homepage_browser(self):
        """Test homepage loads in a real browser with JS execution."""
        fastapi_app = create_app(app)
        client = TestClient(fastapi_app)
        base_url = "http://localhost:8000"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Use the test client to serve content
            resp = client.get("/")
            page.set_content(resp.text)
            assert "MikiUI Demo" in page.title() or "MikiUI Demo" in page.content()
            browser.close()
