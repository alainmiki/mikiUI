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

      var escHandler = function (e) {
        if (e.key === "Escape" && el.getAttribute("data-miki-close-on-escape") !== "false") {
          mikiModal.close(el);
        }
      };
      on(el, "keydown", escHandler);

      var closeBtnCleanups = [];
      var closeBtns = el.querySelectorAll("[data-miki-modal-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          var cleanup = onPointer(btn, "activate", function (e) {
            e.preventDefault();
            mikiModal.close(el);
          });
          closeBtnCleanups.push(cleanup);
        })(closeBtns[i]);
      }

      var overlayCleanup = null;
      if (el.getAttribute("data-miki-close-on-overlay") !== "false") {
        overlayCleanup = onPointer(el, "activate", function (e) {
          if (e.target === el) {
            mikiModal.close(el);
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

     show: function (el) {
       el = resolveEl(el);
       if (!el) return;

       el.style.display = "flex";
       el.setAttribute("data-miki-modal-open", "true");
       el.setAttribute("aria-hidden", "false");

       if (el.dataset.mikiFocusTrapped !== "true") {
         el._mikiFocusTrapCleanup = miki.focusTrap(el);
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
       el = resolveEl(el);
       if (!el) return;

      el.style.display = "none";
      el.setAttribute("data-miki-modal-open", "false");
      el.setAttribute("aria-hidden", "true");
      if (el._mikiFocusTrapCleanup) {
        el._mikiFocusTrapCleanup();
        el._mikiFocusTrapCleanup = null;
      }
      if (el.dataset.mikiFocusTrapReturn) {
         var ret = document.getElementById(el.dataset.mikiFocusTrapReturn);
         if (ret) ret.focus();
         delete el.dataset.mikiFocusTrapReturn;
       }
       el.dispatchEvent(new CustomEvent("miki:modal:closed"));
     },

     toggle: function (el) {
       el = resolveEl(el);
       if (!el) return;
       if (el.getAttribute("data-miki-modal-open") === "true") {
         mikiModal.close(el);
       } else {
         mikiModal.show(el);
       }
     },

     destroy: function (el) {
       mikiDestroy(el);
     }
  };

  window.mikiModal = mikiModal;
})();
