(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiSlider = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var input = container.querySelector('input[type="range"]');
      if (!input) return;

      var valueEl = container.querySelector(".miki-slider-value");
      if (!valueEl) {
        valueEl = document.createElement("span");
        valueEl.className = "miki-slider-value";
        valueEl.textContent = input.value;
        container.appendChild(valueEl);
      }

      function updateValue() {
        valueEl.textContent = input.value;
        miki.dispatch(input, "miki:slider:change", { value: input.value });
      }

      var inputHandler = function () { updateValue(); };
      var changeHandler = function () { updateValue(); };
      on(input, "input", inputHandler);
      on(input, "change", changeHandler);

      var touchStartHandler = function (e) {
        input.dataset.mikiDragging = "true";
        var touch = e.touches && e.touches[0];
        input.dataset.touchStartX = touch ? touch.clientX : 0;
        input.dataset.touchStartY = touch ? touch.clientY : 0;
      };

      var touchMoveHandler = function (e) {
        if (input.dataset.mikiDragging === "true") {
          var touch = e.touches && e.touches[0];
          if (touch) {
            var dx = Math.abs(touch.clientX - parseFloat(input.dataset.touchStartX || 0));
            var dy = Math.abs(touch.clientY - parseFloat(input.dataset.touchStartY || 0));
            if (dx >= dy) {
              e.preventDefault();
            }
          }
        }
      };

      var touchEndHandler = function () {
        input.dataset.mikiDragging = "false";
      };

      on(input, "touchstart", touchStartHandler);
      on(input, "touchmove", touchMoveHandler, { passive: false });
      on(input, "touchend", touchEndHandler);

      var keyHandler = function (e) {
        var min = parseFloat(input.min) || 0;
        var max = parseFloat(input.max) || 100;
        var step = parseFloat(input.step) || 1;
        var current = parseFloat(input.value) || 0;

        if (e.key === "PageUp") {
          e.preventDefault();
          input.value = Math.min(max, current + step * 10);
          updateValue();
        } else if (e.key === "PageDown") {
          e.preventDefault();
          input.value = Math.max(min, current - step * 10);
          updateValue();
        }
      };
      on(input, "keydown", keyHandler);

      var fillHandler = function () { mikiSlider.updateFill(input); };
      on(input, "input", fillHandler);

      mikiSlider.updateFill(input);

      registerDestroyHandler(container, function () {
        off(input, "input", inputHandler);
        off(input, "change", changeHandler);
        off(input, "touchstart", touchStartHandler);
        off(input, "touchmove", touchMoveHandler);
        off(input, "touchend", touchEndHandler);
        off(input, "keydown", keyHandler);
        off(input, "input", fillHandler);
      });
    },

    destroy: function (el) {
      mikiDestroy(el);
    },

    updateFill: function (input) {
      var percent = ((parseFloat(input.value) - parseFloat(input.min || 0)) /
        (parseFloat(input.max || 100) - parseFloat(input.min || 0))) * 100;
      input.style.setProperty("--miki-slider-fill", percent + "%");
    }
  };

  window.mikiSlider = mikiSlider;
})();
