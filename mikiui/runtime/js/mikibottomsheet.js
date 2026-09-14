(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiBottomSheet = {
    _resolve: function (el) {
      if (!el) {
        return document.querySelector("[data-miki-bottom-sheet=\"true\"]");
      }
      if (typeof el === "string") {
        var found = document.querySelector(el);
        if (found) return found;
        return document.querySelector("[data-miki-bottom-sheet=\"true\"]");
      }
      var sheet = findClosest(el, "[data-miki-bottom-sheet=\"true\"]");
      return sheet || el;
    },

    open: function (el) {
      var sheet = mikiBottomSheet._resolve(el);
      if (!sheet) return;

      var backdrop = sheet.querySelector(".miki-bottom-sheet-backdrop");
      var panel = sheet.querySelector(".miki-bottom-sheet-panel");
      if (!panel) return;

      if (!sheet.dataset.mikiSavedOverflow) {
        sheet.dataset.mikiSavedOverflow = document.body.style.overflow || "";
      }

      document.body.style.overflow = "hidden";
      if (backdrop) backdrop.classList.add("miki-bottom-sheet-backdrop-open");
      panel.classList.add("miki-bottom-sheet-panel-open");
      sheet.setAttribute("data-miki-bottom-sheet-open", "true");
      sheet.setAttribute("aria-hidden", "false");

      var onOpen = sheet.getAttribute("data-miki-bottom-sheet-on-open");
      if (onOpen && window[onOpen]) window[onOpen](sheet);
      dispatch(sheet, "miki:bottom-sheet:opened", {});
    },

    close: function (el) {
      var sheet = mikiBottomSheet._resolve(el);
      if (!sheet) return;

      var backdrop = sheet.querySelector(".miki-bottom-sheet-backdrop");
      var panel = sheet.querySelector(".miki-bottom-sheet-panel");
      if (!panel) return;

      document.body.style.overflow = sheet.dataset.mikiSavedOverflow || "";
      delete sheet.dataset.mikiSavedOverflow;

      if (backdrop) backdrop.classList.remove("miki-bottom-sheet-backdrop-open");
      panel.classList.remove("miki-bottom-sheet-panel-open");
      sheet.setAttribute("data-miki-bottom-sheet-open", "false");
      sheet.setAttribute("aria-hidden", "true");

      var onClose = sheet.getAttribute("data-miki-bottom-sheet-on-close");
      if (onClose && window[onClose]) window[onClose](sheet);
      dispatch(sheet, "miki:bottom-sheet:closed", {});
    },

    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      if (!container.hasAttribute("data-miki-bottom-sheet")) return;

      var sheet = container;
      var backdrop = sheet.querySelector(".miki-bottom-sheet-backdrop");
      var panel = sheet.querySelector(".miki-bottom-sheet-panel");
      if (!panel) return;

      var backdropCleanup = null;
      if (backdrop) {
        backdropCleanup = onPointer(backdrop, "activate", function () {
          mikiBottomSheet.close(sheet);
        });
      }

      var closeBtnCleanup = null;
      var closeBtn = sheet.querySelector("[data-miki-bottom-sheet-close=\"true\"]");
      if (closeBtn) {
        closeBtnCleanup = onPointer(closeBtn, "activate", function (e) {
          e.preventDefault();
          mikiBottomSheet.close(sheet);
        });
      }

      var escHandler = function onEsc(e) {
        if (e.key === "Escape" && sheet.getAttribute("data-miki-bottom-sheet-open") === "true") {
          mikiBottomSheet.close(sheet);
        }
      };
      on(document, "keydown", escHandler);

      var dragHandlers = [];
      var startY = 0;
      var currentY = 0;
      var isDragging = false;
      var dragHandle = sheet.querySelector(".miki-bottom-sheet-drag-handle");

      function onDragStart(e) {
        if (e.touches && e.touches[0]) {
          startY = e.touches[0].clientY;
        } else {
          startY = e.clientY;
        }
        isDragging = true;
        panel.style.transition = "none";
      }

      function onDragMove(e) {
        if (!isDragging) return;
        var clientY = (e.touches && e.touches[0]) ? e.touches[0].clientY : e.clientY;
        currentY = clientY;
        var diff = currentY - startY;
        if (diff > 0) {
          panel.style.transform = "translateY(" + diff + "px)";
        }
      }

      function onDragEnd() {
        if (!isDragging) return;
        isDragging = false;
        panel.style.transition = "";
        var diff = currentY - startY;
        if (diff > 100) {
          mikiBottomSheet.close(sheet);
        } else {
          panel.style.transform = "";
        }
        startY = 0;
        currentY = 0;
      }

      if (dragHandle) {
        on(dragHandle, "touchstart", onDragStart, { passive: true });
        dragHandlers.push({ el: dragHandle, event: "touchstart", handler: onDragStart, opts: { passive: true } });
        on(dragHandle, "touchmove", onDragMove, { passive: true });
        dragHandlers.push({ el: dragHandle, event: "touchmove", handler: onDragMove, opts: { passive: true } });
        on(dragHandle, "touchend", onDragEnd);
        dragHandlers.push({ el: dragHandle, event: "touchend", handler: onDragEnd, opts: false });
        on(dragHandle, "mousedown", onDragStart, { passive: true });
        dragHandlers.push({ el: dragHandle, event: "mousedown", handler: onDragStart, opts: { passive: true } });
        on(document, "mousemove", onDragMove, { passive: true });
        dragHandlers.push({ el: document, event: "mousemove", handler: onDragMove, opts: { passive: true } });
        on(document, "mouseup", onDragEnd);
        dragHandlers.push({ el: document, event: "mouseup", handler: onDragEnd, opts: false });
      }

      registerDestroyHandler(sheet, function () {
        if (backdropCleanup) backdropCleanup();
        if (closeBtnCleanup) closeBtnCleanup();
        off(document, "keydown", escHandler);
        for (var k = 0; k < dragHandlers.length; k++) {
          var h = dragHandlers[k];
          off(h.el, h.event, h.handler, h.opts);
        }
      });
    },

    destroy: function (el) {
      mikiDestroy(el);
    }
  };

  window.mikiBottomSheet = mikiBottomSheet;
})();
