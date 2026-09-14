(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.mikiMDI !== "undefined") return;

  var MIN_W = 160;
  var MIN_H = 100;
  var TITLEBAR_MIN_H = 32;

  var _zCounter = 100;

  function nextZ() { return ++_zCounter; }

  function mikiMDI() {}

  var mikiMDI = {
    initArea: function (area) {
      if (!area || area.dataset.mikiMdiInit === "true") return;
      area.dataset.mikiMdiInit = "true";

      var wins = area.querySelectorAll(".miki-mdi-subwindow");
      for (var i = 0; i < wins.length; i++) {
        mikiMDI.initWindow(area, wins[i]);
      }

      var mousedownHandler = function (e) {
        if (e.target === area) {
          for (var k = 0; k < wins.length; k++) {
            wins[k].classList.remove("miki-mdi-active");
          }
        }
      };
      on(area, "mousedown", mousedownHandler);

      registerDestroyHandler(area, function () {
        off(area, "mousedown", mousedownHandler);
      });
    },

    initWindow: function (area, win) {
      if (win.dataset.mikiMdiWinInit === "true") return;
      win.dataset.mikiMdiWinInit = "true";
      win.style.zIndex = String(nextZ());

      var titlebar = win.querySelector(".miki-mdi-titlebar");
      var closeBtn = win.querySelector("[data-miki-mdi-close]");
      var minBtn = win.querySelector("[data-miki-mdi-minimize]");
      var maxBtn = win.querySelector("[data-miki-mdi-maximize]");

      var activateHandler = function () { mikiMDI.activate(win); };
      on(win, "mousedown", activateHandler);

      var closeClickHandler = null;
      if (closeBtn) {
        closeClickHandler = function (e) {
          e.preventDefault();
          e.stopPropagation();
          mikiMDI.close(win);
        };
        on(closeBtn, "click", closeClickHandler);
      }

      var minClickHandler = null;
      if (minBtn) {
        minClickHandler = function (e) {
          e.preventDefault();
          e.stopPropagation();
          mikiMDI.minimize(win);
        };
        on(minBtn, "click", minClickHandler);
      }

      var maxClickHandler = null;
      if (maxBtn) {
        maxClickHandler = function (e) {
          e.preventDefault();
          e.stopPropagation();
          mikiMDI.maximize(win);
        };
        on(maxBtn, "click", maxClickHandler);
      }

      var dblClickHandler = null;
      if (titlebar) {
        dblClickHandler = function (e) {
          e.preventDefault();
          if (win.classList.contains("miki-mdi-maximized")) {
            mikiMDI.restore(win);
          } else {
            mikiMDI.maximize(win);
          }
        };
        on(titlebar, "dblclick", dblClickHandler);
      }

      if (titlebar) {
        mikiMDI._makeDraggable(area, win, titlebar);
      }

      mikiMDI._makeResizable(area, win);

      if (!win.classList.contains("miki-mdi-maximized")) {
        var rect = win.getBoundingClientRect();
        if (rect.width < MIN_W) win.style.width = MIN_W + "px";
        if (rect.height < MIN_H) win.style.height = MIN_H + "px";
      }

      mikiMDI.activate(win);

      var dragCleanups = win._mikiDragCleanups || [];
      var resizeCleanups = win._mikiResizeCleanups || [];

      registerDestroyHandler(win, function () {
        off(win, "mousedown", activateHandler);
        if (closeClickHandler) off(closeBtn, "click", closeClickHandler);
        if (minClickHandler) off(minBtn, "click", minClickHandler);
        if (maxClickHandler) off(maxBtn, "click", maxClickHandler);
        if (dblClickHandler) off(titlebar, "dblclick", dblClickHandler);
        for (var d = 0; d < dragCleanups.length; d++) {
          var dh = dragCleanups[d];
          off(dh.el, dh.event, dh.handler, dh.opts);
        }
        for (var r = 0; r < resizeCleanups.length; r++) {
          var rh = resizeCleanups[r];
          off(rh.el, rh.event, rh.handler, rh.opts);
        }
      });
    },

    activate: function (win) {
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
    },

    close: function (win) {
      if (!win) return;
      win.style.display = "none";
      win.classList.add("miki-mdi-closed");
      dispatch(win, "miki:mdi:close", { window: win });
    },

    minimize: function (win) {
      if (!win) return;
      var body = win.querySelector(".miki-mdi-body");
      if (!body) return;
      var isMin = win.classList.toggle("miki-mdi-minimized");
      if (body) body.style.display = isMin ? "none" : "";
      var minBtn = win.querySelector("[data-miki-mdi-minimize]");
      if (minBtn) minBtn.textContent = isMin ? "▢" : "—";
      dispatch(win, "miki:mdi:minimize", { window: win, minimized: isMin });
    },

    maximize: function (win) {
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
    },

    restore: function (win) {
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
    },

    _makeDraggable: function (area, win, handle) {
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

      var dragCleanups = [];
      on(handle, "mousedown", onDown);
      dragCleanups.push({ el: handle, event: "mousedown", handler: onDown, opts: false });
      on(handle, "touchstart", onDown, { passive: false });
      dragCleanups.push({ el: handle, event: "touchstart", handler: onDown, opts: { passive: false } });
      on(document, "mousemove", onMove);
      dragCleanups.push({ el: document, event: "mousemove", handler: onMove, opts: false });
      on(document, "touchmove", onMove, { passive: false });
      dragCleanups.push({ el: document, event: "touchmove", handler: onMove, opts: { passive: false } });
      on(document, "mouseup", onUp);
      dragCleanups.push({ el: document, event: "mouseup", handler: onUp, opts: false });
      on(document, "touchend", onUp);
      dragCleanups.push({ el: document, event: "touchend", handler: onUp, opts: false });

      win._mikiDragCleanups = dragCleanups;
    },

    _makeResizable: function (area, win) {
      var edges = ["n", "s", "e", "w", "ne", "nw", "se", "sw"];
      var allCleanups = [];
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

          var edgeCleanups = [];
          on(handle, "mousedown", onDown);
          edgeCleanups.push({ el: handle, event: "mousedown", handler: onDown, opts: false });
          on(handle, "touchstart", onDown, { passive: false });
          edgeCleanups.push({ el: handle, event: "touchstart", handler: onDown, opts: { passive: false } });
          on(document, "mousemove", onMove);
          edgeCleanups.push({ el: document, event: "mousemove", handler: onMove, opts: false });
          on(document, "touchmove", onMove, { passive: false });
          edgeCleanups.push({ el: document, event: "touchmove", handler: onMove, opts: { passive: false } });
          on(document, "mouseup", onUp);
          edgeCleanups.push({ el: document, event: "mouseup", handler: onUp, opts: false });
          on(document, "touchend", onUp);
          edgeCleanups.push({ el: document, event: "touchend", handler: onUp, opts: false });

          allCleanups = allCleanups.concat(edgeCleanups);
        })(edges[i]);
      }

      win._mikiResizeCleanups = allCleanups;
    },

    cascade: function (area) {
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
    },

    tile: function (area) {
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
    },

    destroy: function (el) {
      mikiDestroy(el);
    }
  };

  window.mikiMDI = mikiMDI;
})();
