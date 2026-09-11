(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.mikiMenuBar !== "undefined") return;

  /* ---------------------------------------------------------------
   * MenuBar — accessible, touch + mouse menu bar.
   *
   * Features:
   *  - Click / tap a top-level label to toggle its dropdown.
   *  - Hover-intent opens (configurable delay) for pointer users.
   *  - Full keyboard support: Enter/Space/ArrowDown to open,
   *    ArrowUp/ArrowDown to move between items, ArrowRight/Left to
   *    move between top-level menus, Escape to close, Tab to leave.
   *  - Click-away and Escape close all menus.
   *  - Touch-friendly: tap outside closes, tap a label toggles.
   *  - ARIA: aria-haspopup, aria-expanded, role=menu/menuitem.
   *  - CustomEvents: miki:menubar:open, miki:menubar:close.
   * --------------------------------------------------------------- */

  var HOVER_OPEN_DELAY = 120;   // ms before hover opens a menu
  var HOVER_CLOSE_DELAY = 250;  // ms before hover closes an un-hovered menu

  function stop(e) { e.stopPropagation(); }

  function mikiMenuBar() {}

  mikiMenuBar.init = function (navBar) {
    if (!navBar || navBar.dataset.mikiMenuInit === "true") return;
    navBar.dataset.mikiMenuInit = "true";

    var menus = Array.from(navBar.querySelectorAll(".miki-menu"));
    var hoverOpenTimer = null;
    var hoverCloseTimer = null;

    function closeAllMenus() {
      for (var i = 0; i < menus.length; i++) {
        var m = menus[i];
        var dropdown = m.querySelector(".miki-menu-dropdown");
        if (dropdown) {
          dropdown.style.display = "none";
        } else if (m.style.display !== "none") {
          m.style.display = "none";
        }
        var btn = m.parentNode ? m.parentNode.querySelector(".miki-menu-title") : null;
        if (btn) {
          btn.setAttribute("aria-expanded", "false");
          btn.classList.remove("miki-menu-title-active");
        }
        dispatch(navBar, "miki:menubar:close", { menu: m });
      }
    }

    function openMenu(menu) {
      closeAllMenus();
      var dropdown = menu.querySelector(".miki-menu-dropdown");
      if (dropdown) {
        dropdown.style.display = "block";
      } else {
        menu.style.display = "block";
      }
      var btn = menu.parentNode ? menu.parentNode.querySelector(".miki-menu-title") : null;
      if (btn) {
        btn.setAttribute("aria-expanded", "true");
        btn.classList.add("miki-menu-title-active");
      }
      dispatch(navBar, "miki:menubar:open", { menu: menu });
    }

    function toggleMenu(menu) {
      var dropdown = menu.querySelector(".miki-menu-dropdown");
      var isOpen = dropdown ? dropdown.style.display === "block" : menu.style.display === "block";
      if (isOpen) {
        closeAllMenus();
      } else {
        openMenu(menu);
      }
    }

    function focusFirstItem(menu) {
      var item = menu.querySelector('.miki-menu-item > a, .miki-menu-item[tabindex]');
      if (item) item.focus();
    }

    function focusLastItem(menu) {
      var items = menu.querySelectorAll('.miki-menu-item > a, .miki-menu-item[tabindex]');
      if (items.length) items[items.length - 1].focus();
    }

    for (var i = 0; i < menus.length; i++) {
      (function (menu) {
        var title = menu.querySelector(".miki-menu-title");
        if (!title) return;

        /* --- Toggle on click / tap --- */
        on(title, "click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          toggleMenu(menu);
          focusFirstItem(menu);
        });

        /* --- Hover intent (pointer only, not touch) --- */
        on(title, "mouseenter", function () {
          if (isTouchDevice()) return;
          clearTimeout(hoverCloseTimer);
          hoverOpenTimer = setTimeout(function () { openMenu(menu); }, HOVER_OPEN_DELAY);
        });

        on(title, "mouseleave", function () {
          if (isTouchDevice()) return;
          clearTimeout(hoverOpenTimer);
          hoverCloseTimer = setTimeout(closeAllMenus, HOVER_CLOSE_DELAY);
        });

        on(menu, "mouseenter", function () {
          if (isTouchDevice()) return;
          clearTimeout(hoverCloseTimer);
        });

        on(menu, "mouseleave", function () {
          if (isTouchDevice()) return;
          hoverCloseTimer = setTimeout(closeAllMenus, HOVER_CLOSE_DELAY);
        });

        /* --- Keyboard on the title button --- */
        on(title, "keydown", function (e) {
          switch (e.key) {
            case "Enter":
            case " ":
            case "ArrowDown":
              e.preventDefault();
              openMenu(menu);
              focusFirstItem(menu);
              break;
            case "ArrowUp":
              e.preventDefault();
              openMenu(menu);
              focusLastItem(menu);
              break;
            case "ArrowRight":
              e.preventDefault();
              focusNextTitle(title);
              break;
            case "ArrowLeft":
              e.preventDefault();
              focusPrevTitle(title);
              break;
            case "Escape":
              e.preventDefault();
              closeAllMenus();
              title.focus();
              break;
          }
        });

        /* --- Keyboard inside the dropdown --- */
        on(menu, "keydown", function (e) {
          var items = Array.from(menu.querySelectorAll('.miki-menu-item > a, .miki-menu-item[tabindex]'));
          if (!items.length) return;
          var idx = items.indexOf(document.activeElement);

          switch (e.key) {
            case "ArrowDown":
              e.preventDefault();
              if (idx < items.length - 1) items[idx + 1].focus();
              break;
            case "ArrowUp":
              e.preventDefault();
              if (idx > 0) items[idx - 1].focus();
              else { closeAllMenus(); title.focus(); }
              break;
            case "ArrowRight":
              e.preventDefault();
              closeAllMenus();
              var next = focusNextTitle(title);
              if (next) {
                var nm = next.parentNode ? next.parentNode.querySelector(".miki-menu-dropdown") : null;
                if (nm) { openMenu(nm); focusFirstItem(nm); }
              }
              break;
            case "ArrowLeft":
              e.preventDefault();
              closeAllMenus();
              var prev = focusPrevTitle(title);
              if (prev) {
                var pm = prev.parentNode ? prev.parentNode.querySelector(".miki-menu-dropdown") : null;
                if (pm) { openMenu(pm); focusFirstItem(pm); }
              }
              break;
            case "Escape":
              e.preventDefault();
              closeAllMenus();
              title.focus();
              break;
            case "Tab":
              closeAllMenus();
              break;
          }
        });

        /* Prevent clicks inside dropdown from bubbling to document */
        on(menu, "click", stop);
      })(menus[i]);
    }

    function focusNextTitle(title) {
      var titles = Array.from(navBar.querySelectorAll(".miki-menu-title"));
      var idx = titles.indexOf(title);
      if (idx < titles.length - 1) { titles[idx + 1].focus(); return titles[idx + 1]; }
      return null;
    }

    function focusPrevTitle(title) {
      var titles = Array.from(navBar.querySelectorAll(".miki-menu-title"));
      var idx = titles.indexOf(title);
      if (idx > 0) { titles[idx - 1].focus(); return titles[idx - 1]; }
      return null;
    }

    /* --- Click / tap outside closes menus --- */
    on(document, "click", closeAllMenus);
    on(document, "touchstart", function (e) {
      if (!navBar.contains(e.target)) closeAllMenus();
    });

    /* --- Global Escape --- */
    on(document, "keydown", function (e) {
      if (e.key === "Escape") closeAllMenus();
    });
  };

  window.mikiMenuBar = mikiMenuBar;
})();
