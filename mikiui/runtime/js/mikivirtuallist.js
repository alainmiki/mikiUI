(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiVirtualList = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var itemHeight = parseInt(container.getAttribute("data-miki-item-height") || "48", 10);
      var overscan = parseInt(container.getAttribute("data-miki-overscan") || "4", 10);
      var onScroll = container.getAttribute("data-miki-virtual-list-on-scroll");
      var content = container.querySelector(".miki-virtual-list-content") || container;
      var items = content.querySelectorAll(".miki-virtual-item");
      if (!items.length) return;

      var totalHeight = items.length * itemHeight;
      content.style.height = totalHeight + "px";
      content.style.position = "relative";

      function render() {
        var scrollTop = container.scrollTop;
        var viewportHeight = container.clientHeight;
        var startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
        var endIndex = Math.min(items.length, Math.ceil((scrollTop + viewportHeight) / itemHeight) + overscan);

        for (var i = 0; i < items.length; i++) {
          if (i >= startIndex && i < endIndex) {
            items[i].style.display = "";
            items[i].style.transform = "translateY(" + (i * itemHeight) + "px)";
          } else {
            items[i].style.display = "none";
          }
        }

        if (onScroll && window[onScroll]) {
          window[onScroll]({
            scrollTop: scrollTop,
            scrollHeight: totalHeight,
            clientHeight: viewportHeight,
            startIndex: startIndex,
            endIndex: endIndex
          });
        }
      }

      miki.on(container, "scroll", render);
      render();
    }
  };

  window.mikiVirtualList = mikiVirtualList;
})();
