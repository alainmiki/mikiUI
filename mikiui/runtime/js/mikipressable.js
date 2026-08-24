(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiPressable = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var els = container.querySelectorAll("[data-miki-pressable=\"true\"]");
      for (var i = 0; i < els.length; i++) {
        (function (el) {
          if (el.classList.contains("miki-press-disabled")) return;
          miki.on(el, "pointerdown", function () {
            el.classList.add("miki-press-active");
          });
          miki.on(el, "pointerup", function () {
            el.classList.remove("miki-press-active");
          });
          miki.on(el, "pointerleave", function () {
            el.classList.remove("miki-press-active");
          });
        })(els[i]);
      }
    }
  };

  window.mikiPressable = mikiPressable;
})();
