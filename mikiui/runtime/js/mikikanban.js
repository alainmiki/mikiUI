(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiKanban = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var items = el.querySelectorAll('[data-miki-kanban-item="true"]');
      var columns = el.querySelectorAll(".miki-kanban-column");

      for (var i = 0; i < items.length; i++) {
        (function (item) {
          item.setAttribute("draggable", "true");
          on(item, "dragstart", function (e) {
            mikiKanban.draggedItem = item;
            item.classList.add("miki-kanban-dragging");
            e.dataTransfer.effectAllowed = "move";
          });
          on(item, "dragend", function () {
            item.classList.remove("miki-kanban-dragging");
            mikiKanban.draggedItem = null;
          });
        })(items[i]);
      }

      for (var j = 0; j < columns.length; j++) {
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
        })(columns[j]);
      }
    },

    draggedItem: null
  };

  window.mikiKanban = mikiKanban;
})();
