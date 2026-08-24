(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiBottomSheet = {
    open: function (el) {
      var sheet = miki.findClosest(el, "[data-miki-bottom-sheet=\"true\"]") || document.querySelector("[data-miki-bottom-sheet=\"true\"]");
      if (!sheet) return;
      var backdrop = sheet.querySelector("[data-miki-bottom-sheet-backdrop]") || document.querySelector("[data-miki-bottom-sheet-backdrop]");
      if (backdrop) backdrop.classList.add("miki-bottom-sheet-backdrop-open");
      sheet.classList.add("miki-bottom-sheet-panel-open");
      sheet.setAttribute("data-miki-bottom-sheet-open", "true");
      sheet.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      var onOpen = sheet.getAttribute("data-miki-bottom-sheet-on-open");
      if (onOpen && window[onOpen]) window[onOpen](sheet);
      miki.dispatch(sheet, "miki:bottom-sheet:opened", {});
    },

    close: function (el) {
      var sheet = miki.findClosest(el, "[data-miki-bottom-sheet=\"true\"]") || document.querySelector("[data-miki-bottom-sheet=\"true\"]");
      if (!sheet) return;
      var backdrop = sheet.querySelector("[data-miki-bottom-sheet-backdrop]") || document.querySelector("[data-miki-bottom-sheet-backdrop]");
      if (backdrop) backdrop.classList.remove("miki-bottom-sheet-backdrop-open");
      sheet.classList.remove("miki-bottom-sheet-panel-open");
      sheet.setAttribute("data-miki-bottom-sheet-open", "false");
      sheet.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
      var onClose = sheet.getAttribute("data-miki-bottom-sheet-on-close");
      if (onClose && window[onClose]) window[onClose](sheet);
      miki.dispatch(sheet, "miki:bottom-sheet:closed", {});
    },

    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var sheet = container.querySelector("[data-miki-bottom-sheet=\"true\"]") || container;
      if (!sheet.hasAttribute("data-miki-bottom-sheet")) return;

      var backdrop = sheet.querySelector("[data-miki-bottom-sheet-backdrop]");
      if (backdrop) {
        miki.on(backdrop, "click", function () {
          mikiBottomSheet.close(sheet);
        });
      }

      var closeBtn = sheet.querySelector("[data-miki-bottom-sheet-close=\"true\"]");
      if (closeBtn) {
        miki.on(closeBtn, "click", function (e) {
          e.preventDefault();
          mikiBottomSheet.close(sheet);
        });
      }

      miki.on(sheet, "keydown", function (e) {
        if (e.key === "Escape") {
          mikiBottomSheet.close(sheet);
        }
      });

      var startY = 0;
      var currentY = 0;
      var isDragging = false;
      var dragHandle = sheet.querySelector(".miki-bottom-sheet-drag-handle");
      var panel = sheet.querySelector(".miki-bottom-sheet-panel") || sheet;

      function onTouchStart(e) {
        startY = e.touches[0].clientY;
        isDragging = true;
        panel.style.transition = "none";
      }

      function onTouchMove(e) {
        if (!isDragging) return;
        currentY = e.touches[0].clientY;
        var diff = currentY - startY;
        if (diff > 0) {
          panel.style.transform = "translateY(" + diff + "px)";
        }
      }

      function onTouchEnd() {
        if (!isDragging) return;
        isDragging = false;
        panel.style.transition = "";
        var diff = currentY - startY;
        if (diff > 100) {
          mikiBottomSheet.close(sheet);
        } else {
          panel.style.transform = "";
          if (sheet.classList.contains("miki-bottom-sheet-panel-open")) {
            panel.style.transform = "translateY(0)";
          }
        }
        startY = 0;
        currentY = 0;
      }

      if (dragHandle) {
        miki.on(dragHandle, "touchstart", onTouchStart, { passive: true });
        miki.on(dragHandle, "touchmove", onTouchMove, { passive: true });
        miki.on(dragHandle, "touchend", onTouchEnd);
      }
    }
  };

  window.mikiBottomSheet = mikiBottomSheet;
})();
