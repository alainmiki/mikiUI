"""Unit tests for mikiui.engine.bridge."""

import pytest

from mikiui.engine.bridge import (
    BridgeEvent,
    bridge_attr,
    bridge_bind,
    bridge_handler,
    format_detail,
    generate_bridge_id,
)


class TestGenerateBridgeId:
    def test_default_prefix(self):
        id1 = generate_bridge_id()
        id2 = generate_bridge_id()
        assert id1.startswith("miki")
        assert id2.startswith("miki")
        assert id1 != id2

    def test_custom_prefix(self):
        id1 = generate_bridge_id("custom")
        id2 = generate_bridge_id("custom")
        assert id1.startswith("custom")
        assert id1 != id2

    def test_hex_suffix_length(self):
        id1 = generate_bridge_id()
        # "miki-" + 8 hex chars
        suffix = id1.replace("miki-", "")
        assert len(suffix) == 8
        assert all(c in "0123456789abcdef" for c in suffix)


class TestFormatDetail:
    def test_none(self):
        assert format_detail(None) == "{}"

    def test_empty_dict(self):
        assert format_detail({}) == "{}"

    def test_dict_with_strings(self):
        result = format_detail({"group": "abc", "index": 0})
        assert '"group"' in result
        assert '"abc"' in result
        assert "0" in result

    def test_dict_with_unicode(self):
        result = format_detail({"key": "café"})
        assert "café" in result

    def test_dict_with_bool(self):
        result = format_detail({"checked": True, "hidden": False})
        assert '"checked": true' in result
        assert '"hidden": false' in result


class TestBridgeHandler:
    def test_dotted_path_with_dict_detail(self):
        handler = bridge_handler("click", "mikiTabs.show", {"group": "grp", "index": 0})
        assert "mikiBridge.call" in handler
        assert '"mikiTabs"' in handler
        assert '"show"' in handler
        assert '"grp"' in handler
        assert "0" in handler
        assert "mikiBridge.callSafe" in handler
        assert "mikiBridge.dispatch" in handler

    def test_dotted_path_no_detail(self):
        handler = bridge_handler("click", "mikiDialog.close")
        assert "mikiBridge.call" in handler
        assert '"mikiDialog"' in handler
        assert '"close"' in handler
        assert "mikiBridge.callSafe" in handler

    def test_arbitrary_js_expression(self):
        handler = bridge_handler("click", "this.classList.toggle('open')")
        assert "mikiBridge.callSafe" in handler
        assert "this.classList.toggle('open')" in handler
        assert "mikiBridge.dispatch" in handler
        assert "mikiBridge.call(\"" not in handler

    def test_target_this(self):
        handler = bridge_handler("click", "mikiTabs.show", target="this")
        assert "mikiBridge.dispatch(this" in handler

    def test_target_selector(self):
        handler = bridge_handler("click", "mikiDialog.close", target="#mydialog")
        assert "mikiBridge.dispatch(\"#mydialog\"" in handler

    def test_event_name(self):
        handler = bridge_handler("select-tab", "mikiTabs.show", {"group": "g"})
        assert '"select-tab"' in handler


class TestBridgeAttr:
    def test_basic(self):
        attrs = bridge_attr("click", "mikiTabs.show", {"group": "grp", "index": 0})
        assert "data-miki-on" in attrs
        assert "click::" in attrs["data-miki-on"]
        assert "mikiBridge" in attrs["data-miki-on"]

    def test_extra_kwargs(self):
        attrs = bridge_attr("click", "mikiTabs.show", {"group": "grp"}, role="tab")
        assert "data-miki-on" in attrs
        assert "role" in attrs
        assert attrs["role"] == "tab"

    def test_extra_kwargs_underscore_to_hyphen(self):
        attrs = bridge_attr("click", "mikiTabs.show", {"group": "grp"}, aria_label="Close")
        assert attrs["aria-label"] == "Close"

    def test_multiple_bindings_via_separator(self):
        """bridge_attr generates a single binding per call; multiple bindings
        are separated by the caller using the same data-miki-on value."""
        attrs1 = bridge_attr("click", "mikiTabs.show", {"group": "g"})
        attrs2 = bridge_attr("keydown", "mikiTabs.show", {"group": "g"})
        assert attrs1["data-miki-on"].startswith("click::")
        assert attrs2["data-miki-on"].startswith("keydown::")


class TestBridgeBind:
    def test_merge_into_existing(self):
        existing = {"class_": "miki-btn", "type": "button"}
        result = bridge_bind(existing, "click", "mikiDialog.close")
        assert result["class_"] == "miki-btn"
        assert result["type"] == "button"
        assert "data-miki-on" in result

    def test_mutates_original(self):
        existing = {"class_": "miki-btn"}
        bridge_bind(existing, "click", "mikiDialog.close")
        assert "data-miki-on" in existing


class TestBridgeEvent:
    def test_to_attrs(self):
        ev = BridgeEvent("click", "mikiTabs.show", {"group": "g", "index": 0})
        attrs = ev.to_attrs()
        assert "data-miki-on" in attrs
        assert "click::" in attrs["data-miki-on"]

    def test_apply_to(self):
        attrs = {"class_": "btn"}
        ev = BridgeEvent("click", "mikiDialog.close")
        ev.apply_to(attrs)
        assert attrs["class_"] == "btn"
        assert "data-miki-on" in attrs

    def test_call_operator(self):
        attrs = {"class_": "btn"}
        ev = BridgeEvent("click", "mikiTabs.show", {"group": "g"}, role="tab")
        result = ev(attrs)
        assert result is attrs
        assert "data-miki-on" in attrs
        assert attrs["role"] == "tab"

    def test_repr(self):
        ev = BridgeEvent("click", "mikiTabs.show", {"group": "g"})
        r = repr(ev)
        assert "click" in r
        assert "mikiTabs.show" in r
        assert "group" in r
