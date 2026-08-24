(function () {
  "use strict";

  var miki = window.miki || {};

  var widgetRegistry = [
    { selector: '[data-miki-tabs="true"]', init: window.mikiTabs.init, name: "tabs" },
    { selector: '[data-miki-dialog="true"]', init: window.mikiDialog.init, name: "dialog" },
    { selector: '[data-miki-modal="true"]', init: window.mikiModal.init, name: "modal" },
    { selector: '[data-miki-slider="true"]', init: window.mikiSlider.init, name: "slider" },
    { selector: '[data-miki-dial="true"]', init: window.mikiDial.init, name: "dial" },
    { selector: '[data-miki-progress="true"]', init: window.mikiProgress.init, name: "progress" },
    { selector: '[data-miki-progress-dialog="true"]', init: window.mikiProgressDialog.init, name: "progressDialog" },
    { selector: '[data-miki-collapsible="true"]', init: window.mikiCollapsible.init, name: "collapsible" },
    { selector: '[data-miki-accordion="true"]', init: window.mikiAccordion.init, name: "accordion" },
    { selector: '[data-miki-datagrid="true"]', init: window.mikiDataGrid.init, name: "dataGrid" },
    { selector: '[data-miki-kanban="true"]', init: window.mikiKanban.init, name: "kanban" },
    { selector: '[data-miki-chat="true"]', init: window.mikiChat.init, name: "chat" },
    { selector: '[data-miki-dropzone="true"]', init: window.mikiDropzone.init, name: "dropzone" },
    { selector: '[data-miki-carousel="true"]', init: window.mikiCarousel.init, name: "carousel" },
    { selector: '[data-miki-messagebox="true"]', init: window.mikiMessageBox.init, name: "messageBox" },
    { selector: '[data-miki-context-window="true"]', init: window.mikiContextWindow.init, name: "contextWindow" },
    { selector: '[data-miki-menubar="true"]', init: window.mikiMenuBar.init, name: "menuBar" },
    { selector: '[data-miki-dockable="true"]', init: window.mikiDockablePanel.init, name: "dockable" },
    { selector: '[data-miki-splitview="true"]', init: window.mikiSplitView.init, name: "splitView" },
    { selector: '[data-miki-drawer="true"]', init: window.mikiDrawer.init, name: "drawer" },
    { selector: '[data-miki-toggle="true"]', init: window.mikiToggle.init, name: "toggle" },
    { selector: '[data-miki-searchable="true"]', init: window.mikiSearchableSelect.init, name: "searchable" },
    { selector: '[data-miki-bottom-sheet="true"]', init: window.mikiBottomSheet.init, name: "bottomSheet" },
    { selector: '[data-miki-bottom-nav="true"]', init: window.mikiBottomNav.init, name: "bottomNav" },
    { selector: '[data-miki-chip="true"]', init: window.mikiChip.init, name: "chip" },
    { selector: '[data-miki-lazy-grid="true"]', init: window.mikiLazyGrid.init, name: "lazyGrid" },
    { selector: '[data-miki-virtual-list="true"]', init: window.mikiVirtualList.init, name: "virtualList" },
    { selector: '[data-miki-scrollview]', init: window.mikiScrollView.init, name: "scrollView" },
    { selector: '[data-miki-pressable="true"]', init: window.mikiPressable.init, name: "pressable" }
  ];

  function initAll() {
    for (var i = 0; i < widgetRegistry.length; i++) {
      var widgets = document.querySelectorAll(widgetRegistry[i].selector);
      for (var j = 0; j < widgets.length; j++) {
        try {
          widgetRegistry[i].init(widgets[j]);
        } catch (e) {
          // Widget init failed — don't break the whole page
        }
      }
    }
  }

  window.MikiUI = {
    init: initAll,
    initAll: initAll,
    version: "2.0"
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initAll();
    });
  } else {
    initAll();
  }

  document.addEventListener("miki:swapped", function () {
    initAll();
  });

  document.addEventListener("htmx:afterSwap", function () {
    initAll();
  });
})();
