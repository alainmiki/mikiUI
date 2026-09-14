(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiAccordion = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var groupId = container.getAttribute("data-miki-accordion-group") || generateId("miki-accordion");
      container.setAttribute("data-miki-accordion-group", groupId);

      var items = container.querySelectorAll("[data-miki-collapsible-header=\"true\"]");
      for (var i = 0; i < items.length; i++) {
        var header = items[i];
        var parent = header.closest("[data-miki-collapsible=\"true\"]");
        if (parent) {
          parent.setAttribute("data-miki-accordion-group", groupId);
        }
      }

      var collapsibles = container.querySelectorAll("[data-miki-collapsible=\"true\"]");
      for (var j = 0; j < collapsibles.length; j++) {
        mikiCollapsible.init(collapsibles[j]);
      }

      registerDestroyHandler(container, function () {
        var children = container.querySelectorAll("[data-miki-collapsible=\"true\"]");
        for (var c = 0; c < children.length; c++) {
          mikiDestroy(children[c]);
        }
      });
    },

    destroy: function (el) {
      mikiDestroy(el);
    }
  };

  window.mikiAccordion = mikiAccordion;
})();
