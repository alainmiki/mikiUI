"""Tests for layout widgets: Hero, Footer, Navbar (widget), Sidebar, Drawer, Rail, ContextWindow."""

from __future__ import annotations

from mikiui import render
from mikiui.components import Navbar
from mikiui.widgets import Drawer, Footer, Hero, Rail, Sidebar, ContextWindow


def test_hero_renders_title():
    html = render(Hero("Welcome"))
    assert "miki-hero" in html
    assert "Welcome" in html
    assert 'role="banner"' in html


def test_hero_with_subtitle():
    html = render(Hero("Title", subtitle="Sub"))
    assert "Sub" in html
    assert "miki-hero-subtitle" in html


def test_hero_with_action():
    html = render(Hero("Title", action="Click me"))
    assert "miki-hero-action" in html


def test_hero_with_image():
    html = render(Hero("Title", image="/bg.jpg"))
    assert "background-image" in html
    assert "/bg.jpg" in html


def test_hero_variants():
    html = render(Hero("Title", variant="secondary"))
    assert "miki-hero-secondary" in html


def test_hero_align_center():
    html = render(Hero("Title", align="center"))
    assert "miki-hero-center" in html


def test_footer_renders_content():
    html = render(Footer("Some content", copyright="© 2024"))
    assert "miki-footer" in html
    assert "Some content" in html
    assert "© 2024" in html
    assert 'role="contentinfo"' in html


def test_footer_with_social_links():
    html = render(Footer(social=[("GitHub", "https://github.com")]))
    assert "miki-footer-social" in html
    assert "github.com" in html


def test_navbar_renders_brand_and_links():
    html = render(Navbar("MyBrand", links=[("Home", "/"), ("About", "/about")]))
    assert "miki-navbar" in html
    assert "MyBrand" in html
    assert 'href="/"' in html
    assert 'href="/about"' in html
    assert 'aria-label="Main navigation"' in html


def test_navbar_sticky():
    html = render(Navbar("Brand", sticky=True))
    assert "miki-navbar-sticky" in html


def test_navbar_dark():
    html = render(Navbar("Brand", dark=True))
    assert "miki-navbar-dark" in html


def test_navbar_toggle_button():
    html = render(Navbar("Brand", links=[("Home", "/")]))
    assert "miki-navbar-toggle" in html
    assert 'aria-label="Toggle navigation menu"' in html


def test_navbar_right_content():
    html = render(Navbar("Brand", links=[("Home", "/"), ("Login", "/login")], right="Profile"))
    assert "miki-navbar-right" in html
    assert "Profile" in html


def test_sidebar_renders_title():
    html = render(Sidebar(("Home", "/"), title="Menu"))
    assert "miki-sidebar" in html
    assert "Menu" in html
    assert 'role="complementary"' in html


def test_sidebar_width():
    html = render(Sidebar(title="Menu", width="300px"))
    assert "300px" in html


def test_sidebar_mobile():
    html = render(Sidebar(("Home", "/"), mobile=True))
    assert "miki-sidebar-mobile" in html


def test_drawer_renders_title():
    html = render(Drawer("Content", title="Settings"))
    assert "miki-drawer" in html
    assert 'role="dialog"' in html
    assert "Settings" in html
    assert "miki-drawer-close" in html


def test_drawer_sides():
    html = render(Drawer("Content", side="right"))
    assert "miki-drawer-right" in html


def test_drawer_no_close():
    html = render(Drawer("Content", title="T", closable=False))
    assert "miki-drawer-close" not in html


def test_rail_renders_items():
    html = render(Rail(
        ("Dashboard", "/dashboard", "home"),
        ("Settings", "/settings", "settings"),
    ))
    assert "miki-rail" in html
    assert 'href="/dashboard"' in html
    assert 'href="/settings"' in html
    assert 'aria-label="Navigation rail"' in html


def test_rail_side_right():
    html = render(Rail(("Home", "/", "home"), side="right"))
    assert "miki-rail-right" in html


def test_context_window_renders():
    html = render(ContextWindow(("Item 1", "/item1"), trigger="Menu"))
    assert "miki-context-window" in html
    assert "Menu" in html
    assert 'role="menu"' in html


def test_context_window_position():
    html = render(ContextWindow(("Item", "/"), position="top"))
    assert "miki-context-top" in html


def test_context_window_action_items():
    def delete_item():
        pass
    html = render(ContextWindow(("Delete", delete_item)))
    assert "onclick" in html
