(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiContextWindow = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var trigger = container.querySelector(".miki-context-trigger");
      var menu = container.querySelector(".miki-context-menu");

      if (!menu) return;

      var isOpen = false;

      function toggle() {
        if (isOpen) {
          close();
        } else {
          open();
        }
      }

      function open() {
        menu.style.display = "block";
        isOpen = true;
        container.setAttribute("data-miki-context-open", "true");

        // Position the menu
        var rect = menu.getBoundingClientRect();
        var viewport = {
          width: window.innerWidth,
          height: window.innerHeight
        };

        if (rect.right > viewport.width) {
          menu.style.left = "auto";
          menu.style.right = "0";
        }
        if (rect.bottom > viewport.height) {
          menu.style.top = "auto";
          menu.style.bottom = "100%";
        }
      }

      function close() {
        menu.style.display = "none";
        isOpen = false;
        container.setAttribute("data-miki-context-open", "false");
      }

      if (trigger) {
        on(trigger, "click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          toggle();
        });
        on(trigger, "keydown", function (e) {
          if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
            e.preventDefault();
            toggle();
          }
        });
      }

      // Click-away to close
      on(document, "click", function () {
        if (isOpen) {
          close();
        }
      });

      // ESC to close
      on(document, "keydown", function (e) {
        if (e.key === "Escape" && isOpen) {
          close();
        }
      });

      // Menu keyboard navigation
      if (menu) {
        on(menu, "keydown", function (e) {
          var items = Array.from(menu.querySelectorAll('[role="menuitem"]'));
          var currentIndex = items.indexOf(document.activeElement);

          if (e.key === "ArrowDown") {
            e.preventDefault();
            var next = (currentIndex + 1) % items.length;
            items[next].focus();
          } else if (e.key === "ArrowUp") {
            e.preventDefault();
            var prev = (currentIndex - 1 + items.length) % items.length;
            items[prev].focus();
          } else if (e.key === "Escape") {
            close();
          }
        });
      }
    }
  };

  window.mikiContextWindow = mikiContextWindow;
})();
