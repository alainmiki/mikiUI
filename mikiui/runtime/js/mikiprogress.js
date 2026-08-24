(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiProgress = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var value = parseFloat(el.getAttribute("data-value") || el.getAttribute("value") || 0);
      var max = parseFloat(el.getAttribute("data-max") || el.getAttribute("max") || 100);
      var percent = max > 0 ? (value / max) * 100 : 0;

      // Style native <progress> element
      var nativeProgress = el.querySelector("progress");
      if (nativeProgress) {
        nativeProgress.value = value;
        nativeProgress.max = max;
      }

      // Style custom progress bar
      var fill = el.querySelector(".miki-progress-value");
      if (fill) {
        fill.style.width = percent + "%";
      }

      el.setAttribute("data-miki-progress-percent", Math.round(percent) + "%");
      dispatch(el, "miki:progress:init", { value: value, max: max, percent: percent });
    },

    set: function (el, value, max) {
      max = max || 100;
      var percent = max > 0 ? (value / max) * 100 : 0;

      var nativeProgress = el.querySelector("progress");
      if (nativeProgress) {
        nativeProgress.value = value;
        nativeProgress.max = max;
      }

      var fill = el.querySelector(".miki-progress-value");
      if (fill) {
        fill.style.width = percent + "%";
      }

      el.setAttribute("data-value", value);
      el.setAttribute("data-max", max);
      el.setAttribute("data-miki-progress-percent", Math.round(percent) + "%");
      dispatch(el, "miki:progress:change", { value: value, max: max, percent: percent });
    }
  };

  window.mikiProgress = mikiProgress;
})();
