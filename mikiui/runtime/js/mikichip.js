(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiChip = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var chips = container.querySelectorAll("[data-miki-chip=\"true\"]");
      for (var i = 0; i < chips.length; i++) {
        (function (chip) {
           miki.onPointer(chip, "activate", function (e) {
             if (chip.hasAttribute("data-miki-chip-remove")) return;
             var selected = chip.getAttribute("aria-selected") !== "true";
             chip.setAttribute("aria-selected", selected ? "true" : "false");
             if (selected) {
               chip.classList.add("miki-chip-selected");
             } else {
               chip.classList.remove("miki-chip-selected");
             }
             miki.dispatch(chip, "miki:chip:toggled", { selected: selected });
           });

          miki.on(chip, "keydown", function (e) {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              chip.click();
            }
          });

          var removeBtn = chip.querySelector("[data-miki-chip-remove=\"true\"]");
          if (removeBtn) {
            miki.onPointer(removeBtn, "activate", function (e) {
              e.stopPropagation();
              miki.dispatch(chip, "miki:chip:remove", {});
              chip.remove();
            });
          }
        })(chips[i]);
      }
    }
  };

  window.mikiChip = mikiChip;
})();
