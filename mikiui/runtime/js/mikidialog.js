(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDialog = {
    init: function (dlg) {
      if (dlg.dataset.mikiInit === "true") return;
      dlg.dataset.mikiInit = "true";

      // ESC to close
      on(dlg, "keydown", function (e) {
        if (e.key === "Escape" && dlg.open) {
          var closeOnEsc = dlg.getAttribute("data-miki-dialog-close-on-escape");
          if (closeOnEsc === null || closeOnEsc === "true") {
            mikiDialog.close(dlg);
          }
        }
      });

      // Click/Tap on backdrop — activates on both mouse click and touch tap.
      // Treat either the dialog element itself or an explicit overlay child as
      // the backdrop so native <dialog> elements and custom overlay containers
      // behave consistently.
      if (dlg.getAttribute("data-miki-dialog-close-on-overlay") === "true") {
        onPointer(dlg, "activate", function (e) {
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

      // Close buttons inside the dialog
      var closeBtns = dlg.querySelectorAll("[data-miki-dialog-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          onPointer(btn, "activate", function (e) {
            e.preventDefault();
            mikiDialog.close(dlg);
          });
        })(closeBtns[i]);
      }
    },

     show: function (dlg) {
       var resolved = resolveEl(dlg);
       if (!resolved) return;
       var dialog = findClosest(resolved, "[data-miki-dialog=\"true\"]") || findClosest(resolved, "dialog");
       if (!dialog) dialog = resolved;
       dlg = dialog;
      // Save the currently-focused element so we can restore focus later
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

      // Focus trap (skip if already trapped)
      if (dlg.dataset.mikiFocusTrapped !== "true") {
        miki.focusTrap(dlg);
      }

      // Focus first focusable element inside the dialog
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

      // Restore focus to trigger element
      var triggerId = dlg.getAttribute("data-miki-dialog-trigger");
      if (triggerId) {
        var trigger = document.getElementById(triggerId);
        if (trigger && typeof trigger.focus === "function") {
          trigger.focus();
        }
      }
      // Clean up focus trap
      dlg.dataset.mikiFocusTrapped = "false";

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
     }
  };

  window.mikiDialog = mikiDialog;
})();
