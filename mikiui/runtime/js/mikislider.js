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
        // Create a value display if it doesn't exist
        valueEl = document.createElement("span");
        valueEl.className = "miki-slider-value";
        valueEl.textContent = input.value;
        container.appendChild(valueEl);
      }

      function updateValue() {
        valueEl.textContent = input.value;
        dispatch(input, "miki:slider:change", { value: input.value });
      }

      on(input, "input", updateValue);
      on(input, "change", updateValue);

      // Keyboard: PageUp/PageDown for 10-step increments
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

      // Initial fill styling
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
