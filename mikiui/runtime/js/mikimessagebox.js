(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiMessageBox = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var closeBtns = el.querySelectorAll("[data-miki-messagebox-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          on(btn, "click", function (e) {
            e.preventDefault();
            mikiMessageBox.close(el);
          });
        })(closeBtns[i]);
      }

      // ESC to close
      on(el, "keydown", function (e) {
        if (e.key === "Escape") {
          mikiMessageBox.close(el);
        }
      });

      // Click on overlay background
      if (el.getAttribute("data-miki-close-on-overlay") !== "false") {
        on(el, "click", function (e) {
          if (e.target === el) {
            mikiMessageBox.close(el);
          }
        });
      }
    },

    close: function (el) {
      el.style.display = "none";
      el.setAttribute("data-miki-messagebox-open", "false");
      el.setAttribute("aria-hidden", "true");
      el.dataset.mikiFocusTrapped = "false";
      dispatch(el, "miki:messagebox:closed", {});
    },

    show: function (el) {
      el.style.display = "flex";
      el.setAttribute("data-miki-messagebox-open", "true");
      el.setAttribute("aria-hidden", "false");

      // Focus trap
      var focusable = el.querySelectorAll(
        'a[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length > 0) {
        focusable[0].focus();
      }
      miki.focusTrap(el);

      dispatch(el, "miki:messagebox:opened", {});
    }
  };

  window.mikiMessageBox = mikiMessageBox;
})();
