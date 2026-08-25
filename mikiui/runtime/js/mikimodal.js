(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiModal = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var isOpen = el.getAttribute("data-miki-modal-open") === "true";
      if (!isOpen) {
        el.style.display = "none";
      }

      // Close buttons — works on both mouse click and touch tap
      var closeBtns = el.querySelectorAll("[data-miki-modal-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          onPointer(btn, "activate", function (e) {
            e.preventDefault();
            mikiModal.close(el);
          });
        })(closeBtns[i]);
      }

      // Click/Tap on overlay (outside panel) closes
      if (el.getAttribute("data-miki-close-on-overlay") !== "false") {
        onPointer(el, "activate", function (e) {
          if (e.target === el) {
            mikiModal.close(el);
          }
        });
      }

      // ESC key
      on(el, "keydown", function (e) {
        if (e.key === "Escape" && el.getAttribute("data-miki-close-on-escape") !== "false") {
          mikiModal.close(el);
        }
      });
    },

    show: function (el) {
      el.style.display = "flex";
      el.setAttribute("data-miki-modal-open", "true");
      el.setAttribute("aria-hidden", "false");

      // Focus trap (skip if already trapped)
      if (el.dataset.mikiFocusTrapped !== "true") {
        miki.focusTrap(el);
      }

      var focusable = el.querySelectorAll(
        'a[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length > 0) {
        focusable[0].focus();
      }

      el.dispatchEvent(new CustomEvent("miki:modal:opened"));
    },

    close: function (el) {
      el.style.display = "none";
      el.setAttribute("data-miki-modal-open", "false");
      el.setAttribute("aria-hidden", "true");
      el.dataset.mikiFocusTrapped = "false";
      // Restore focus to the element that opened the modal
      if (el.dataset.mikiFocusTrapReturn) {
        var ret = document.getElementById(el.dataset.mikiFocusTrapReturn);
        if (ret) ret.focus();
        delete el.dataset.mikiFocusTrapReturn;
      }
      el.dispatchEvent(new CustomEvent("miki:modal:closed"));
    },

    toggle: function (el) {
      if (el.getAttribute("data-miki-modal-open") === "true") {
        mikiModal.close(el);
      } else {
        mikiModal.show(el);
      }
    }
  };

  window.mikiModal = mikiModal;
})();
