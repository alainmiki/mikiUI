(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiMenuBar = {
    init: function (navBar) {
      if (navBar.dataset.mikiInit === "true") return;
      navBar.dataset.mikiInit = "true";

      var titles = navBar.querySelectorAll(".miki-menu-title");
      var menus = navBar.querySelectorAll(".miki-menu");

      for (var i = 0; i < titles.length; i++) {
        (function (title) {
          on(title, "click", function (e) {
            e.stopPropagation();
            var menu = title.nextElementSibling;
            if (menu && menu.classList.contains("miki-menu")) {
              // Close all other menus
              var allMenus = navBar.querySelectorAll(".miki-menu");
              for (var j = 0; j < allMenus.length; j++) {
                if (allMenus[j] !== menu) {
                  allMenus[j].style.display = "none";
                }
              }
              menu.style.display = menu.style.display === "block" ? "none" : "block";
            }
          });

          on(title, "keydown", function (e) {
            if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
              e.preventDefault();
              var menu = title.nextElementSibling;
              if (menu && menu.classList.contains("miki-menu")) {
                menu.style.display = "block";
                var firstItem = menu.querySelector('.miki-menu-item');
                if (firstItem) firstItem.focus();
              }
            }
          });
        })(titles[i]);
      }

      // Click-away to close all menus
      on(document, "click", function () {
        for (var k = 0; k < menus.length; k++) {
          menus[k].style.display = "none";
        }
      });

      // ESC to close menus
      on(document, "keydown", function (e) {
        if (e.key === "Escape") {
          for (var m = 0; m < menus.length; m++) {
            menus[m].style.display = "none";
          }
        }
      });
    }
  };

  window.mikiMenuBar = mikiMenuBar;

  /* ===================== Auto-init System ===================== */

  var widgetRegistry = [
    { selector: '[data-miki-tabs="true"]', init: mikiTabs.init, name: "tabs" },
    { selector: '[data-miki-dialog="true"]', init: mikiDialog.init, name: "dialog" },
    { selector: '[data-miki-modal="true"]', init: mikiModal.init, name: "modal" },
    { selector: '[data-miki-slider="true"]', init: mikiSlider.init, name: "slider" },
    { selector: '[data-miki-dial="true"]', init: mikiDial.init, name: "dial" },
    { selector: '[data-miki-progress="true"]', init: mikiProgress.init, name: "progress" },
    { selector: '[data-miki-progress-dialog="true"]', init: mikiProgressDialog.init, name: "progressDialog" },
    { selector: '[data-miki-collapsible="true"]', init: mikiCollapsible.init, name: "collapsible" },
    { selector: '[data-miki-accordion="true"]', init: mikiAccordion.init, name: "accordion" },
    { selector: '[data-miki-datagrid="true"]', init: mikiDataGrid.init, name: "dataGrid" },
    { selector: '[data-miki-kanban="true"]', init: mikiKanban.init, name: "kanban" },
    { selector: '[data-miki-chat="true"]', init: mikiChat.init, name: "chat" },
    { selector: '[data-miki-dropzone="true"]', init: mikiDropzone.init, name: "dropzone" },
    { selector: '[data-miki-carousel="true"]', init: mikiCarousel.init, name: "carousel" },
    { selector: '[data-miki-messagebox="true"]', init: mikiMessageBox.init, name: "messageBox" },
    { selector: '[data-miki-context-window="true"]', init: mikiContextWindow.init, name: "contextWindow" },
    { selector: '[data-miki-menubar="true"]', init: mikiMenuBar.init, name: "menuBar" },
    { selector: '[data-miki-dockable="true"]', init: mikiDockablePanel.init, name: "dockable" },
    { selector: '[data-miki-splitview="true"]', init: mikiSplitView.init, name: "splitView" },
    { selector: '[data-miki-drawer="true"]', init: mikiDrawer.init, name: "drawer" },
    { selector: '[data-miki-toggle="true"]', init: mikiToggle.init, name: "toggle" },
    { selector: '[data-miki-searchable="true"]', init: mikiSearchableSelect.init, name: "searchable" },
  ];

  function initAll(scope) {
    scope = scope || document;

    for (var i = 0; i < widgetRegistry.length; i++) {
      var widgets = scope.querySelectorAll(widgetRegistry[i].selector);
      for (var j = 0; j < widgets.length; j++) {
        widgetRegistry[i].init(widgets[j]);
      }
    }

    // Drawer close buttons (inside the drawer container)
    var drawerCloseBtns = scope.querySelectorAll("[data-miki-drawer-close=\"true\"]");
    for (var d = 0; d < drawerCloseBtns.length; d++) {
      drawerCloseBtns[d].dataset.mikiInit = "true";
    }

    // Drawer overlay click-to-close
    var drawerOverlays = scope.querySelectorAll("[data-miki-drawer-overlay=\"true\"]");
    for (var o = 0; o < drawerOverlays.length; o++) {
      if (drawerOverlays[o].dataset.mikiInit === "true") continue;
      drawerOverlays[o].dataset.mikiInit = "true";
      (function (overlay) {
        on(overlay, "click", function () {
          var drawer = overlay.closest(".miki-drawer");
          if (drawer) {
            drawer.classList.remove("miki-drawer-open");
            drawer.setAttribute("aria-hidden", "true");
          }
        });
      })(drawerOverlays[o]);
    }

    // Drawer toggle buttons (external)
    var drawerToggles = scope.querySelectorAll("[data-miki-drawer-toggle=\"true\"]");
    for (var t = 0; t < drawerToggles.length; t++) {
      if (drawerToggles[t].dataset.mikiInit === "true") continue;
      drawerToggles[t].dataset.mikiInit = "true";
      (function (btn) {
        on(btn, "click", function (e) {
          e.preventDefault();
          var target = btn.getAttribute("data-miki-drawer-target");
          var drawer;
          if (target) {
            drawer = document.querySelector(target);
          } else {
            drawer = btn.closest(".miki-drawer") || document.querySelector(".miki-drawer");
          }
          if (drawer) {
            drawer.classList.toggle("miki-drawer-open");
            var isOpen = drawer.classList.contains("miki-drawer-open");
            drawer.setAttribute("aria-hidden", !isOpen);
            dispatch(drawer, "miki:drawer:toggled", { open: isOpen });
          }
        });
      })(drawerToggles[t]);
    }

    // Dockable panel action buttons (already bound via init, but handle
    // dynamically-added buttons)
    var dockActions = scope.querySelectorAll("[data-miki-dock-action]");
    for (var u = 0; u < dockActions.length; u++) {
      if (dockActions[u].dataset.mikiInit === "true") continue;
      dockActions[u].dataset.mikiInit = "true";
      (function (btn) {
        var action = btn.getAttribute("data-miki-dock-action");
        on(btn, "click", function (e) {
          e.preventDefault();
          var panel = btn.closest(".miki-dockable-panel");
          if (!panel) return;
          if (action === "toggle") mikiDockablePanel.toggle(panel);
          else if (action === "close") mikiDockablePanel.close(panel);
          else if (action === "detach") mikiDockablePanel.detach(panel);
        });
      })(dockActions[u]);
    }
  }

  /* ---- Global convenience functions (called from onclick attrs) ---- */

  window.mikiCloseDialog = function (btn) {
    var dlg = btn.closest("dialog");
    if (dlg) mikiDialog.close(dlg);
  };

  window.mikiClose = {
    dialog: function (btn) {
      var dlg = btn.closest("dialog");
      if (dlg) mikiDialog.close(dlg);
    },
    modal: function (btn) {
      var modal = btn.closest(".miki-modal");
      if (modal) mikiModal.close(modal);
    }
  };

  /* ---- Auto-init on DOM ready ---- */

  window.MikiUI = {
    init: initAll,
    initAll: initAll,
    version: "1.0",
  };

  window.mikiMenuBar = mikiMenuBar;
})();
