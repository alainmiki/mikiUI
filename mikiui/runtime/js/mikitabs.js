(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiTabs = {
    show: function (groupId, index) {
      var i = parseInt(index, 10);
      var pagesContainer = document.getElementById(groupId + "-pages");
      var tablist = document.getElementById(groupId + "-tablist");

      // Show/hide panels
      if (pagesContainer) {
        for (var j = 0; j < pagesContainer.children.length; j++) {
          pagesContainer.children[j].style.display = j === i ? "block" : "none";
          pagesContainer.children[j].setAttribute("aria-hidden", j !== i ? "true" : "false");
        }
      }

      // Also handle individual panel elements by ID (for the Div-based tabs)
      var panel = document.getElementById(groupId + "-panel-" + i);
      if (panel) {
        panel.style.display = "block";
        panel.setAttribute("aria-hidden", "false");
      }
      // Hide other panels
      for (var n = 0; n < 100; n++) {
        if (n === i) continue;
        var otherPanel = document.getElementById(groupId + "-panel-" + n);
        if (otherPanel) {
          otherPanel.style.display = "none";
          otherPanel.setAttribute("aria-hidden", "true");
        }
        if (!otherPanel && n > 0) break;
      }

      // Update tab buttons
      if (tablist) {
        for (var k = 0; k < tablist.children.length; k++) {
          tablist.children[k].classList.toggle("miki-tab-active", k === i);
          tablist.children[k].setAttribute("aria-selected", k === i ? "true" : "false");
          tablist.children[k].setAttribute("tabindex", k === i ? "0" : "-1");
        }
      }

      // Sync hidden Section elements with [role=tabpanel]
      var allPanels = document.querySelectorAll('[role="tabpanel"][id^="' + groupId + '-panel-"]');
      for (var p = 0; p < allPanels.length; p++) {
        allPanels[p].hidden = p !== i;
        allPanels[p].setAttribute("aria-hidden", p !== i ? "true" : "false");
      }

      dispatch(document, "miki:tabs:changed", { group: groupId, index: i });
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
      dispatch(document, "miki:tabs:closed", { group: groupId, index: parseInt(index, 10) });
    },

    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      // Find all tab buttons within this container
      var tabs = container.querySelectorAll('[role="tab"]');
      for (var i = 0; i < tabs.length; i++) {
        (function (tab, idx) {
          on(tab, "click", function (e) {
            e.preventDefault();
            var group = tab.getAttribute("data-miki-tab-group") || tab.getAttribute("aria-controls");
            if (group) {
              var dashIndex = group.lastIndexOf("-panel-");
              var groupId = dashIndex !== -1 ? group.substring(0, dashIndex) : group;
              var panelIdx = dashIndex !== -1 ? parseInt(group.substring(dashIndex + 7), 10) : idx;
              mikiTabs.show(groupId || "miki-tabs", panelIdx);
            }
          });

          // Keyboard navigation
          on(tab, "keydown", function (e) {
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
          });
        })(tabs[i], i);
      }
    }
  };

  window.mikiTabs = mikiTabs;
})();
