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

      if (!drawer.dataset.mikiEscBound) {
        drawer.dataset.mikiEscBound = "true";
        var escHandler = function onEsc(e) {
          if (e.key === "Escape" &&
              drawer.getAttribute("data-miki-drawer-esc-close") !== "false" &&
              drawer.classList.contains("miki-drawer-open")) {
            mikiDrawer.close(drawer);
            drawer.dataset.mikiEscBound = "false";
          }
        };
        on(document, "keydown", escHandler);
        drawer._mikiEscHandler = escHandler;
      }

      var focusable = drawer.querySelectorAll(
        'a[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length > 0) focusable[0].focus();
      if (drawer.dataset.mikiFocusTrapped !== "true") {
        drawer._mikiFocusTrapCleanup = miki.focusTrap(drawer);
        drawer.dataset.mikiFocusTrapped = "true";
      }

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

      var overlayCleanup = null;
      var overlay = el.querySelector("[data-miki-drawer-overlay=\"true\"]");
      if (overlay) {
        overlayCleanup = onPointer(overlay, "activate", function () {
          mikiDrawer.close(el);
        });
      }

      var closeBtnCleanups = [];
      var closeBtns = el.querySelectorAll("[data-miki-drawer-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          var cleanup = onPointer(btn, "activate", function (e) {
            e.preventDefault();
            mikiDrawer.close(el);
          });
          closeBtnCleanups.push(cleanup);
        })(closeBtns[i]);
      }

      registerDestroyHandler(el, function () {
        if (overlayCleanup) overlayCleanup();
        for (var j = 0; j < closeBtnCleanups.length; j++) {
          closeBtnCleanups[j]();
        }
        if (el._mikiEscHandler) {
          off(document, "keydown", el._mikiEscHandler);
          el._mikiEscHandler = null;
        }
        if (el._mikiFocusTrapCleanup) {
          el._mikiFocusTrapCleanup();
          el._mikiFocusTrapCleanup = null;
        }
      });
    },

    destroy: function (el) {
      mikiDestroy(el);
    }
  };

  window.mikiDrawer = mikiDrawer;
})();
