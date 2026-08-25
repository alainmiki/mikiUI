(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiSplitView = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var splitter = el.querySelector(':scope > [data-miki-splitter="true"]');
      if (!splitter) return;

      var firstPane = el.querySelector(':scope > [data-miki-split-pane="first"]');
      var secondPane = el.querySelector(':scope > [data-miki-split-pane="second"]');
      if (!firstPane || !secondPane) return;

      var orientation = el.getAttribute("data-orientation") || "horizontal";
      var resizeMode = el.getAttribute("data-resize-mode") || "horizontal";
      var minSize = parseInt(el.getAttribute("data-min-size") || "50", 10);
      var splitThreshold = parseInt(el.getAttribute("data-split-threshold") || "5", 10);
      var persistKey = el.getAttribute("data-miki-persist-key") || null;
       var splitterWidth = parseInt(splitter.getAttribute("data-splitter-width") || "8", 10);

      var isHorizontal = orientation === "horizontal";
      var canDragX = (resizeMode === "horizontal" || resizeMode === "both");
      var canDragY = (resizeMode === "vertical" || resizeMode === "both");
      var dragAxis = resizeMode === "horizontal" ? "x" : (resizeMode === "vertical" ? "y" : (isHorizontal ? "x" : "y"));

      var dragging = false;
      var startPosX = 0, startPosY = 0;
      var startSizeFirstX = 0, startSizeFirstY = 0;
      var dragStarted = false;
      var activeDragAxis = dragAxis;

      /* Guard: only call preventDefault when the event is cancelable to
         avoid browser "Ignored attempt to cancel a touch event" warnings. */
      function safePrevent(e) {
        if (e && e.cancelable) {
          e.preventDefault();
        }
      }

      /* Normalize coordinates from mouse or touch event */
      function coords(e) {
        var p = (window.miki && miki.eventPoint) ? miki.eventPoint(e)
               : (e.touches && e.touches[0]) ? { x: e.touches[0].clientX, y: e.touches[0].clientY }
               : (e.changedTouches && e.changedTouches[0]) ? { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY }
               : { x: e.clientX || 0, y: e.clientY || 0 };
        return p;
      }

      function dims() {
        return {
          cw: el.offsetWidth,
          ch: el.offsetHeight,
          sw: splitter.offsetWidth,
          sh: splitter.offsetHeight
        };
      }

      function setPaneSize(px, axis) {
        firstPane.style.flex = "none";
        firstPane.style.flexBasis = px + "px";
        secondPane.style.flex = "1 1 0";
        secondPane.style.flexBasis = "auto";
      }

      function clearInlineFlex() {
        [firstPane, secondPane].forEach(function(pane) {
          pane.style.removeProperty("flex");
          pane.style.removeProperty("flex-basis");
          pane.style.removeProperty("flex-grow");
          pane.style.removeProperty("flex-shrink");
        });
      }

      function onMove(e) {
        if (!dragging) return;

        var p = coords(e);
        var dx = p.x - startPosX;
        var dy = p.y - startPosY;

        /* For 'both' mode: lock axis on first meaningful movement */
        if (resizeMode === "both" && !dragStarted) {
          if (Math.abs(dx) > splitThreshold || Math.abs(dy) > splitThreshold) {
            activeDragAxis = Math.abs(dx) >= Math.abs(dy) ? "x" : "y";
            dragStarted = true;
          }
        }

        if (activeDragAxis === "x" && canDragX) {
          var d = dims();
          var maxW = d.cw - d.sw - minSize;
          var newW = Math.max(minSize, Math.min(maxW, startSizeFirstX + dx));
          setPaneSize(newW, "x");
        } else if (activeDragAxis === "y" && canDragY) {
          var d2 = dims();
          var maxH = d2.ch - d2.sh - minSize;
          var newH = Math.max(minSize, Math.min(maxH, startSizeFirstY + dy));
          setPaneSize(newH, "y");
        }

        dispatch(el, "miki:splitview:resize", {
          orientation: orientation,
          resizeMode: resizeMode,
          axis: activeDragAxis
        });
      }

      function onEnd() {
         if (!dragging) return;
         dragging = false;
         dragStarted = false;
         activeDragAxis = dragAxis;
         splitter.classList.remove("miki-splitter-dragging");
         splitter.style.cursor = "";

         /* Remove all possible event listeners (some may not have been bound) */
        off(document, "pointermove", onMove);
        off(document, "pointerup", onEnd);
        off(document, "mousemove", onMove);
        off(document, "mouseup", onEnd);
        off(document, "touchmove", onMove);
        off(document, "touchend", onEnd);

        /* Persist layout if requested */
        try {
          if (persistKey && window.localStorage && window.mikiSplitView && typeof window.mikiSplitView.getLayout === "function") {
            var layout = window.mikiSplitView.getLayout(el);
            localStorage.setItem(persistKey, JSON.stringify(layout));
          }
        } catch (err) {
          /* ignore storage errors */
        }
      }

      function onStart(e) {
        /* Prevent double-init from pointerdown + mousedown firing together */
        if (dragging) return;
        /* Left-click only; ignore right-click/middle-click */
        if (e.button !== undefined && e.button !== 0) return;
        /* Ignore if not primary touch/mouse */
        if (e.pointerType === "touch" && e.isPrimary === false) return;
        safePrevent(e);

        dragging = true;
        dragStarted = false;
        activeDragAxis = dragAxis;
        var p = coords(e);
        startPosX = p.x;
        startPosY = p.y;
        startSizeFirstX = firstPane.offsetWidth;
        startSizeFirstY = firstPane.offsetHeight;
        splitter.classList.add("miki-splitter-dragging");

        /* Bind ALL event types so we work with pointer, mouse, and touch.
           The onStart guard prevents double-init from pointerdown + mousedown. */
        on(document, "pointermove", onMove, { passive: false });
        on(document, "pointerup", onEnd);
        on(document, "mousemove", onMove, { passive: false });
        on(document, "mouseup", onEnd);
        on(document, "touchmove", onMove, { passive: false });
        on(document, "touchend", onEnd);
      }

      /* Mouse down / touch start / pointer down — unified handler.
         When PointerEvent is available, prefer pointer events but also
         bind mousedown as a fallback (Playwright mouse actions may not
         always fire pointerdown in headless mode). The onStart guard
         prevents double-binding. */
       on(splitter, "mousedown", onStart);
      on(splitter, "touchstart", onStart, { passive: false });
      if (window.PointerEvent) {
        on(splitter, "pointerdown", onStart, { passive: false });
      }

      /* Double-click to maximize/restore the first pane */
      on(splitter, "dblclick", function () {
        if (el.classList.contains("miki-split-maximized")) {
          el.classList.remove("miki-split-maximized");
          clearInlineFlex();
        } else {
          el.classList.add("miki-split-maximized");
          var d = dims();
          if (isHorizontal) {
            firstPane.style.flex = "none";
            firstPane.style.flexBasis = (d.cw - d.sw) + "px";
          } else {
            firstPane.style.flex = "none";
            firstPane.style.flexBasis = (d.ch - d.sh) + "px";
          }
          secondPane.style.flex = "1 1 0";
          secondPane.style.flexBasis = "auto";
        }
        dispatch(el, "miki:splitview:maximized", {
          maximized: el.classList.contains("miki-split-maximized")
        });
      });

      /* Keyboard: arrow keys for fine adjustment */
      on(splitter, "keydown", function (e) {
        var step = e.shiftKey ? 1 : 5;
        var d = dims();
        var activeAxis = (orientation === "horizontal") ? "x" : "y";

        if (activeAxis === "x" && canDragX) {
          var currentW = firstPane.offsetWidth;
          var maxW = d.cw - d.sw - minSize;
          if (e.key === "ArrowLeft") {
            safePrevent(e);
            setPaneSize(Math.max(minSize, currentW - step), "x");
          } else if (e.key === "ArrowRight") {
            safePrevent(e);
            setPaneSize(Math.min(maxW, currentW + step), "x");
          }
        } else if (activeAxis === "y" && canDragY) {
          var currentH = firstPane.offsetHeight;
          var maxH = d.ch - d.sh - minSize;
          if (e.key === "ArrowUp") {
            safePrevent(e);
            setPaneSize(Math.max(minSize, currentH - step), "y");
          } else if (e.key === "ArrowDown") {
            safePrevent(e);
            setPaneSize(Math.min(maxH, currentH + step), "y");
          }
        }
      });

      /* Make splitter focusable for keyboard + screen readers */
      splitter.setAttribute("tabindex", "0");
      splitter.setAttribute("role", "separator");
      if (!splitter.getAttribute("aria-label")) {
        splitter.setAttribute("aria-label", "Resize panes");
      }
      splitter.setAttribute("aria-orientation", isHorizontal ? "horizontal" : "vertical");
    },

     getLayout: function (el) {
       var data = [];
       var panes = el.querySelectorAll(':scope > [data-miki-split-pane]');
      for (var i = 0; i < panes.length; i++) {
        var pane = panes[i];
        data.push({
          id: pane.id || "",
          size: pane.dataset.mikiSize || pane.style.flexBasis || "",
          collapsed: pane.classList.contains("miki-split-pane-collapsed")
        });
      }
      return {
        orientation: el.getAttribute("data-orientation") || "horizontal",
        resizeMode: el.getAttribute("data-resize-mode") || "horizontal",
        minSize: parseInt(el.getAttribute("data-min-size") || "50", 10),
        panes: data
      };
    },

    setLayout: function (el, layout) {
      if (!layout) return;
      el.setAttribute("data-orientation", layout.orientation || "horizontal");
      el.setAttribute("data-resize-mode", layout.resizeMode || "horizontal");
      el.setAttribute("data-min-size", String(layout.minSize || 50));

      var panes = el.querySelectorAll(':scope > [data-miki-split-pane]');
      for (var i = 0; i < layout.panes.length && i < panes.length; i++) {
        var pane = panes[i];
        var state = layout.panes[i];
        if (state.size) {
          pane.style.flex = "none";
          pane.style.flexBasis = state.size;
        }
        pane.classList.toggle("miki-split-pane-collapsed", !!state.collapsed);
        if (state.id) pane.id = state.id;
      }

      el.dataset.mikiInit = "";
      mikiSplitView.init(el);
    },

    addPane: function (el, contentHtml) {
       var splitter = el.querySelector(':scope > [data-miki-splitter="true"]');
      if (!splitter) return;

      var newPane = document.createElement("div");
      newPane.className = "miki-split-pane miki-split-second";
      newPane.setAttribute("data-miki-split-pane", "second");
      newPane.setAttribute("role", "region");
      newPane.innerHTML = contentHtml;
      newPane.style.flex = "1 1 0";

       var oldSecond = el.querySelector(':scope > [data-miki-split-pane="second"]');
      if (oldSecond) {
        oldSecond.setAttribute("data-miki-split-pane", "third");
        var newSplitter = splitter.cloneNode(false);
        newSplitter.setAttribute("data-miki-splitter", "true");
        el.insertBefore(newSplitter, oldSecond);
        el.insertBefore(newPane, oldSecond);
      }

      el.dataset.mikiInit = "";
      mikiSplitView.init(el);
    },

    removePane: function (el, index) {
       var panes = el.querySelectorAll(':scope > [data-miki-split-pane]');
       if (index < 0 || index >= panes.length) return;
      var pane = panes[index];
      var splitter = pane.nextElementSibling;
      if (splitter && splitter.hasAttribute("data-miki-splitter")) {
        splitter.remove();
      }
      pane.remove();
      el.dataset.mikiInit = "";
      mikiSplitView.init(el);
    }
  };

  window.mikiSplitView = mikiSplitView;
})();
