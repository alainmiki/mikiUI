(function () {
  "use strict";

  window.miki = window.miki || {};

  "use strict";

  /* ===================== Utility helpers ===================== */

  function on(el, event, handler, opts) {
    el.addEventListener(event, handler, opts || false);
  }

  function off(el, event, handler, opts) {
    el.removeEventListener(event, handler, opts || false);
  }

  function findClosest(el, selector) {
    return el ? el.closest(selector) : null;
  }

  function generateId(prefix) {
    return prefix + "-" + Math.random().toString(36).slice(2, 10);
  }

  function dispatch(el, name, detail) {
    el.dispatchEvent(
      new CustomEvent(name, { detail: detail || {}, bubbles: true, cancelable: true })
    );
  }

  /* ===================== Dialog / Modal ===================== */

  /* ---- Focus trap helper ---- */

  function focusTrap(container, opts) {
    opts = opts || {};

    function getFocusable(el) {
      return el.querySelectorAll(
        'a[href], area[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), iframe, object, embed, ' +
        '[tabindex]:not([tabindex="-1"]), [contenteditable]'
      );
    }

    // Save the currently focused element so we can restore focus on close
    var active = document.activeElement;
    if (active && active !== document.body) {
      if (!active.id) active.id = generateId("miki-tabexit");
      container.dataset.mikiFocusTrapReturn = active.id;
    }

    function trap(e) {
      // Don't trap if the container is no longer open/visible
      var isOpen = container.hasAttribute("open") ||
        container.getAttribute("data-miki-modal-open") === "true" ||
        container.getAttribute("data-miki-dialog") === "true";
      var isDisplayed = container.style.display !== "none" && container.style.display !== "";
      if (!isOpen && !isDisplayed) return;

      var focusable = getFocusable(container);
      if (!focusable.length) return;

      var first = focusable[0];
      var last = focusable[focusable.length - 1];

      // Check if focus is still inside the container
      var inside = container.contains(document.activeElement);
      if (!inside) {
        // Focus left the container — bring it back to first
        e.preventDefault();
        first.focus();
        return;
      }

      if (e.key === "Tab") {
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault();
            last.focus();
          }
        } else {
          if (document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      }
    }

    container.dataset.mikiFocusTrapped = "true";
    on(document, "keydown", trap);
  }

  window.miki.on = on;
  window.miki.off = off;
  window.miki.findClosest = findClosest;
  window.miki.generateId = generateId;
  window.miki.dispatch = dispatch;
  window.miki.focusTrap = focusTrap;
})();
