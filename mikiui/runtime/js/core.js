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

  function resolveEl(el) {
    if (!el) return null;
    if (typeof el === "string") {
      return document.querySelector(el);
    }
    return el;
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

  /* ===================== Pointer normalization ===================== */

  var TOUCH_EVENTS = ["touchstart", "touchmove", "touchend", "touchcancel"];
  var MOUSE_EVENTS = ["mousedown", "mousemove", "mouseup", "mouseleave"];

  /* Detect the primary pointer type for the current session */
  var _pointerType = typeof window.PointerEvent !== "undefined"
    ? window.PointerEvent.prototype
    : null;
  function isTouchDevice() {
    return typeof window !== "undefined" &&
      (window.ontouchstart !== undefined ||
       (typeof navigator !== "undefined" &&
        navigator.maxTouchPoints > 0));
  }

  /* onPointer(el, type, handler)
     Binds the appropriate event(s) for the given interaction "type":
     - "activate" => click (mouse) + touchend (touch) — avoids 300ms delay
     - "down"     => mousedown + touchstart
     - "up"       => mouseup + touchend
     - "move"     => mousemove + touchmove
     - "leave"    => mouseleave + touchend (fallback)
     Returns a cleanup function. */
  function onPointer(el, type, handler, opts) {
    var map = {
      activate: { mouse: "click", touch: "touchend" },
      down:     { mouse: "mousedown", touch: "touchstart" },
      up:       { mouse: "mouseup",   touch: "touchend" },
      move:     { mouse: "mousemove", touch: "touchmove" },
      leave:    { mouse: "mouseleave", touch: "touchend" }
    };
    var events = map[type] || { mouse: type, touch: type };
    var used = [];

    function wrap(fn) {
      return function (e) {
        /* If it's a touch event but we only want non-touch, skip */
        if (e && e.pointerType === "touch" && opts && opts.mouseOnly) return;
        if (e && e.type && e.type.indexOf("touch") !== -1 && opts && opts.mouseOnly) return;
        fn.call(this, e);
      };
    }

    /* Always bind mouse (works on touch too via tap->click for "activate") */
    on(el, events.mouse, wrap(handler), opts);
    used.push({ type: events.mouse, handler: handler });

    /* For non-click events, also bind touch */
    if (events.touch !== events.mouse) {
      on(el, events.touch, wrap(handler), opts);
      used.push({ type: events.touch, handler: handler });
    }

    return function cleanup() {
      for (var i = 0; i < used.length; i++) {
        off(el, used[i].type, wrap(handler), opts);
      }
    };
  }

  /* preventTouchScroll(el) — call on elements that handle their own
     touchmove (e.g. slider thumbs, drag handles) to prevent page scroll */
  function preventTouchScroll(el, onScrollPrevented) {
    on(el, "touchmove", function (e) {
      if (e.cancelable !== false) {
        e.preventDefault();
      }
      if (onScrollPrevented) onScrollPrevented(e);
    }, { passive: false });
  }

  /* getEventPoint(e) — normalize touch/mouse coordinates */
  function eventPoint(e) {
    if (e.touches && e.touches.length > 0) {
      return { x: e.touches[0].clientX, y: e.touches[0].clientY };
    }
    if (e.changedTouches && e.changedTouches.length > 0) {
      return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY };
    }
    return { x: e.clientX || 0, y: e.clientY || 0 };
  }

  window.miki.on = on;
  window.miki.off = off;
  window.miki.findClosest = findClosest;
  window.miki.resolveEl = resolveEl;
  window.miki.generateId = generateId;
  window.miki.dispatch = dispatch;
  window.miki.focusTrap = focusTrap;
  window.miki.onPointer = onPointer;
  window.miki.isTouchDevice = isTouchDevice;
  window.miki.eventPoint = eventPoint;
  window.miki.preventTouchScroll = preventTouchScroll;

  /* Expose utilities as bare globals so widget modules (each in their own IIFE)
     can call on(), off(), dispatch(), findClosest(), generateId() without
     a miki. prefix.  These do NOT conflict with standard window properties
     (window.on / window.off / etc. are not part of the DOM spec). */
  window.on = on;
  window.off = off;
  window.findClosest = findClosest;
  window.resolveEl = resolveEl;
  window.dispatch = dispatch;
  window.findClosest = findClosest;
  window.generateId = generateId;
  window.onPointer = onPointer;
  window.isTouchDevice = isTouchDevice;
  window.eventPoint = eventPoint;
  window.preventTouchScroll = preventTouchScroll;
})();
