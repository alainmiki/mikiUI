/* mikiNavbar — lightweight helpers for the MikiUI Navbar widget. */
(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.mikiNavbar !== "undefined") return;

  function mikiNavbar() {}

  mikiNavbar.toggle = function (toggleBtn) {
    if (!toggleBtn) return;
    var navbar = toggleBtn.closest(".miki-navbar");
    if (!navbar) return;
    var links = navbar.querySelector(".miki-navbar-links");
    if (!links) return;
    var isOpen = links.classList.toggle("open");
    toggleBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
  };

  mikiNavbar.init = function (navEl) {
    if (!navEl || navEl.dataset.mikiNavbarInit === "true") return;
    navEl.dataset.mikiNavbarInit = "true";

    var toggle = navEl.querySelector(".miki-navbar-toggle");
    if (toggle) {
      var handler = function () {
        mikiNavbar.toggle(toggle);
      };
      on(toggle, "click", handler);
      registerDestroyHandler(navEl, function () {
        off(toggle, "click", handler);
      });
    }

    try {
      var rect = navEl.getBoundingClientRect();
      var height = Math.ceil(rect.height);
      document.documentElement.style.setProperty("--miki-navbar-height", height + "px");
    } catch (e) {
      /* ignore */
    }
  };

  mikiNavbar.destroy = function (el) {
    mikiDestroy(el);
  };

  window.mikiNavbar = mikiNavbar;
})();
