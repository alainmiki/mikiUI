(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiCollapsible = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var header = el.querySelector("[data-miki-collapsible-header=\"true\"]");
      if (header) {
        onPointer(header, "activate", function () {
          mikiCollapsible.toggle(el);
        });
        on(header, "keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            mikiCollapsible.toggle(el);
          }
        });
      }

      // Accordion: only one open at a time
      if (el.getAttribute("data-miki-accordion") === "true") {
        var allInGroup = document.querySelectorAll(
          '[data-miki-accordion-group="' + (el.getAttribute("data-miki-accordion-group") || "") + '"][data-miki-collapsible="true"]'
        );
        // Group auto-init handled below
      }
    },

    toggle: function (el) {
      if (el.classList.contains("miki-collapsible-open")) {
        mikiCollapsible.close(el);
      } else {
        mikiCollapsible.open(el);
      }
    },

    open: function (el) {
      // Close siblings if within an accordion group
      var group = el.getAttribute("data-miki-accordion-group");
      if (group) {
        var siblings = document.querySelectorAll(
          '[data-miki-accordion-group="' + group + '"][data-miki-collapsible="true"]'
        );
        for (var i = 0; i < siblings.length; i++) {
          if (siblings[i] !== el) {
            siblings[i].classList.remove("miki-collapsible-open");
            siblings[i].classList.add("miki-collapsible-closed");
            siblings[i].setAttribute("data-miki-state", "closed");
          }
        }
      }

      el.classList.remove("miki-collapsible-closed");
      el.classList.add("miki-collapsible-open");
      el.setAttribute("data-miki-state", "open");

      var header = el.querySelector("[data-miki-collapsible-header=\"true\"]");
      if (header) {
        header.setAttribute("aria-expanded", "true");
      }

      var toggle = el.querySelector(".miki-collapsible-toggle");
      if (toggle) {
        toggle.textContent = "▼";
      }

      dispatch(el, "miki:collapsible:opened", {});
    },

    close: function (el) {
      el.classList.remove("miki-collapsible-open");
      el.classList.add("miki-collapsible-closed");
      el.setAttribute("data-miki-state", "closed");

      var header = el.querySelector("[data-miki-collapsible-header=\"true\"]");
      if (header) {
        header.setAttribute("aria-expanded", "false");
      }

      var toggle = el.querySelector(".miki-collapsible-toggle");
      if (toggle) {
        toggle.textContent = "▶";
      }

      dispatch(el, "miki:collapsible:closed", {});
    }
  };

  window.mikiCollapsible = mikiCollapsible;
})();
