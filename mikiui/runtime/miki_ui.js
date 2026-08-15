/* MikiUI UI helpers (offline, dependency-free).
 * Provides framework interactions that work without Alpine.js, so core
 * widgets work in the native desktop window without any CDN.
 */

(function () {
  "use strict";

  // Tab switching for mikiui.components.Tabs.
  window.mikiTabs = {
    show: function (groupId, index) {
      var j = 0;
      for (;;) {
        var panel = document.getElementById(groupId + "-panel-" + j);
        if (!panel) break;
        panel.style.display = j === index ? "" : "none";
        var tab = document.getElementById(groupId + "-tab-" + j);
        if (tab) tab.setAttribute("aria-selected", j === index ? "true" : "false");
        j++;
      }
    },
    activate: function (groupId, index) {
      var i = parseInt(index);
      for (var j = 0, panels = document.getElementById(groupId + "-pages").children; j < panels.length; j++) {
        panels[j].style.display = j === i ? "block" : "none";
      }
      for (var k = 0, tabs = document.getElementById(groupId + "-tablist").children; k < tabs.length; k++) {
        tabs[k].classList.toggle("miki-tab-active", k === i);
        tabs[k].setAttribute("aria-selected", k === i ? "true" : "false");
      }
    },
    close: function (groupId, index) {
      var panel = document.getElementById(groupId + "-panel-" + index);
      if (panel) panel.remove();
      var tab = document.getElementById(groupId + "-tab-" + index);
      if (tab) tab.remove();
    }
  };

  // Close a native <dialog> from a button inside it.
  window.mikiCloseDialog = function (btn) {
    var dlg = btn.closest("dialog");
    if (dlg) dlg.close();
  };

  // Dockable panel controls
  window.mikiDockablePanel = {
    toggle: function (el) {
      var panel = el.closest(".miki-dockable-panel");
      if (panel) {
        var isOpen = panel.querySelector(".miki-dock-body").hasAttribute("hidden");
        panel.querySelector(".miki-dock-body").toggleAttribute("hidden");
      }
    },
    detach: function (el) {
      var panel = el.closest(".miki-dockable-panel");
      if (panel) {
        var isFloating = panel.classList.contains("miki-dock-floating");
        panel.classList.toggle("miki-dock-floating");
        if (isFloating) {
          panel.style.position = "";
          panel.style.zIndex = "";
        } else {
          panel.style.position = "fixed";
          panel.style.zIndex = "1000";
        }
      }
    },
    close: function (el) {
      var panel = el.closest(".miki-dockable-panel");
      if (panel) panel.remove();
    }
  };

  // Splitter/drag handle for SplitView
  window.mikiSplitView = {
    startDrag: function (e, el) {
      var hv = el.querySelector(".miki-splitter");
      var horizontal = el.classList.contains("miki-split-h");
      el.dataset.resizing = "true";
      el.dataset.startX = e.clientX;
      el.dataset.startY = e.clientY;
      el.dataset.left = el.dataset.left || 0;
      el.dataset.top = el.dataset.top || 0;
      var leftPane = el.querySelector(".miki-split-left");
      var rightPane = el.querySelector(".miki-split-right");
      el.dataset.startWidth = leftPane.offsetWidth;
      el.dataset.startHeight = leftPane.offsetHeight;
      document.addEventListener("mousemove", window.mikiSplitView.onDrag);
      document.addEventListener("mouseup", window.mikiSplitView.stopDrag);
    },
    onDrag: function (e) {
      var el = e.target.closest(".miki-splitview") || e.target.closest(".miki-splitview-container");
      if (!el || !el.dataset.resizing) return;
      var horizontal = el.classList.contains("miki-split-h");
      var leftPane = el.querySelector(".miki-split-left");
      var rightPane = el.querySelector(".miki-split-right");
      var deltaX = horizontal ? e.clientX - el.dataset.startX : 0;
      var deltaY = horizontal ? 0 : e.clientY - el.dataset.startY;
      var newWidth = Math.max(100, el.dataset.startWidth + deltaX);
      var newHeight = Math.max(100, el.dataset.startHeight + deltaY);
      if (horizontal && rightPane && leftPane) {
        leftPane.style.width = newWidth + "px";
        rightPane.style.width = (el.offsetWidth - newWidth - 8) + "px";
      } else if (leftPane && rightPane) {
        leftPane.style.height = newHeight + "px";
        rightPane.style.height = (el.offsetHeight - newHeight - 8) + "px";
      }
    },
    stopDrag: function () {
      var el = document.querySelector(".miki-splitview[miki-resizing]");
      if (el) {
        delete el.dataset.resizing;
      }
      document.removeEventListener("mousemove", window.mikiSplitView.onDrag);
      document.removeEventListener("mouseup", window.mikiSplitView.stopDrag);
    }
  };

  // Drawer controls
  window.mikiDrawer = {
    open: function (el) {
      var drawer = el.closest(".miki-drawer");
      if (drawer) {
        drawer.classList.add("miki-drawer-open");
      }
    },
    close: function (el) {
      var drawer = el.closest(".miki-drawer");
      if (drawer) {
        drawer.classList.remove("miki-drawer-open");
      }
    },
    toggle: function (el) {
      var drawer = el.closest(".miki-drawer");
      if (drawer) {
        drawer.classList.toggle("miki-drawer-open");
      }
    }
  };

  // MessageBox close functionality
  window.mikiMessageBox = {
    close: function (btn) {
      var box = btn.closest(".miki-messagebox");
      if (box) box.style.display = "none";
    }
  };

  // DataGrid sorting and filtering
  window.mikiDataGrid = {
    init: function (el) {
      el.dataset.sortField = "";
      el.dataset.sortDir = "asc";
    },
    sort: function (el, field) {
      if (el.dataset.sortField === field) {
        el.dataset.sortDir = el.dataset.sortDir === "asc" ? "desc" : "asc";
      } else {
        el.dataset.sortField = field;
        el.dataset.sortDir = "asc";
      }
      // Re-render rows in sorted order (simplified - real impl would use HTMX)
      var tbody = el.querySelector("tbody");
      if (!tbody) return;
      var rows = Array.from(tbody.querySelectorAll("tr"));
      rows.sort(function (a, b) {
        var aVal = a.cells[0].textContent;
        var bVal = b.cells[0].textContent;
        var dir = el.dataset.sortDir === "asc" ? 1 : -1;
        if (aVal < bVal) return -1 * dir;
        if (aVal > bVal) return 1 * dir;
        return 0;
      });
      rows.forEach(function (r) { tbody.appendChild(r); });
    },
    filter: function (el, query) {
      var tbody = el.querySelector("tbody");
      if (!tbody) return;
      var rows = tbody.querySelectorAll("tr");
      rows.forEach(function (row) {
        var text = row.textContent.toLowerCase();
        row.style.display = text.includes(query.toLowerCase()) ? "" : "none";
      });
    }
  };

  // Generic close helpers for dialogs and modals
  window.mikiClose = {
    dialog: function (btn) {
      var dlg = btn.closest("dialog");
      if (dlg) dlg.close();
    },
    modal: function (btn) {
      var modal = btn.closest(".miki-modal, .miki-messagebox");
      if (modal) modal.style.display = "none";
    }
  };
})();