(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiSplitView = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var splitter = el.querySelector('[data-miki-splitter="true"]');
      if (!splitter) return;

      var firstPane = el.querySelector('[data-miki-split-pane="first"]');
      var secondPane = el.querySelector('[data-miki-split-pane="second"]');
      if (!firstPane || !secondPane) return;

      var orientation = el.getAttribute("data-orientation") || "horizontal";
      var resizeMode = el.getAttribute("data-resize-mode") || "horizontal";
      var minSize = parseInt(el.getAttribute("data-min-size") || "50", 10);
      // Threshold (px) to detect first meaningful movement in 'both' mode.
      var splitThreshold = parseInt(el.getAttribute("data-split-threshold") || "5", 10);
      // Optional persistence key for layout saving/loading
      var persistKey = el.getAttribute("data-miki-persist-key") || null;

      // Determine which axes are active based on resize_mode
      var canDragX = (resizeMode === "horizontal" || resizeMode === "both");
      var canDragY = (resizeMode === "vertical" || resizeMode === "both");

      // Default drag axis: horizontal orientation → X-axis, vertical → Y-axis
      var dragAxis = (orientation === "horizontal") ? "x" : "y";
      if (resizeMode === "horizontal") dragAxis = "x";
      if (resizeMode === "vertical") dragAxis = "y";

      var dragging = false;
      var startPosX = 0, startPosY = 0;
      var startSizeFirstX = 0, startSizeFirstY = 0;
      var dragStarted = false;

      function resetFlexBasis() {
        firstPane.style.flexBasis = "";
        secondPane.style.flexBasis = "";
        firstPane.style.flex = "";
        secondPane.style.flex = "";
      }

      function getDims() {
        return {
          containerW: el.offsetWidth,
          containerH: el.offsetHeight,
          splitterW: splitter.offsetWidth,
          splitterH: splitter.offsetHeight
        };
      }

      function applySize(primarySize, axis) {
        firstPane.style.flexBasis = primarySize + "px";
        firstPane.style.flex = "none";
        secondPane.style.flexBasis = "auto";
        secondPane.style.flex = "1 1 0";
      }

      function onMouseMove(e) {
        if (!dragging) return;
        e.preventDefault();

        var mouseX = e.clientX;
        var mouseY = e.clientY;

        // For 'both' mode: determine axis on first meaningful movement (5px threshold)
        if (resizeMode === "both" && !dragStarted) {
          var deltaX0 = Math.abs(mouseX - startPosX);
          var deltaY0 = Math.abs(mouseY - startPosY);
          if (deltaX0 > splitThreshold || deltaY0 > splitThreshold) {
            dragAxis = deltaX0 >= deltaY0 ? "x" : "y";
            dragStarted = true;
          }
        }

        if (dragAxis === "x" && canDragX) {
          var deltaX = mouseX - startPosX;
          var newSizeX = startSizeFirstX + deltaX;
          var dims = getDims();
          var maxW = dims.containerW - dims.splitterW - minSize;
          newSizeX = Math.max(minSize, Math.min(maxW, newSizeX));
          applySize(newSizeX, "x");
        } else if (dragAxis === "y" && canDragY) {
          var deltaY = mouseY - startPosY;
          var newSizeY = startSizeFirstY + deltaY;
          var dims2 = getDims();
          var maxH = dims2.containerH - dims2.splitterH - minSize;
          newSizeY = Math.max(minSize, Math.min(maxH, newSizeY));
          applySize(newSizeY, "y");
        }

        dispatch(el, "miki:splitview:resize", {
          orientation: orientation,
          resizeMode: resizeMode,
          axis: dragAxis
        });
      }

      function onMouseUp() {
        dragging = false;
        dragStarted = false;
        splitter.classList.remove("miki-splitter-dragging");
        splitter.style.cursor = "";
        resetFlexBasis();
        off(document, "mousemove", onMouseMove);
        off(document, "mouseup", onMouseUp);
        // Persist layout if requested
        try {
          if (persistKey && window.localStorage && window.mikiSplitView && typeof window.mikiSplitView.getLayout === 'function') {
            var layout = window.mikiSplitView.getLayout(el);
            localStorage.setItem(persistKey, JSON.stringify(layout));
          }
        } catch (err) {
          /* ignore storage errors */
        }
      }

      on(splitter, "mousedown", function (e) {
        if (e.button !== 0) return;
        e.preventDefault();

        dragging = true;
        startPosX = e.clientX;
        startPosY = e.clientY;
        startSizeFirstX = firstPane.offsetWidth;
        startSizeFirstY = firstPane.offsetHeight;
        splitter.classList.add("miki-splitter-dragging");
        on(document, "mousemove", onMouseMove, { passive: false });
        on(document, "mouseup", onMouseUp);
      });

      // Double-click to maximize/restore
      on(splitter, "dblclick", function () {
        if (el.classList.contains("miki-split-maximized")) {
          el.classList.remove("miki-split-maximized");
          resetFlexBasis();
        } else {
          el.classList.add("miki-split-maximized");
          var dims = getDims();
          var activeAxis = (orientation === "horizontal") ? "x" : "y";
          if (activeAxis === "x") {
            firstPane.style.flexBasis = (dims.containerW - dims.splitterW) + "px";
            firstPane.style.flex = "none";
            secondPane.style.flexBasis = "auto";
            secondPane.style.flex = "1 1 0";
          } else {
            firstPane.style.flexBasis = (dims.containerH - dims.splitterH) + "px";
            firstPane.style.flex = "none";
            secondPane.style.flexBasis = "auto";
            secondPane.style.flex = "1 1 0";
          }
        }
        dispatch(el, "miki:splitview:maximized", { maximized: el.classList.contains("miki-split-maximized") });
      });

      // Keyboard support (arrow keys adjust by 5px)
      on(splitter, "keydown", function (e) {
        var step = e.shiftKey ? 1 : 5;
        var dims = getDims();
        var activeAxis = (orientation === "horizontal") ? "x" : "y";

        if (activeAxis === "x" && canDragX) {
          var currentSize = firstPane.offsetWidth;
          var maxSize = dims.containerW - dims.splitterW - minSize;
          if (e.key === "ArrowLeft") {
            e.preventDefault();
            var newW = Math.max(minSize, currentSize - step);
            firstPane.style.flexBasis = newW + "px";
            firstPane.style.flex = "none";
            secondPane.style.flexBasis = "auto";
            secondPane.style.flex = "1 1 0";
          } else if (e.key === "ArrowRight") {
            e.preventDefault();
            var newW2 = Math.min(maxSize, currentSize + step);
            firstPane.style.flexBasis = newW2 + "px";
            firstPane.style.flex = "none";
            secondPane.style.flexBasis = "auto";
            secondPane.style.flex = "1 1 0";
          }
        } else if (activeAxis === "y" && canDragY) {
          var currentSize = firstPane.offsetHeight;
          var maxSize = dims.containerH - dims.splitterH - minSize;
          if (e.key === "ArrowUp") {
            e.preventDefault();
            var newH = Math.max(minSize, currentSize - step);
            firstPane.style.flexBasis = newH + "px";
            firstPane.style.flex = "none";
            secondPane.style.flexBasis = "auto";
            secondPane.style.flex = "1 1 0";
          } else if (e.key === "ArrowDown") {
            e.preventDefault();
            var newH2 = Math.min(maxSize, currentSize + step);
            firstPane.style.flexBasis = newH2 + "px";
            firstPane.style.flex = "none";
            secondPane.style.flexBasis = "auto";
            secondPane.style.flex = "1 1 0";
          }
        }
      });

      // Touch support
      on(splitter, "touchstart", function (e) {
        if (e.touches.length !== 1) return;
        e.preventDefault();
        dragStarted = false;
        dragging = true;
        startPosX = e.touches[0].clientX;
        startPosY = e.touches[0].clientY;
        startSizeFirstX = firstPane.offsetWidth;
        startSizeFirstY = firstPane.offsetHeight;
        splitter.classList.add("miki-splitter-dragging");
      }, { passive: false });

      on(document, "touchmove", onMouseMove, { passive: false });
      on(document, "touchend", onMouseUp);
    },

    // Get layout state as a serializable object
    getLayout: function (el) {
      var data = [];
      var panes = el.querySelectorAll('[data-miki-split-pane]');
      for (var i = 0; i < panes.length; i++) {
        var pane = panes[i];
        var size = pane.dataset.mikiSize || pane.style.flexBasis || "";
        data.push({
          id: pane.id || "",
          size: size,
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

    // Apply layout from a saved state object
    setLayout: function (el, layout) {
      if (!layout) return;
      el.setAttribute("data-orientation", layout.orientation || "horizontal");
      el.setAttribute("data-resize-mode", layout.resizeMode || "horizontal");
      el.setAttribute("data-min-size", String(layout.minSize || 50));

      var panes = el.querySelectorAll('[data-miki-split-pane]');
      for (var i = 0; i < panes.length; i++) {
        if (i >= layout.panes.length) break;
        var pane = panes[i];
        var state = layout.panes[i];
        if (state.size) {
          pane.style.flexBasis = state.size;
          pane.style.flex = "none";
        }
        if (state.collapsed) {
          pane.classList.add("miki-split-pane-collapsed");
        } else {
          pane.classList.remove("miki-split-pane-collapsed");
        }
        if (state.id) pane.id = state.id;
      }

      // Re-init to pick up new attributes
      if (el.dataset.mikiInit === "true") {
        el.dataset.mikiInit = "";
        mikiSplitView.init(el);
      }
      // If a persisted layout exists, apply it (after re-init)</br>
      try {
        if (persistKey && window.localStorage) {
          var stored = localStorage.getItem(persistKey);
          if (stored) {
            var parsed = JSON.parse(stored);
            if (parsed) {
              // apply stored layout
              if (el.dataset.mikiInit === "true") {
                el.dataset.mikiInit = "";
              }
              window.mikiSplitView.setLayout(el, parsed);
            }
          }
        }
      } catch (err) {
        /* ignore storage / parse errors */
      }
    },

    // Add a new pane (inserts before the splitter)
    addPane: function (el, contentHtml, position) {
      var splitter = el.querySelector('[data-miki-splitter="true"]');
      if (!splitter) return;
      var firstPane = el.querySelector('[data-miki-split-pane="first"]');
      if (!firstPane) return;

      var newPane = document.createElement("div");
      newPane.className = "miki-split-pane";
      newPane.setAttribute("data-miki-split-pane", "second");
      newPane.setAttribute("role", "region");
      newPane.innerHTML = contentHtml;
      newPane.style.flex = "1 1 0";

      // Insert new pane + splitter before second pane
      var secondPane = el.querySelector('[data-miki-split-pane="second"]');
      if (position === "before-first" || !secondPane) {
        el.insertBefore(newPane, firstPane);
        var newSplitter = splitter.cloneNode(false);
        newSplitter.setAttribute("data-miki-splitter", "true");
        el.insertBefore(newSplitter, firstPane);
      } else {
        // Replace second pane position
        var newSplitter2 = splitter.cloneNode(false);
        newSplitter2.setAttribute("data-miki-splitter", "true");
        el.insertBefore(newPane, splitter);
        el.insertBefore(newSplitter2, secondPane);
      }

      // Re-init
      el.dataset.mikiInit = "";
      mikiSplitView.init(el);
    },

    // Remove a pane by index (0 = first, 1 = second)
    removePane: function (el, index) {
      var panes = el.querySelectorAll('[data-miki-split-pane]');
      if (index < 0 || index >= panes.length) return;
      var pane = panes[index];
      var splitter = pane.nextElementSibling;
      if (splitter && splitter.hasAttribute("data-miki-splitter")) {
        splitter.remove();
      } else {
        splitter = pane.previousElementSibling;
        if (splitter && splitter.hasAttribute("data-miki-splitter")) {
          splitter.remove();
        }
      }
      pane.remove();
      el.dataset.mikiInit = "";
      mikiSplitView.init(el);
    }
  };

  window.mikiSplitView = mikiSplitView;
})();
