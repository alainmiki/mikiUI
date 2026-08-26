(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDrawer = {
    _resolve: function (el) {
      var resolved = resolveEl(el);
      if (!resolved) return null;
      var drawer = findClosest(resolved, ".miki-drawer");
      return drawer || resolved;
    },

    open: function (el) {
      var drawer = mikiDrawer._resolve(el);
      if (!drawer) return;

      drawer.classList.add("miki-drawer-open");
      drawer.setAttribute("aria-hidden", "false");
      drawer.setAttribute("tabindex", "-1");
      drawer.focus();

      /* ESC key to close when drawer is open */
      if (!drawer.dataset.mikiEscBound) {
        drawer.dataset.mikiEscBound = "true";
        on(document, "keydown", function onEsc(e) {
          if (e.key === "Escape" &&
              drawer.getAttribute("data-miki-drawer-esc-close") !== "false" &&
              drawer.classList.contains("miki-drawer-open")) {
            mikiDrawer.close(drawer);
            drawer.dataset.mikiEscBound = "false";
          }
        });
      }

      /* Focus first focusable element */
      var focusable = drawer.querySelectorAll(
        'a[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length > 0) focusable[0].focus();
      miki.focusTrap(drawer);
      drawer.dataset.mikiFocusTrapped = "true";

      dispatch(drawer, "miki:drawer:opened", {});
    },

    close: function (el) {
      var drawer = mikiDrawer._resolve(el);
      if (!drawer) return;

      drawer.classList.remove("miki-drawer-open");
      drawer.setAttribute("aria-hidden", "true");
      if (drawer.dataset.mikiFocusTrapped === "true") {
        drawer.dataset.mikiFocusTrapped = "false";
      }
      if (drawer.dataset.mikiEscBound === "true") {
        drawer.dataset.mikiEscBound = "false";
      }
      drawer.removeAttribute("tabindex");
      dispatch(drawer, "miki:drawer:closed", {});
    },

    toggle: function (el) {
      var drawer = mikiDrawer._resolve(el);
      if (!drawer) return;

      if (drawer.classList.contains("miki-drawer-open")) {
        mikiDrawer.close(drawer);
      } else {
        mikiDrawer.open(drawer);
      }
    },

    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      /* Overlay click/tap-to-close */
      var overlay = el.querySelector("[data-miki-drawer-overlay=\"true\"]");
      if (overlay) {
        onPointer(overlay, "activate", function () {
          mikiDrawer.close(el);
        });
      }

      /* Close buttons */
      var closeBtns = el.querySelectorAll("[data-miki-drawer-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          onPointer(btn, "activate", function (e) {
            e.preventDefault();
            mikiDrawer.close(el);
          });
        })(closeBtns[i]);
      }
    }
  };

  window.mikiDrawer = mikiDrawer;
})();
