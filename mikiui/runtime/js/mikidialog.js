(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDialog = {
    init: function (dlg) {
      if (dlg.dataset.mikiInit === "true") return;
      dlg.dataset.mikiInit = "true";

      var escHandler = function (e) {
        if (e.key === "Escape" && dlg.open) {
          var closeOnEsc = dlg.getAttribute("data-miki-dialog-close-on-escape");
          if (closeOnEsc === null || closeOnEsc === "true") {
            mikiDialog.close(dlg);
          }
        }
      };
      on(dlg, "keydown", escHandler);

      var overlayCleanup = null;
      if (dlg.getAttribute("data-miki-dialog-close-on-overlay") === "true") {
        overlayCleanup = onPointer(dlg, "activate", function (e) {
          var target = e && e.target ? e.target : null;
          var targetNode = target && target.closest ? target : null;
          var isBackdrop =
            target === dlg ||
            (targetNode && targetNode.matches && targetNode.matches("[data-miki-dialog-close='true']")) ||
            (target && target.getAttribute && target.getAttribute("data-miki-dialog-close") === "true");
          if (isBackdrop) {
            mikiDialog.close(dlg);
          }
        });
      }

      var closeBtnCleanups = [];
      var closeBtns = dlg.querySelectorAll("[data-miki-dialog-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          var cleanup = onPointer(btn, "activate", function (e) {
            e.preventDefault();
            mikiDialog.close(dlg);
          });
          closeBtnCleanups.push(cleanup);
        })(closeBtns[i]);
      }

      registerDestroyHandler(dlg, function () {
        off(dlg, "keydown", escHandler);
        if (overlayCleanup) overlayCleanup();
        for (var j = 0; j < closeBtnCleanups.length; j++) {
          closeBtnCleanups[j]();
        }
        if (dlg._mikiFocusTrapCleanup) {
          dlg._mikiFocusTrapCleanup();
          dlg._mikiFocusTrapCleanup = null;
        }
      });
    },

     show: function (dlg) {
       var resolved = resolveEl(dlg);
       if (!resolved) return;
       var dialog = findClosest(resolved, "[data-miki-dialog=\"true\"]") || findClosest(resolved, "dialog");
       if (!dialog) dialog = resolved;
       dlg = dialog;
      var active = document.activeElement;
      if (active && active !== document.body && active.id) {
        dlg.setAttribute("data-miki-dialog-trigger", active.id);
      } else {
        var _id = active && active.tagName ? active.tagName.toLowerCase() + "-trigger" : "dialog-trigger";
        dlg.setAttribute("data-miki-dialog-trigger", _id);
      }

      if (typeof dlg.showModal === "function") {
        dlg.showModal();
      } else {
        dlg.setAttribute("open", "");
        dlg.style.display = "block";
      }

      if (dlg.dataset.mikiFocusTrapped !== "true") {
        dlg._mikiFocusTrapCleanup = miki.focusTrap(dlg);
      }

      var focusable = dlg.querySelectorAll(
        'a[href], area[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length > 0) {
        focusable[0].focus();
      }

      dlg.dispatchEvent(new CustomEvent("miki:dialog:opened"));
    },

     close: function (dlg) {
       var resolved = resolveEl(dlg);
       if (!resolved) return;
       var dialog = findClosest(resolved, "[data-miki-dialog=\"true\"]") || findClosest(resolved, "dialog");
       if (!dialog) dialog = resolved;
       dlg = dialog;
      if (typeof dlg.close === "function") {
        dlg.close();
      } else {
        dlg.removeAttribute("open");
        dlg.style.display = "none";
      }

      if (dlg._mikiFocusTrapCleanup) {
        dlg._mikiFocusTrapCleanup();
        dlg._mikiFocusTrapCleanup = null;
      }

      var triggerId = dlg.getAttribute("data-miki-dialog-trigger");
      if (triggerId) {
        var trigger = document.getElementById(triggerId);
        if (trigger && typeof trigger.focus === "function") {
          trigger.focus();
        }
      }

      dlg.dispatchEvent(new CustomEvent("miki:dialog:closed"));
    },

     toggle: function (dlg) {
       var resolved = resolveEl(dlg);
       if (!resolved) return;
       var dialog = findClosest(resolved, "[data-miki-dialog=\"true\"]") || findClosest(resolved, "dialog");
       if (!dialog) return;
       if (dialog.open) {
         mikiDialog.close(dialog);
       } else {
         mikiDialog.show(dialog);
       }
     },

     destroy: function (dlg) {
       mikiDestroy(dlg);
     }
  };

  window.mikiDialog = mikiDialog;
})();
