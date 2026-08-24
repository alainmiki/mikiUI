(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiProgressDialog = {
    init: function (dlg) {
      if (dlg.dataset.mikiInit === "true") return;
      dlg.dataset.mikiInit = "true";

      // Delegate to mikiDialog for backdrop/ESC handling
      mikiDialog.init(dlg);

      var value = parseFloat(dlg.getAttribute("data-value") || 0);
      var max = parseFloat(dlg.getAttribute("data-max") || 100);

      var bar = dlg.querySelector(".miki-progress-bar, progress");
      if (bar) {
        if (bar.tagName === "PROGRESS") {
          bar.value = value;
          bar.max = max;
        } else {
          var fill = bar.querySelector(".miki-progress-value");
          if (fill) {
            var percent = max > 0 ? (value / max) * 100 : 0;
            fill.style.width = percent + "%";
          }
        }
      }
    },

    setValue: function (dlg, value) {
      var max = parseFloat(dlg.getAttribute("data-max") || 100);
      var bar = dlg.querySelector(".miki-progress-bar, progress");
      if (bar) {
        if (bar.tagName === "PROGRESS") {
          bar.value = value;
        } else {
          var fill = bar.querySelector(".miki-progress-value");
          if (fill) {
            var percent = max > 0 ? (value / max) * 100 : 0;
            fill.style.width = percent + "%";
          }
        }
      }
      dlg.setAttribute("data-value", value);
      dispatch(dlg, "miki:progressdialog:value", { value: value, max: max });
    }
  };

  window.mikiProgressDialog = mikiProgressDialog;
})();
