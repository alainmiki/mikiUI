"""Tests for the web build system."""

from __future__ import annotations

import os

from mikiui import Div, MikiApp
from mikiui.build.web_build import (
    _render_sitemap,
    _route_filename,
    _write_404_page,
    _write_robots_txt,
    build_web,
)


def make_app() -> MikiApp:
    app = MikiApp(title="Web Test")

    @app.route("/")
    def home():
        return Div("home")

    @app.route("/about")
    def about():
        return Div("about")

    return app


def test_route_filename():
    assert _route_filename("/") == "index.html"
    assert _route_filename("") == "index.html"
    assert _route_filename("/about") == "about.html"
    assert _route_filename("/blog/post") == "blog_post.html"


def test_render_sitemap_uses_route_paths(tmp_path):
    app = make_app()
    out = str(tmp_path)
    result = _render_sitemap(app, out, ["/", "/about"])
    assert result is not None
    with open(result, encoding="utf-8") as fh:
        xml = fh.read()
    assert "<url>" in xml
    assert "/about" in xml


def test_render_sitemap_returns_none_for_empty_pages(tmp_path):
    app = make_app()
    out = str(tmp_path)
    assert _render_sitemap(app, out, []) is None


def test_write_robots_txt(tmp_path):
    result = _write_robots_txt(str(tmp_path))
    assert result is not None
    with open(os.path.join(str(tmp_path), "robots.txt"), encoding="utf-8") as fh:
        content = fh.read()
    assert "User-agent: *" in content
    assert "Sitemap: /sitemap.xml" in content


def test_write_404_page(tmp_path):
    result = _write_404_page(str(tmp_path), title="Lost")
    assert result is not None
    with open(os.path.join(str(tmp_path), "404.html"), encoding="utf-8") as fh:
        content = fh.read()
    assert "<!doctype html>" in content.lower() or "<!DOCTYPE html>" in content
    assert "miki_ui.js" in content


def test_build_web_fullstack_includes_server_and_404(tmp_path):
    app = make_app()
    report = build_web(app, mode="fullstack", out_dir=str(tmp_path))
    assert report["status"] == "ok"
    assert report["server_script"] is not None
    assert report.get("404") is not None
    assert report.get("robots") is not None
    assert os.path.isfile(os.path.join(str(tmp_path), "server.py"))
    assert os.path.isfile(os.path.join(str(tmp_path), "404.html"))
    assert os.path.isfile(os.path.join(str(tmp_path), "robots.txt"))


def test_build_web_separate_excludes_server(tmp_path):
    app = make_app()
    report = build_web(app, mode="separate", out_dir=str(tmp_path))
    assert report["status"] == "ok"
    assert report["server_script"] is None
    assert report.get("404") is not None
    assert report.get("robots") is not None
    assert os.path.isfile(os.path.join(str(tmp_path), "404.html"))
    assert os.path.isfile(os.path.join(str(tmp_path), "robots.txt"))
    assert not os.path.isfile(os.path.join(str(tmp_path), "server.py"))
