"""Tests for advanced widgets: Card, Carousel, Pagination, Avatar, Badge, Progress, Icon."""

from __future__ import annotations

import pytest

from mikiui import render
from mikiui.widgets import Avatar, Badge, Card, Carousel, Icon, IconSet, Pagination, Progress

# --- Card -------------------------------------------------------------------

def test_card_renders_content_and_title():
    html = render(Card("Body content", title="My Card"))
    assert "miki-card" in html
    assert "My Card" in html
    assert "Body content" in html


def test_card_with_image():
    html = render(Card("Content", image="/pic.jpg"))
    assert "miki-card-image" in html
    assert "/pic.jpg" in html


def test_card_footer():
    html = render(Card("Body", footer="Action"))
    assert "miki-card-footer" in html
    assert "Action" in html


def test_card_variants():
    html = render(Card("Body", variant="outlined"))
    assert "miki-card-outlined" in html
    html = render(Card("Body", variant="filled"))
    assert "miki-card-filled" in html


# --- Carousel ---------------------------------------------------------------

def test_carousel_renders_slides():
    html = render(Carousel(("img1.jpg", "Image 1"), ("img2.jpg", "Image 2")))
    assert "miki-carousel" in html
    assert "miki-carousel-slide" in html
    assert 'aria-label="Image carousel"' in html


def test_carousel_autoplay():
    html = render(Carousel(("a.jpg", "A"), autoplay=True, interval=3000))
    assert 'data-autoplay="true"' in html
    assert 'data-interval="3000"' in html


def test_carousel_has_navigation():
    html = render(Carousel(("a.jpg", "A"), ("b.jpg", "B")))
    assert "miki-carousel-prev" in html
    assert "miki-carousel-next" in html
    assert "miki-carousel-dots" in html


# --- Pagination -------------------------------------------------------------

def test_pagination_renders_pages():
    html = render(Pagination(current=2, total=5, base_url="/page"))
    assert "miki-pagination" in html
    assert 'aria-label="Pagination"' in html


def test_pagination_single_page():
    html = render(Pagination(current=1, total=1))
    assert "miki-pagination" in html
    assert "miki-pagination-list" in html


def test_pagination_next_disabled():
    html = render(Pagination(current=5, total=5, base_url="/page"))
    assert "miki-pagination-item-disabled" in html


def test_pagination_prev_disabled():
    html = render(Pagination(current=1, total=5, base_url="/page"))
    assert "miki-pagination-item-disabled" in html


def test_pagination_current_marked():
    html = render(Pagination(current=3, total=5, base_url="/page"))
    assert 'aria-current="page"' in html


# --- Avatar -----------------------------------------------------------------

def test_avatar_renders_image():
    html = render(Avatar("https://example.com/avatar.png", alt="User Name"))
    assert "miki-avatar" in html
    assert "miki-avatar-md" in html
    assert "https://example.com/avatar.png" in html


def test_avatar_with_status():
    html = render(Avatar("/img.png", status="online"))
    assert "miki-avatar-status-online" in html


def test_avatar_size():
    html = render(Avatar("/img.png", size="lg"))
    assert "miki-avatar-lg" in html
    html = render(Avatar("/img.png", size="sm"))
    assert "miki-avatar-sm" in html


# --- Badge ------------------------------------------------------------------

def test_badge_renders_text():
    html = render(Badge("New", variant="primary"))
    assert "miki-badge" in html
    assert "miki-badge-primary" in html
    assert "New" in html
    assert 'role="status"' in html


def test_badge_size():
    html = render(Badge("Label", size="sm"))
    assert "miki-badge-sm" in html


def test_badge_variants():
    for v in ("default", "secondary", "success", "warning", "error", "ghost"):
        html = render(Badge("X", variant=v))
        assert f"miki-badge-{v}" in html


# --- Progress ----------------------------------------------------------------

def test_progress_renders_value():
    html = render(Progress(75, label="Loading", variant="success"))
    assert "miki-progress" in html
    assert "miki-progress-success" in html
    assert "Loading" in html
    assert "aria-valuenow" in html


def test_progress_clamps_value():
    html = render(Progress(150, label="Done"))
    assert "100%" in html


def test_progress_low_value():
    html = render(Progress(10, label="Low"))
    assert "10%" in html


# --- Icon -------------------------------------------------------------------

def test_icon_renders_svg():
    html = render(Icon("home", size=24))
    assert "<svg" in html
    assert 'width="24"' in html
    assert 'height="24"' in html
    assert "miki-icon" in html


def test_icon_variant():
    html = render(Icon("star", variant="solid"))
    assert 'fill="currentColor"' in html


def test_icon_outline_is_default():
    html = render(Icon("star"))
    assert 'fill="none"' in html


def test_icon_with_class():
    html = render(Icon("home", class_="text-blue-400"))
    assert "text-blue-400" in html


def test_icon_unknown_raises():
    with pytest.raises(ValueError, match="Unknown icon"):
        Icon("unknown-icon")


def test_icon_set_has_icon():
    assert IconSet.has_icon("home") is True
    assert IconSet.has_icon("nonexistent") is False


def test_icon_set_names():
    names = IconSet.icon_names()
    assert "home" in names
    assert "star" in names
    assert "settings" in names
