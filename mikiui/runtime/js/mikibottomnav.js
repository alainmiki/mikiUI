(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiBottomNav = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var items = container.querySelectorAll(".miki-bottom-nav-item");
      for (var i = 0; i < items.length; i++) {
        (function (item, idx) {
          item.setAttribute("role", "tab");
          item.setAttribute("aria-selected", item.classList.contains("miki-bottom-nav-item-active") ? "true" : "false");

          miki.on(item, "click", function () {
            for (var j = 0; j < items.length; j++) {
              items[j].classList.remove("miki-bottom-nav-item-active");
              items[j].setAttribute("aria-selected", "false");
            }
            item.classList.add("miki-bottom-nav-item-active");
            item.setAttribute("aria-selected", "true");
            miki.dispatch(container, "miki:bottom-nav:changed", { index: idx });
          });

          miki.on(item, "keydown", function (e) {
            var count = items.length;
            var next = -1;
            if (e.key === "ArrowRight" || e.key === "ArrowDown") {
              e.preventDefault();
              next = (idx + 1) % count;
            } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
              e.preventDefault();
              next = (idx - 1 + count) % count;
            } else if (e.key === "Home") {
              e.preventDefault();
              next = 0;
            } else if (e.key === "End") {
              e.preventDefault();
              next = count - 1;
            }
            if (next >= 0 && items[next]) {
              items[next].focus();
            }
          });
        })(items[i], i);
      }
    }
  };

  window.mikiBottomNav = mikiBottomNav;
})();
