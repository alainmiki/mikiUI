/* MikiUI UI helpers (offline, dependency-free).
 * Provides framework interactions that do not require Alpine.js, so core
 * widgets work in the native desktop window without any CDN. */

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
  };

  // Close a native <dialog> from a button inside it.
  window.mikiCloseDialog = function (btn) {
    var dlg = btn.closest("dialog");
    if (dlg) dlg.close();
  };
})();
