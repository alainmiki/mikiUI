(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiMessageBox = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var escHandler = function (e) {
        if (e.key === "Escape") {
          mikiMessageBox.close(el);
        }
      };
      on(el, "keydown", escHandler);

      var closeBtnCleanups = [];
      var closeBtns = el.querySelectorAll("[data-miki-messagebox-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          var cleanup = onPointer(btn, "activate", function (e) {
            e.preventDefault();
            mikiMessageBox.close(el);
          });
          closeBtnCleanups.push(cleanup);
        })(closeBtns[i]);
      }

      var overlayCleanup = null;
      if (el.getAttribute("data-miki-close-on-overlay") !== "false") {
        overlayCleanup = onPointer(el, "activate", function (e) {
          if (e.target === el) {
            mikiMessageBox.close(el);
          }
        });
      }

      registerDestroyHandler(el, function () {
        off(el, "keydown", escHandler);
        if (overlayCleanup) overlayCleanup();
        for (var j = 0; j < closeBtnCleanups.length; j++) {
          closeBtnCleanups[j]();
        }
        if (el._mikiFocusTrapCleanup) {
          el._mikiFocusTrapCleanup();
          el._mikiFocusTrapCleanup = null;
        }
      });
    },

    close: function (el) {
      el.style.display = "none";
      el.setAttribute("data-miki-messagebox-open", "false");
      el.setAttribute("aria-hidden", "true");
      if (el._mikiFocusTrapCleanup) {
        el._mikiFocusTrapCleanup();
        el._mikiFocusTrapCleanup = null;
      }
      dispatch(el, "miki:messagebox:closed", {});
    },

    show: function (el) {
      el.style.display = "flex";
      el.setAttribute("data-miki-messagebox-open", "true");
      el.setAttribute("aria-hidden", "false");

      var focusable = el.querySelectorAll(
        'a[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length > 0) {
        focusable[0].focus();
      }
      el._mikiFocusTrapCleanup = miki.focusTrap(el);

      dispatch(el, "miki:messagebox:opened", {});
    },

    destroy: function (el) {
      mikiDestroy(el);
    }
  };

  window.mikiMessageBox = mikiMessageBox;
})();
