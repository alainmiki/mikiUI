(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiToggle = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      // The toggle button's inner icon is a child <i> or span
      var iconEl = el.querySelector(".miki-toggle-icon") || el.firstElementChild;

      function swap() {
        var iconOn = el.getAttribute("data-miki-icon-on");
        var iconOff = el.getAttribute("data-miki-icon-off");
        var isOn = el.getAttribute("data-miki-state") === "on";
        var newState = isOn ? "off" : "on";
        var newIcon = isOn ? iconOff : iconOn;
        if (iconEl) iconEl.textContent = newIcon;
        el.setAttribute("data-miki-state", newState);
        el.setAttribute("aria-pressed", isOn ? "false" : "true");

        var labelOn = el.getAttribute("data-miki-aria-label-on");
        var labelOff = el.getAttribute("data-miki-aria-label-off");
        var newLabel = isOn ? labelOff : labelOn;
        if (newLabel) el.setAttribute("aria-label", newLabel);

        dispatch(el, "miki:toggle:changed", { state: newState });
      }

      on(el, "click", function (e) {
        e.preventDefault();
        swap();
      });

      // Keyboard: Enter/Space toggles
      on(el, "keydown", function (e) {
        if (e.key === " " || e.key === "Enter") {
          e.preventDefault();
          swap();
        }
      });

      // Touch: tap toggles (click handles this, but add explicit touch support)
      on(el, "touchend", function (e) {
        e.preventDefault();
        swap();
      }, { passive: false });

      // Initialize state
      if (!el.getAttribute("data-miki-state")) {
        el.setAttribute("data-miki-state", "on");
        el.setAttribute("aria-pressed", "true");
      }
    }
  };

  window.mikiToggle = mikiToggle;
})();
