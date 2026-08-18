/*!
 * MikiUI History Router v1.0
 * Lightweight client-side router for SPA mode.
 * Intercepts same-origin link clicks, pushes history state,
 * and reloads the page content via HTMX or fetch.
 *
 * Usage:
 *   <a href="/about" data-miki-nav>About</a>
 *   <nav data-miki-nav>
 *
 * Events:
 *   "miki:navigate" — dispatched on the document with {path, method, preventDefault}
 *   "miki:loaded"  — dispatched after the new content is swapped in
 */
(function () {
  "use strict";

  if (typeof window === "undefined") return;

  var HISTORY_SUPPORTED = !!(window.history && window.history.pushState);

  function _isSameOrigin(href) {
    try {
      var origin = window.location.origin;
      var url = new URL(href, origin);
      return url.origin === origin;
    } catch (e) {
      return false;
    }
  }

  function _interceptClick(e) {
    var link = e.target.closest("a[href]");
    if (!link) return;
    if (e.target.closest("[data-miki-nav-ignore]")) return;
    var href = link.getAttribute("href");
    if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:")) return;
    if (!_isSameOrigin(href)) return;
    if (link.hasAttribute("download")) return;
    if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;

    e.preventDefault();
    var path = href.replace(window.location.origin, "") || "/";
    _navigate(path, "GET");
  }

  function _navigate(path, method) {
    if (!HISTORY_SUPPORTED) {
      window.location.href = path;
      return;
    }
    var evt = new CustomEvent("miki:navigate", {
      detail: { path: path, method: method, preventDefault: _preventDefault },
      cancelable: true,
      bubbles: true,
    });
    window.dispatchEvent(evt);
    if (evt.defaultPrevented) return;

    window.history.pushState({ path: path }, "", path);
    _load(path, method);
  }

  function _preventDefault() {
    // placeholder so callers can cancel via event.detail.preventDefault()
  }

  function _load(path, method) {
    if (method !== "GET") return;
    var main = document.getElementById("miki-app") || document.body;
    if (typeof htmx !== "undefined" && htmx.ajax) {
      htmx.ajax("GET", path, { target: main, swap: "innerHTML" }).then(function () {
        document.dispatchEvent(new CustomEvent("miki:loaded", { detail: { path: path } }));
      }).catch(function () {
        window.location.href = path;
      });
    } else {
      fetch(path, { method: "GET", headers: { "X-Requested-With": "MikiUI" } })
        .then(function (res) { return res.text(); })
        .then(function (html) {
          main.innerHTML = html;
          document.dispatchEvent(new CustomEvent("miki:loaded", { detail: { path: path } }));
        })
        .catch(function () {
          window.location.href = path;
        });
    }
  }

  function _init() {
    document.addEventListener("click", _interceptClick, false);
    window.addEventListener("popstate", function (e) {
      var path = window.location.pathname;
      _load(path, "GET");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", _init);
  } else {
    _init();
  }

  window.mikiRouter = {
    navigate: _navigate,
    load: _load,
    isSameOrigin: _isSameOrigin,
  };
})();
