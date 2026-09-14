(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiLazyGrid = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      if (!("IntersectionObserver" in window)) return;

      var items = container.querySelectorAll(".miki-lazy-item");
      if (!items.length) return;

      var onLoadMore = container.getAttribute("data-miki-lazy-load-more");

      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("miki-lazy-visible");
              observer.unobserve(entry.target);
            }
          });

          if (onLoadMore && entries[0].isIntersecting) {
            if (window[onLoadMore]) window[onLoadMore](container);
          }
        },
        { rootMargin: "200px" }
      );

      for (var i = 0; i < items.length; i++) {
        observer.observe(items[i]);
      }

      if (onLoadMore) {
        var sentinel = container.querySelector(".miki-lazy-sentinel");
        if (sentinel) {
          observer.observe(sentinel);
        }
      }

      registerDestroyHandler(container, function () {
        observer.disconnect();
      });
    },

    destroy: function (el) {
      mikiDestroy(el);
    }
  };

  window.mikiLazyGrid = mikiLazyGrid;
})();
