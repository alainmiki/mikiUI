(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiScrollView = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var onScroll = container.getAttribute("data-miki-scrollview-on-scroll");
      if (onScroll) {
        miki.on(container, "scroll", function () {
          if (window[onScroll]) {
            window[onScroll]({
              scrollTop: container.scrollTop,
              scrollLeft: container.scrollLeft,
              scrollHeight: container.scrollHeight,
              scrollWidth: container.scrollWidth,
              clientHeight: container.clientHeight,
              clientWidth: container.clientWidth
            });
          }
        });
      }
    },

    scrollTo: function (el, options) {
      var view = miki.findClosest(el, ".miki-scrollview") || el;
      var x = options && options.left !== undefined ? options.left : view.scrollLeft;
      var y = options && options.top !== undefined ? options.top : view.scrollTop;
      var behavior = options && options.behavior || "auto";
      view.scrollTo({ left: x, top: y, behavior: behavior });
    }
  };

  window.mikiScrollView = mikiScrollView;
})();
