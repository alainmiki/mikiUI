(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDial = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var input = container.querySelector('input[type="range"]');
      if (!input) return;

      var valueEl = container.querySelector(".miki-dial-value");
      var knob = container.querySelector(".miki-dial-knob");

      function update() {
        var val = input.value;
        if (valueEl) valueEl.textContent = val;
        if (knob) {
          var percent = ((parseFloat(val) - parseFloat(input.min || 0)) /
            (parseFloat(input.max || 100) - parseFloat(input.min || 0))) * 100;
          var rotation = (percent / 100) * 270 - 135; // -135 to +135 degrees
          knob.style.transform = "rotate(" + rotation + "deg)";
        }
        dispatch(input, "miki:dial:change", { value: val });
      }

      on(input, "input", update);
      on(input, "change", update);

      // Keyboard support
      on(input, "keydown", function (e) {
        var min = parseFloat(input.min) || 0;
        var max = parseFloat(input.max) || 100;
        var step = parseFloat(input.step) || 1;
        var current = parseFloat(input.value) || 0;

        if (e.key === "ArrowUp" || e.key === "ArrowRight") {
          e.preventDefault();
          input.value = Math.min(max, current + step);
          update();
        } else if (e.key === "ArrowDown" || e.key === "ArrowLeft") {
          e.preventDefault();
          input.value = Math.max(min, current - step);
          update();
        } else if (e.key === "Home") {
          e.preventDefault();
          input.value = min;
          update();
        } else if (e.key === "End") {
          e.preventDefault();
          input.value = max;
          update();
        }
      });

      update();
    }
  };

  window.mikiDial = mikiDial;
})();
