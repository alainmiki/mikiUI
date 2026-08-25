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

      on(input, "input", updateValue);
      on(input, "change", updateValue);

      /* Touch drag: prevent page scroll while dragging the thumb */
      on(input, "touchstart", function (e) {
        input.dataset.mikiDragging = "true";
        var touch = e.touches && e.touches[0];
        input.dataset.touchStartX = touch ? touch.clientX : 0;
        input.dataset.touchStartY = touch ? touch.clientY : 0;
      });

      on(input, "touchmove", function (e) {
        if (input.dataset.mikiDragging === "true") {
          var touch = e.touches && e.touches[0];
          /* Allow native range input to update value; just prevent scroll */
          if (touch) {
            var dx = Math.abs(touch.clientX - parseFloat(input.dataset.touchStartX || 0));
            var dy = Math.abs(touch.clientY - parseFloat(input.dataset.touchStartY || 0));
            /* If horizontal movement, prevent vertical scroll */
            if (dx >= dy) {
              e.preventDefault();
            }
          }
        }
      }, { passive: false });

      on(input, "touchend", function () {
        input.dataset.mikiDragging = "false";
      });

      /* Keyboard: PageUp/PageDown for 10-step increments */
      on(input, "keydown", function (e) {
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
      });

      /* Initial fill styling */
      mikiSlider.updateFill(input);
      on(input, "input", function () { mikiSlider.updateFill(input); });
    },

    updateFill: function (input) {
      var percent = ((parseFloat(input.value) - parseFloat(input.min || 0)) /
        (parseFloat(input.max || 100) - parseFloat(input.min || 0))) * 100;
      input.style.setProperty("--miki-slider-fill", percent + "%");
    }
  };

  window.mikiSlider = mikiSlider;
})();
