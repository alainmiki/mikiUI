(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiTabs = {
    show: function (groupId, index) {
      var i = parseInt(index, 10);
      var pagesContainer = document.getElementById(groupId + "-pages");
      var tablist = document.getElementById(groupId + "-tablist");

      if (pagesContainer) {
        for (var j = 0; j < pagesContainer.children.length; j++) {
          pagesContainer.children[j].style.display = j === i ? "block" : "none";
          pagesContainer.children[j].setAttribute("aria-hidden", j !== i ? "true" : "false");
        }
      }

      var panel = document.getElementById(groupId + "-panel-" + i);
      if (panel) {
        panel.style.display = "block";
        panel.setAttribute("aria-hidden", "false");
      }
      for (var n = 0; n < 100; n++) {
        if (n === i) continue;
        var otherPanel = document.getElementById(groupId + "-panel-" + n);
        if (otherPanel) {
          otherPanel.style.display = "none";
          otherPanel.setAttribute("aria-hidden", "true");
        }
        if (!otherPanel && n > 0) break;
      }

      if (tablist) {
        for (var k = 0; k < tablist.children.length; k++) {
          tablist.children[k].classList.toggle("miki-tab-active", k === i);
          tablist.children[k].setAttribute("aria-selected", k === i ? "true" : "false");
          tablist.children[k].setAttribute("tabindex", k === i ? "0" : "-1");
        }
      }

      var allPanels = document.querySelectorAll('[role="tabpanel"][id^="' + groupId + '-panel-"]');
      for (var p = 0; p < allPanels.length; p++) {
        allPanels[p].hidden = p !== i;
        allPanels[p].setAttribute("aria-hidden", p !== i ? "true" : "false");
      }

      miki.dispatch(document, "miki:tabs:changed", { group: groupId, index: i });
    },

    showAlpineFallback: function (groupId, index) {
      var i = parseInt(index, 10);
      var pages = document.getElementById(groupId + "-pages");
      if (pages) {
        for (var j = 0; j < pages.children.length; j++) {
          pages.children[j].style.display = j === i ? "block" : "none";
        }
      }
      var tablist = document.getElementById(groupId + "-tablist");
      if (tablist) {
        for (var k = 0; k < tablist.children.length; k++) {
          tablist.children[k].classList.toggle("miki-tab-active", k === i);
          tablist.children[k].setAttribute("aria-selected", k === i ? "true" : "false");
        }
      }
    },

    activate: function (groupId, index) {
      mikiTabs.show(groupId, index);
    },

    close: function (groupId, index) {
      var panel = document.getElementById(groupId + "-panel-" + index);
      if (panel) panel.remove();
      var tab = document.getElementById(groupId + "-tab-" + index);
      if (tab) tab.remove();
      miki.dispatch(document, "miki:tabs:closed", { group: groupId, index: parseInt(index, 10) });
    },

    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var tabs = container.querySelectorAll('[role="tab"]');
      var tabHandlers = [];
      for (var i = 0; i < tabs.length; i++) {
        (function (tab, idx) {
          var activateCleanup = onPointer(tab, "activate", function (e) {
            e.preventDefault();
            var group = tab.getAttribute("data-miki-tab-group") || tab.getAttribute("aria-controls");
            if (group) {
              var dashIndex = group.lastIndexOf("-panel-");
              var groupId = dashIndex !== -1 ? group.substring(0, dashIndex) : group;
              var panelIdx = dashIndex !== -1 ? parseInt(group.substring(dashIndex + 7), 10) : idx;
              mikiTabs.show(groupId || "miki-tabs", panelIdx);
            }
          });

          var keyHandler = function (e) {
            var tablist = tab.parentNode;
            var allTabs = Array.from(tablist.children);
            var currentIndex = allTabs.indexOf(tab);

            if (e.key === "ArrowRight" || e.key === "ArrowDown") {
              e.preventDefault();
              var next = (currentIndex + 1) % allTabs.length;
              allTabs[next].focus();
              allTabs[next].click();
            } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
              e.preventDefault();
              var prev = (currentIndex - 1 + allTabs.length) % allTabs.length;
              allTabs[prev].focus();
              allTabs[prev].click();
            } else if (e.key === "Home") {
              e.preventDefault();
              allTabs[0].focus();
              allTabs[0].click();
            } else if (e.key === "End") {
              e.preventDefault();
              allTabs[allTabs.length - 1].focus();
              allTabs[allTabs.length - 1].click();
            } else if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              tab.click();
            }
          };
          on(tab, "keydown", keyHandler);

          var startX = 0, startY = 0, endX = 0, endY = 0;
          on(tab, "touchstart", function (e) {
            if (e.touches && e.touches.length > 0) {
              startX = e.touches[0].clientX;
              startY = e.touches[0].clientY;
            }
          });
          var touchEndHandler = function (e) {
            if (!startX || !startY) return;
            endX = e.changedTouches && e.changedTouches[0] ? e.changedTouches[0].clientX : 0;
            endY = e.changedTouches && e.changedTouches[0] ? e.changedTouches[0].clientY : 0;
            var dx = endX - startX;
            var dy = endY - startY;
            var absDx = Math.abs(dx);
            var absDy = Math.abs(dy);
            if (absDx > 30 && absDx > absDy * 1.5) {
              var tablistEl = tab.parentNode;
              var allTabsLocal = Array.from(tablistEl.children);
              var currentIdx = allTabsLocal.indexOf(tab);
              if (dx > 0 && currentIdx > 0) {
                allTabsLocal[currentIdx - 1].click();
              } else if (dx < 0 && currentIdx < allTabsLocal.length - 1) {
                allTabsLocal[currentIdx + 1].click();
              }
            }
          };
          on(tab, "touchend", touchEndHandler);

          tabHandlers.push({
            activateCleanup: activateCleanup,
            tab: tab,
            keyHandler: keyHandler,
            touchEndHandler: touchEndHandler
          });
        })(tabs[i], i);
      }

      registerDestroyHandler(container, function () {
        for (var k = 0; k < tabHandlers.length; k++) {
          var th = tabHandlers[k];
          if (th.activateCleanup) th.activateCleanup();
          off(th.tab, "keydown", th.keyHandler);
          off(th.tab, "touchend", th.touchEndHandler);
        }
      });
    },

    destroy: function (el) {
      mikiDestroy(el);
    }
  };

  window.mikiTabs = mikiTabs;
})();
