(function () {
  "use strict";

  var miki = window.miki || {};

  /* Widget auto-init registry.
   * Each entry maps a CSS selector to an init function. The bridge
   * (miki_bridge.js) also maintains its own registry and calls these
   * same functions. Widgets register themselves here for backward
   * compatibility and so initAll() works even without the bridge.
   */
  var widgetRegistry = [
    { selector: '[data-miki-tabs="true"]', init: function(el){return window.mikiTabs && mikiTabs.init(el);}, name: "tabs" },
    { selector: '[data-miki-editor-area="true"]', init: function(el){return window.mikiEditorArea && mikiEditorArea.init(el);}, name: "editorArea" },
    { selector: '[data-miki-editor="true"]', init: function(el){return window.mikiIDE && mikiIDE.init(el);}, name: "ide" },
    { selector: '[data-miki-mdiarea="true"]', init: function(el){return window.mikiMDI && mikiMDI.initArea(el);}, name: "mdi" },
    { selector: '[data-miki-stackedpanel="true"]', init: function(el){return window.mikiStackedPanel && mikiStackedPanel.init(el);}, name: "stackedPanel" },
    { selector: '[data-miki-dialog="true"]', init: function(el){return window.mikiDialog && mikiDialog.init(el);}, name: "dialog" },
    { selector: '[data-miki-modal="true"]', init: function(el){return window.mikiModal && mikiModal.init(el);}, name: "modal" },
    { selector: '[data-miki-slider="true"]', init: function(el){return window.mikiSlider && mikiSlider.init(el);}, name: "slider" },
    { selector: '[data-miki-dial="true"]', init: function(el){return window.mikiDial && mikiDial.init(el);}, name: "dial" },
    { selector: '[data-miki-progress="true"]', init: function(el){return window.mikiProgress && mikiProgress.init(el);}, name: "progress" },
    { selector: '[data-miki-progress-dialog="true"]', init: function(el){return window.mikiProgressDialog && mikiProgressDialog.init(el);}, name: "progressDialog" },
    { selector: '[data-miki-collapsible="true"]', init: function(el){return window.mikiCollapsible && mikiCollapsible.init(el);}, name: "collapsible" },
    { selector: '[data-miki-accordion="true"]', init: function(el){return window.mikiAccordion && mikiAccordion.init(el);}, name: "accordion" },
    { selector: '[data-miki-datagrid="true"]', init: function(el){return window.mikiDataGrid && mikiDataGrid.init(el);}, name: "dataGrid" },
    { selector: '[data-miki-kanban="true"]', init: function(el){return window.mikiKanban && mikiKanban.init(el);}, name: "kanban" },
    { selector: '[data-miki-chat="true"]', init: function(el){return window.mikiChat && mikiChat.init(el);}, name: "chat" },
    { selector: '[data-miki-dropzone="true"]', init: function(el){return window.mikiDropzone && mikiDropzone.init(el);}, name: "dropzone" },
    { selector: '[data-miki-carousel="true"]', init: function(el){return window.mikiCarousel && mikiCarousel.init(el);}, name: "carousel" },
    { selector: '[data-miki-messagebox="true"]', init: function(el){return window.mikiMessageBox && mikiMessageBox.init(el);}, name: "messageBox" },
    { selector: '[data-miki-context-window="true"]', init: function(el){return window.mikiContextWindow && mikiContextWindow.init(el);}, name: "contextWindow" },
    { selector: '[data-miki-menubar="true"]', init: function(el){return window.mikiMenuBar && mikiMenuBar.init(el);}, name: "menuBar" },
    { selector: '[data-miki-navbar="true"]', init: function(el){return window.mikiNavbar && mikiNavbar.init && mikiNavbar.init(el);}, name: "navbar" },
    { selector: '[data-miki-dockable="true"]', init: function(el){return window.mikiDockablePanel && mikiDockablePanel.init(el);}, name: "dockable" },
    { selector: '[data-miki-splitview="true"]', init: function(el){return window.mikiSplitView && mikiSplitView.init(el);}, name: "splitView" },
    { selector: '[data-miki-drawer="true"]', init: function(el){return window.mikiDrawer && mikiDrawer.init(el);}, name: "drawer" },
    { selector: '[data-miki-toggle="true"]', init: function(el){return window.mikiToggle && mikiToggle.init(el);}, name: "toggle" },
    { selector: '[data-miki-searchable="true"]', init: function(el){return window.mikiSearchableSelect && mikiSearchableSelect.init(el);}, name: "searchable" },
    { selector: '[data-miki-bottom-sheet="true"]', init: function(el){return window.mikiBottomSheet && mikiBottomSheet.init(el);}, name: "bottomSheet" },
    { selector: '[data-miki-bottom-nav="true"]', init: function(el){return window.mikiBottomNav && mikiBottomNav.init(el);}, name: "bottomNav" },
    { selector: '[data-miki-chip="true"]', init: function(el){return window.mikiChip && mikiChip.init(el);}, name: "chip" },
    { selector: '[data-miki-lazy-grid="true"]', init: function(el){return window.mikiLazyGrid && mikiLazyGrid.init(el);}, name: "lazyGrid" },
    { selector: '[data-miki-virtual-list="true"]', init: function(el){return window.mikiVirtualList && mikiVirtualList.init(el);}, name: "virtualList" },
    { selector: '[data-miki-scrollview]', init: function(el){return window.mikiScrollView && mikiScrollView.init(el);}, name: "scrollView" },
    { selector: '[data-miki-pressable="true"]', init: function(el){return window.mikiPressable && mikiPressable.init(el);}, name: "pressable" }
  ];

  /* Register all widgets with the bridge so mikiBridge.initAll()
   * is the single source of truth for auto-init.
   */
  if (window.mikiBridge && mikiBridge.register) {
    for (var i = 0; i < widgetRegistry.length; i++) {
      var entry = widgetRegistry[i];
      mikiBridge.register(entry.selector, entry.name, entry.init);
    }
  }

  /* Widget init from the local registry (backward compat) */
  function initWidgets(scope) {
    scope = scope || document;
    for (var i = 0; i < widgetRegistry.length; i++) {
      var entry = widgetRegistry[i];
      var widgets;
      if (scope === document) {
        widgets = document.querySelectorAll(entry.selector);
      } else {
        widgets = scope.matches && scope.matches(entry.selector)
          ? [scope]
          : scope.querySelectorAll(entry.selector);
      }
      for (var j = 0; j < widgets.length; j++) {
        var widget = widgets[j];
        var tag = widget && widget.dataset ? widget.dataset.mikiWidgetInit : null;
        if (tag === entry.name) continue;
        try {
          entry.init(widget);
          if (widget && widget.dataset) {
            widget.dataset.mikiWidgetInit = entry.name;
          }
        } catch (e) {
          /* Widget init failed -- do not break the whole page */
        }
      }
    }
  }

  /* Full init: widgets + data-miki-on bindings (via bridge) */
  function fullInitAll(scope) {
    initWidgets(scope);
    if (window.mikiBridge && mikiBridge.initAll) {
      mikiBridge.initAll();
    }
  }

  window.MikiUI = {
    init: fullInitAll,
    initAll: fullInitAll,
    initWidgets: initWidgets,
    version: "2.1",
    registry: widgetRegistry
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      fullInitAll();
    });
  } else {
    fullInitAll();
  }

  function debounce(fn, delay) {
    var timer;
    return function () {
      var args = arguments;
      var context = this;
      clearTimeout(timer);
      timer = setTimeout(function () {
        fn.apply(context, args);
      }, delay);
    };
  }

  function reinitLayoutWidgets() {
    var dockables = document.querySelectorAll('[data-miki-dockable="true"]');
    for (var i = 0; i < dockables.length; i++) {
      var el = dockables[i];
      el.dataset.mikiInit = "";
      if (window.mikiDockablePanel) mikiDockablePanel.init(el);
    }

    var mdiareas = document.querySelectorAll('[data-miki-mdiarea="true"]');
    for (var j = 0; j < mdiareas.length; j++) {
      var area = mdiareas[j];
      area.dataset.mikiMdiInit = "";
      var wins = area.querySelectorAll(".miki-mdi-subwindow");
      for (var w = 0; w < wins.length; w++) {
        wins[w].dataset.mikiMdiWinInit = "";
      }
      if (window.mikiMDI) mikiMDI.initArea(area);
    }

    var splitviews = document.querySelectorAll('[data-miki-splitview="true"]');
    for (var k = 0; k < splitviews.length; k++) {
      var sv = splitviews[k];
      sv.dataset.mikiInit = "";
      if (window.mikiSplitView) mikiSplitView.init(sv);
    }
  }

  var debouncedReinit = debounce(reinitLayoutWidgets, 150);
  window.addEventListener("resize", debouncedReinit);
  window.addEventListener("orientationchange", debouncedReinit);
})();
