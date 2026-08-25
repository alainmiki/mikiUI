(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDrawer = {
    open: function (el) {
      var drawer = findClosest(el, ".miki-drawer");
      if (drawer) {
        drawer.classList.add("miki-drawer-open");
        drawer.setAttribute("aria-hidden", "false");
        dispatch(drawer, "miki:drawer:opened", {});
      }
    },

    close: function (el) {
      var drawer = findClosest(el, ".miki-drawer");
      if (drawer) {
        drawer.classList.remove("miki-drawer-open");
        drawer.setAttribute("aria-hidden", "true");
        dispatch(drawer, "miki:drawer:closed", {});
      }
    },

    toggle: function (el) {
      var drawer = findClosest(el, ".miki-drawer");
      if (!drawer) {
        // Try target selector
        var target = el.getAttribute("data-miki-drawer-target");
        if (target) {
          drawer = document.querySelector(target);
        }
        if (!drawer) {
          drawer = document.querySelector(".miki-drawer");
        }
      }
      if (drawer) {
        drawer.classList.toggle("miki-drawer-open");
        var isOpen = drawer.classList.contains("miki-drawer-open");
        drawer.setAttribute("aria-hidden", !isOpen);
        dispatch(drawer, "miki:drawer:toggled", { open: isOpen });
      }
    },

    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      // ESC to close drawer
      on(el, "keydown", function (e) {
        if (e.key === "Escape" && el.getAttribute("data-miki-drawer-esc-close") !== "false") {
          mikiDrawer.close(el);
        }
      });

      // Overlay click/tap-to-close
      var overlay = el.querySelector("[data-miki-drawer-overlay=\"true\"]");
      if (overlay) {
        onPointer(overlay, "activate", function () {
          mikiDrawer.close(el);
        });
      }

      // Close buttons
      var closeBtns = el.querySelectorAll("[data-miki-drawer-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          onPointer(btn, "activate", function (e) {
            e.preventDefault();
            mikiDrawer.close(el);
          });
        })(closeBtns[i]);
      }
    },

    open: function (el) {
      var drawer = findClosest(el, ".miki-drawer");
      if (drawer) {
        drawer.classList.add("miki-drawer-open");
        drawer.setAttribute("aria-hidden", "false");
        var focusable = drawer.querySelectorAll(
          'a[href], input:not([disabled]):not([type="hidden"]), ' +
          'select:not([disabled]), textarea:not([disabled]), ' +
          'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        if (focusable.length > 0) focusable[0].focus();
        miki.focusTrap(drawer);
        dispatch(drawer, "miki:drawer:opened", {});
      }
    },

    close: function (el) {
      var drawer = findClosest(el, ".miki-drawer");
      if (drawer) {
        drawer.classList.remove("miki-drawer-open");
        drawer.setAttribute("aria-hidden", "true");
        drawer.dataset.mikiFocusTrapped = "false";
        dispatch(drawer, "miki:drawer:closed", {});
      }
    }
  };

  window.mikiDrawer = mikiDrawer;
})();
