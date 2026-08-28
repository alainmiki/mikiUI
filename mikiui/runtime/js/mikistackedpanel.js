(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.mikiStackedPanel !== "undefined") return;

  /* ---------------------------------------------------------------
   * StackedPanel — a QStackedWidget-like container.
   *
   * Features:
   *  - Click / tap a tab to show its page.
   *  - Keyboard: ArrowLeft/Right to move, Home/End to jump,
   *    Enter/Space to activate.
   *  - ARIA roles: tablist, tab, tabpanel with aria-selected,
   *    aria-controls, roving tabindex.
   *  - CustomEvents: miki:stackedpanel:change { index }.
   *  - Empty-state safe (no pages => no-op).
   *  - Public API: mikiStackedPanel.show(el, index),
   *    mikiStackedPanel.activeIndex(el).
   * --------------------------------------------------------------- */

  function mikiStackedPanel() {}

  mikiStackedPanel.init = function (el) {
    if (!el || el.dataset.mikiStackInit === "true") return;
    el.dataset.mikiStackInit = "true";

    var tabbar = el.querySelector(".miki-stack-tabs");
    var pageContainer = el.querySelector(".miki-stack-pages");
    if (!tabbar || !pageContainer) return;

    var tabs = Array.from(tabbar.querySelectorAll(".miki-stack-tab"));
    var pages = Array.from(pageContainer.children);
    if (!tabs.length || !pages.length) return;

    function show(index, focus) {
      index = Math.max(0, Math.min(index, tabs.length - 1));
      for (var i = 0; i < tabs.length; i++) {
        var active = i === index;
        tabs[i].classList.toggle("miki-stack-tab-active", active);
        tabs[i].setAttribute("aria-selected", active ? "true" : "false");
        tabs[i].setAttribute("tabindex", active ? "0" : "-1");
        if (pages[i]) {
          pages[i].style.display = active ? "" : "none";
          pages[i].setAttribute("aria-hidden", active ? "false" : "true");
        }
      }
      if (focus && tabs[index]) tabs[index].focus();
      dispatch(el, "miki:stackedpanel:change", { index: index });
    }

    mikiStackedPanel._showFn = show;

    for (var i = 0; i < tabs.length; i++) {
      (function (tab, idx) {
        on(tab, "click", function (e) {
          e.preventDefault();
          show(idx, false);
        });

        on(tab, "keydown", function (e) {
          var newIdx = idx;
          switch (e.key) {
            case "ArrowRight":
            case "Down":
              e.preventDefault();
              newIdx = (idx + 1) % tabs.length;
              break;
            case "ArrowLeft":
            case "Up":
              e.preventDefault();
              newIdx = (idx - 1 + tabs.length) % tabs.length;
              break;
            case "Home":
              e.preventDefault();
              newIdx = 0;
              break;
            case "End":
              e.preventDefault();
              newIdx = tabs.length - 1;
              break;
            case "Enter":
            case " ":
              e.preventDefault();
              show(idx, true);
              return;
            default:
              return;
          }
          show(newIdx, true);
        });
      })(tabs[i], i);
    }
  };

  mikiStackedPanel.show = function (el, index) {
    if (!el) return;
    var fn = mikiStackedPanel._showFn;
    if (fn) fn(index, true);
  };

  mikiStackedPanel.activeIndex = function (el) {
    if (!el) return -1;
    var tabbar = el.querySelector(".miki-stack-tabs");
    if (!tabbar) return -1;
    var tabs = tabbar.querySelectorAll(".miki-stack-tab");
    for (var i = 0; i < tabs.length; i++) {
      if (tabs[i].classList.contains("miki-stack-tab-active")) return i;
    }
    return -1;
  };

  window.mikiStackedPanel = mikiStackedPanel;
})();
