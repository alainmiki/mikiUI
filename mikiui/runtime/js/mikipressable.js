(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiPressable = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var els = container.querySelectorAll("[data-miki-pressable=\"true\"]");
      var pressHandlers = [];
      for (var i = 0; i < els.length; i++) {
        (function (el) {
          if (el.classList.contains("miki-press-disabled")) return;
          var pointerDownHandler = function () {
            el.classList.add("miki-press-active");
          };
          var pointerUpHandler = function () {
            el.classList.remove("miki-press-active");
          };
          var pointerLeaveHandler = function () {
            el.classList.remove("miki-press-active");
          };
          miki.on(el, "pointerdown", pointerDownHandler);
          miki.on(el, "pointerup", pointerUpHandler);
          miki.on(el, "pointerleave", pointerLeaveHandler);
          pressHandlers.push({
            el: el,
            down: pointerDownHandler,
            up: pointerUpHandler,
            leave: pointerLeaveHandler
          });
        })(els[i]);
      }

      registerDestroyHandler(container, function () {
        for (var j = 0; j < pressHandlers.length; j++) {
          var ph = pressHandlers[j];
          off(ph.el, "pointerdown", ph.down);
          off(ph.el, "pointerup", ph.up);
          off(ph.el, "pointerleave", ph.leave);
        }
      });
    },

    destroy: function (el) {
      mikiDestroy(el);
    }
  };

  window.mikiPressable = mikiPressable;
})();
