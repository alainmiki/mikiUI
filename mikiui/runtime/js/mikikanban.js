(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiKanban = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      mikiKanban.el = el;
      mikiKanban.columns = el.querySelectorAll(".miki-kanban-column");
      mikiKanban.items = el.querySelectorAll('[data-miki-kanban-item="true"]');
      mikiKanban.draggedItem = null;

      for (var i = 0; i < mikiKanban.items.length; i++) {
        var item = mikiKanban.items[i];
        item.setAttribute("draggable", "true");

        /* --- Desktop: HTML5 Drag & Drop --- */
        on(item, "dragstart", function (e) {
          mikiKanban.draggedItem = this;
          this.classList.add("miki-kanban-dragging");
          e.dataTransfer.effectAllowed = "move";
        });
        on(item, "dragend", function () {
          this.classList.remove("miki-kanban-dragging");
          mikiKanban.draggedItem = null;
        });

        /* --- Mobile: Touch events --- */
        on(item, "touchstart", function (e) {
          if (e.touches.length !== 1) return;
          mikiKanban.draggedItem = this;
          this.classList.add("miki-kanban-dragging");
          this._mikiTouchStartY = e.touches[0].clientY;
        }, { passive: true });

        on(item, "touchmove", function (e) {
          if (!mikiKanban.draggedItem) return;
          if (e.touches.length !== 1) return;
          var deltaY = e.touches[0].clientY - (this._mikiTouchStartY || 0);
          /* Only start moving if drag distance exceeds 10px */
          if (Math.abs(deltaY) < 10) return;
          /* Prevent scrolling during drag */
          e.preventDefault();
          /* Find target column based on touch position */
          var touch = e.touches[0];
          var target = document.elementFromPoint(touch.clientX, touch.clientY);
          var column = target ? findClosest(target, ".miki-kanban-column") : null;
          if (column && column !== mikiKanban._lastTargetColumn) {
            mikiKanban._lastTargetColumn = column;
            column.classList.add("miki-drag-over");
          }
          /* Remove highlight from other columns */
          for (var k = 0; k < mikiKanban.columns.length; k++) {
            if (mikiKanban.columns[k] !== column) {
              mikiKanban.columns[k].classList.remove("miki-drag-over");
            }
          }
        }, { passive: false });

        on(item, "touchend", function (e) {
          if (!mikiKanban.draggedItem) return;
          this.classList.remove("miki-kanban-dragging");
          var target = mikiKanban._lastTargetColumn;
          mikiKanban._lastTargetColumn = null;
          mikiKanban.draggedItem = null;
          delete this._mikiTouchStartY;

          if (target && target !== this.parentNode) {
            var fromColumn = "";
            var parentCol = this.closest(".miki-kanban-column");
            if (parentCol) {
              fromColumn = parentCol.getAttribute("data-miki-kanban-column") || "";
            }
            target.appendChild(this);
            target.classList.remove("miki-drag-over");
            var toColumn = target.getAttribute("data-miki-kanban-column") || "";
            dispatch(el, "miki:kanban:drop", {
              item: this.textContent.trim(),
              fromColumn: fromColumn,
              toColumn: toColumn
            });
          }
        });
      }

      /* --- Desktop column drop targets --- */
      for (var j = 0; j < mikiKanban.columns.length; j++) {
        (function (column) {
          on(column, "dragover", function (e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = "move";
            column.classList.add("miki-drag-over");
          });
          on(column, "dragleave", function () {
            column.classList.remove("miki-drag-over");
          });
          on(column, "drop", function (e) {
            e.preventDefault();
            column.classList.remove("miki-drag-over");
            var dragged = mikiKanban.draggedItem;
            if (dragged && dragged !== column) {
              column.appendChild(dragged);
              var columnName = column.getAttribute("data-miki-kanban-column") || "";
              var fromColumn = "";
              var parentCol = dragged.closest(".miki-kanban-column");
              if (parentCol) {
                fromColumn = parentCol.getAttribute("data-miki-kanban-column") || "";
              }
              dispatch(el, "miki:kanban:drop", {
                item: dragged.textContent.trim(),
                fromColumn: fromColumn,
                toColumn: columnName
              });
            }
          });
        })(mikiKanban.columns[j]);
      }

      /* --- Mobile: touch-friendly double-tap to select --- */
      on(el, "touchstart", function (e) {
        if (e.target.matches('[data-miki-kanban-item="true"]')) {
          var now = Date.now();
          var lastTap = el._mikiLastTap || 0;
          if (now - lastTap < 300) {
            /* Double-tap — could open item detail */
            dispatch(el, "miki:kanban:doubletap", {
              item: e.target.textContent.trim()
            });
            e.target.classList.add("miki-kanban-selected");
          }
          el._mikiLastTap = now;
        }
      }, { passive: true });
    },

    draggedItem: null
  };

  window.mikiKanban = mikiKanban;
})();
