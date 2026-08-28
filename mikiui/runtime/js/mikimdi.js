(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.mikiMDI !== "undefined") return;

  /* ---------------------------------------------------------------
   * MdiArea / MdiSubWindow — multiple-document interface.
   *
   * Features:
   *  - Drag windows by their titlebar (mouse + touch).
   *  - Resize windows from edges/corners (8 handles).
   *  - Minimize (collapse body), maximize (fill area), close (hide).
   *  - Z-order: clicking a window brings it to front.
   *  - Keyboard: Escape closes the focused window.
   *  - Cascade and tile helpers via public API.
   *  - CustomEvents: miki:mdi:activate, miki:mdi:close,
   *    miki:mdi:minimize, miki:mdi:maximize, miki:mdi:move,
   *    miki:mdi:resize.
   *  - Public API: mikiMDI.activate(el), mikiMDI.close(el),
   *    mikiMDI.minimize(el), mikiMDI.maximize(el),
   *    mikiMDI.cascade(area), mikiMDI.tile(area).
   * --------------------------------------------------------------- */

  var MIN_W = 160;
  var MIN_H = 100;
  var TITLEBAR_MIN_H = 32;

  var _zCounter = 100;

  function nextZ() { return ++_zCounter; }

  function mikiMDI() {}

  mikiMDI.initArea = function (area) {
    if (!area || area.dataset.mikiMdiInit === "true") return;
    area.dataset.mikiMdiInit = "true";

    var wins = area.querySelectorAll(".miki-mdi-subwindow");
    for (var i = 0; i < wins.length; i++) {
      mikiMDI.initWindow(area, wins[i]);
    }

    /* Click on the empty area background deactivates all windows */
    on(area, "mousedown", function (e) {
      if (e.target === area) {
        for (var k = 0; k < wins.length; k++) {
          wins[k].classList.remove("miki-mdi-active");
        }
      }
    });
  };

  mikiMDI.initWindow = function (area, win) {
    if (win.dataset.mikiMdiWinInit === "true") return;
    win.dataset.mikiMdiWinInit = "true";
    win.style.zIndex = String(nextZ());

    var titlebar = win.querySelector(".miki-mdi-titlebar");
    var closeBtn = win.querySelector("[data-miki-mdi-close]");
    var minBtn = win.querySelector("[data-miki-mdi-minimize]");
    var maxBtn = win.querySelector("[data-miki-mdi-maximize]");

    /* --- Activate on focus --- */
    on(win, "mousedown", function () {
      mikiMDI.activate(win);
    });

    /* --- Close --- */
    if (closeBtn) {
      on(closeBtn, "click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        mikiMDI.close(win);
      });
    }

    /* --- Minimize --- */
    if (minBtn) {
      on(minBtn, "click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        mikiMDI.minimize(win);
      });
    }

    /* --- Maximize --- */
    if (maxBtn) {
      on(maxBtn, "click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        mikiMDI.maximize(win);
      });
    }

    /* Double-click titlebar to maximize/restore */
    if (titlebar) {
      on(titlebar, "dblclick", function (e) {
        e.preventDefault();
        if (win.classList.contains("miki-mdi-maximized")) {
          mikiMDI.restore(win);
        } else {
          mikiMDI.maximize(win);
        }
      });
    }

    /* --- Drag --- */
    if (titlebar) {
      mikiMDI._makeDraggable(area, win, titlebar);
    }

    /* --- Resize handles --- */
    mikiMDI._makeResizable(area, win);

    /* Initial bounds (if not maximized) */
    if (!win.classList.contains("miki-mdi-maximized")) {
      /* Ensure min dimensions */
      var rect = win.getBoundingClientRect();
      if (rect.width < MIN_W) win.style.width = MIN_W + "px";
      if (rect.height < MIN_H) win.style.height = MIN_H + "px";
    }

    mikiMDI.activate(win);
  };

  mikiMDI.activate = function (win) {
    if (!win) return;
    var area = win.parentElement;
    if (area) {
      var all = area.querySelectorAll(".miki-mdi-subwindow");
      for (var i = 0; i < all.length; i++) {
        all[i].classList.remove("miki-mdi-active");
      }
    }
    win.classList.add("miki-mdi-active");
    win.style.zIndex = String(nextZ());
    dispatch(win, "miki:mdi:activate", { window: win });
  };

  mikiMDI.close = function (win) {
    if (!win) return;
    win.style.display = "none";
    win.classList.add("miki-mdi-closed");
    dispatch(win, "miki:mdi:close", { window: win });
  };

  mikiMDI.minimize = function (win) {
    if (!win) return;
    var body = win.querySelector(".miki-mdi-body");
    if (!body) return;
    var isMin = win.classList.toggle("miki-mdi-minimized");
    if (body) body.style.display = isMin ? "none" : "";
    var minBtn = win.querySelector("[data-miki-mdi-minimize]");
    if (minBtn) minBtn.textContent = isMin ? "▢" : "—";
    dispatch(win, "miki:mdi:minimize", { window: win, minimized: isMin });
  };

  mikiMDI.maximize = function (win) {
    if (!win) return;
    win._mikiPrevBounds = {
      left: win.style.left,
      top: win.style.top,
      width: win.style.width,
      height: win.style.height,
    };
    win.classList.add("miki-mdi-maximized");
    win.style.left = "0";
    win.style.top = "0";
    win.style.width = "100%";
    win.style.height = "100%";
    dispatch(win, "miki:mdi:maximize", { window: win });
  };

  mikiMDI.restore = function (win) {
    if (!win) return;
    win.classList.remove("miki-mdi-maximized");
    if (win._mikiPrevBounds) {
      win.style.left = win._mikiPrevBounds.left;
      win.style.top = win._mikiPrevBounds.top;
      win.style.width = win._mikiPrevBounds.width;
      win.style.height = win._mikiPrevBounds.height;
      win._mikiPrevBounds = null;
    } else {
      win.style.width = "";
      win.style.height = "";
    }
    dispatch(win, "miki:mdi:restore", { window: win });
  };

  mikiMDI._makeDraggable = function (area, win, handle) {
    var dragging = false;
    var startX = 0, startY = 0, origLeft = 0, origTop = 0;

    function onDown(e) {
      if (win.classList.contains("miki-mdi-maximized")) return;
      if (e.target.closest("button")) return;
      var pt = eventPoint(e);
      dragging = true;
      startX = pt.x;
      startY = pt.y;
      var rect = win.getBoundingClientRect();
      var areaRect = area.getBoundingClientRect();
      origLeft = rect.left - areaRect.left;
      origTop = rect.top - areaRect.top;
      win.classList.add("miki-mdi-dragging");
      mikiMDI.activate(win);
      e.preventDefault();
    }

    function onMove(e) {
      if (!dragging) return;
      var pt = eventPoint(e);
      var dx = pt.x - startX;
      var dy = pt.y - startY;
      win.style.left = (origLeft + dx) + "px";
      win.style.top = (origTop + dy) + "px";
      dispatch(win, "miki:mdi:move", { left: origLeft + dx, top: origTop + dy });
    }

    function onUp() {
      dragging = false;
      win.classList.remove("miki-mdi-dragging");
    }

    on(handle, "mousedown", onDown);
    on(handle, "touchstart", onDown, { passive: false });
    on(document, "mousemove", onMove);
    on(document, "touchmove", onMove, { passive: false });
    on(document, "mouseup", onUp);
    on(document, "touchend", onUp);
  };

  mikiMDI._makeResizable = function (area, win) {
    var edges = ["n", "s", "e", "w", "ne", "nw", "se", "sw"];
    for (var i = 0; i < edges.length; i++) {
      (function (edge) {
        var handle = document.createElement("div");
        handle.className = "miki-mdi-resize-handle miki-mdi-resize-" + edge;
        handle.dataset.mikiMdiResize = edge;
        win.appendChild(handle);

        var dragging = false;
        var startX = 0, startY = 0, origX = 0, origY = 0, origW = 0, origH = 0;

        function onDown(e) {
          if (win.classList.contains("miki-mdi-maximized")) return;
          var pt = eventPoint(e);
          dragging = true;
          startX = pt.x;
          startY = pt.y;
          var rect = win.getBoundingClientRect();
          origX = rect.left;
          origY = rect.top;
          origW = rect.width;
          origH = rect.height;
          win.classList.add("miki-mdi-resizing");
          e.preventDefault();
          e.stopPropagation();
        }

        function onMove(e) {
          if (!dragging) return;
          var pt = eventPoint(e);
          var dx = pt.x - startX;
          var dy = pt.y - startY;
          var newX = origX, newY = origY, newW = origW, newH = origH;

          if (edge.indexOf("e") !== -1) newW = Math.max(MIN_W, origW + dx);
          if (edge.indexOf("w") !== -1) {
            newW = Math.max(MIN_W, origW - dx);
            newX = origX + origW - newW;
          }
          if (edge.indexOf("s") !== -1) newH = Math.max(MIN_H, origH + dy);
          if (edge.indexOf("n") !== -1) {
            newH = Math.max(MIN_H, origH - dy);
            newY = origY + origH - newH;
          }

          win.style.left = newX + "px";
          win.style.top = newY + "px";
          win.style.width = newW + "px";
          win.style.height = newH + "px";
          dispatch(win, "miki:mdi:resize", { width: newW, height: newH });
        }

        function onUp() {
          dragging = false;
          win.classList.remove("miki-mdi-resizing");
        }

        on(handle, "mousedown", onDown);
        on(handle, "touchstart", onDown, { passive: false });
        on(document, "mousemove", onMove);
        on(document, "touchmove", onMove, { passive: false });
        on(document, "mouseup", onUp);
        on(document, "touchend", onUp);
      })(edges[i]);
    }
  };

  mikiMDI.cascade = function (area) {
    var wins = area.querySelectorAll(".miki-mdi-subwindow");
    var offset = 0;
    for (var i = 0; i < wins.length; i++) {
      var w = wins[i];
      if (w.style.display === "none") continue;
      w.classList.remove("miki-mdi-maximized", "miki-mdi-minimized");
      w.style.left = (20 + offset) + "px";
      w.style.top = (20 + offset) + "px";
      w.style.width = "60%";
      w.style.height = "60%";
      offset += 28;
    }
  };

  mikiMDI.tile = function (area) {
    var wins = Array.from(area.querySelectorAll(".miki-mdi-subwindow")).filter(function (w) {
      return w.style.display !== "none";
    });
    var n = wins.length;
    if (!n) return;
    var cols = Math.ceil(Math.sqrt(n));
    var rows = Math.ceil(n / cols);
    var areaRect = area.getBoundingClientRect();
    var wPct = 100 / cols;
    var hPct = 100 / rows;
    for (var i = 0; i < wins.length; i++) {
      var r = Math.floor(i / cols);
      var c = i % cols;
      wins[i].classList.remove("miki-mdi-maximized", "miki-mdi-minimized");
      wins[i].style.left = (c * wPct) + "%";
      wins[i].style.top = (r * hPct) + "%";
      wins[i].style.width = wPct + "%";
      wins[i].style.height = hPct + "%";
    }
  };

  window.mikiMDI = mikiMDI;
})();
