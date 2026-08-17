/*!
 * MikiUI Editor Area Runtime - VS Code-like split view with tabs
 *
 * Scoped under mikiEditorArea to avoid conflicts with miki_ui.js.
 *
 * Features:
 * - Tab switching with keyboard navigation
 * - Tab closing
 * - Drag tabs between editor groups
 * - Drag splitters to resize groups
 * - Double-click splitter to maximize/restore
 * - Arrow keys for fine adjustment
 * - Touch support
 * - Smooth resize with requestAnimationFrame
 */

(function () {
  "use strict";

  if (typeof window === "undefined") return;

  var on = function (el, event, handler, opts) {
    el.addEventListener(event, handler, opts || false);
  };

  var off = function (el, event, handler, opts) {
    el.removeEventListener(event, handler, opts || false);
  };

  var dispatch = function (el, name, detail) {
    el.dispatchEvent(
      new CustomEvent(name, { detail: detail || {}, bubbles: true, cancelable: true })
    );
  };

  /* ===================== Editor Area ===================== */

  var mikiEditorArea = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var groups = el.querySelectorAll("[data-miki-editor-group=\"true\"]");
      for (var i = 0; i < groups.length; i++) {
        mikiEditorArea.initGroup(groups[i]);
      }

      var splitters = el.querySelectorAll("[data-miki-editor-splitter=\"true\"]");
      for (var j = 0; j < splitters.length; j++) {
        mikiEditorArea.initSplitter(el, splitters[j]);
      }

      // Global drop zone for tab drag
      mikiEditorArea.initDragDrop(el);
    },

    /* ---- Group / Tabs ---- */

    initGroup: function (group) {
      var tabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
      for (var i = 0; i < tabs.length; i++) {
        (function (tab, idx) {
          // Tab click
          on(tab, "click", function (e) {
            if (e.target.closest("[data-miki-tab-close=\"true\"])) return;
            var groupId = tab.getAttribute("data-miki-tab-group");
            mikiEditorArea.showTab(groupId, idx);
          });

          // Close button
          var closeBtn = tab.querySelector("[data-miki-tab-close=\"true\"]");
          if (closeBtn) {
            on(closeBtn, "click", function (e) {
              e.preventDefault();
              e.stopPropagation();
              var groupId = tab.getAttribute("data-miki-tab-group");
              mikiEditorArea.closeTab(groupId, idx);
            });
          }

          // Keyboard navigation within tab
          on(tab, "keydown", function (e) {
            var groupEl = tab.closest("[data-miki-editor-group=\"true\"]");
            if (!groupEl) return;
            var allTabs = Array.from(groupEl.querySelectorAll("[data-miki-tab=\"true\"]"));
            var currentIndex = allTabs.indexOf(tab);
            var newIndex = currentIndex;

            if (e.key === "ArrowRight") {
              e.preventDefault();
              newIndex = (currentIndex + 1) % allTabs.length;
            } else if (e.key === "ArrowLeft") {
              e.preventDefault();
              newIndex = (currentIndex - 1 + allTabs.length) % allTabs.length;
            } else if (e.key === "Home") {
              e.preventDefault();
              newIndex = 0;
            } else if (e.key === "End") {
              e.preventDefault();
              newIndex = allTabs.length - 1;
            } else if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              var groupId = tab.getAttribute("data-miki-tab-group");
              mikiEditorArea.showTab(groupId, currentIndex);
              return;
            }

            if (newIndex !== currentIndex && allTabs[newIndex]) {
              allTabs[newIndex].focus();
              var gid = tab.getAttribute("data-miki-tab-group");
              mikiEditorArea.showTab(gid, newIndex);
            }
          });

          // Drag start for tabs
          on(tab, "dragstart", function (e) {
            tab.classList.add("miki-dragging");
            e.dataTransfer.effectAllowed = "move";
            e.dataTransfer.setData("text/plain", idx.toString());
            e.dataTransfer.setData("application/miki-tab-group", tab.getAttribute("data-miki-tab-group") || "");
            dispatch(tab, "miki:editor:tabdragstart", { tabIndex: idx, groupId: tab.getAttribute("data-miki-tab-group") });
          });

          on(tab, "dragend", function () {
            tab.classList.remove("miki-dragging");
            dispatch(tab, "miki:editor:tabdragend", {});
          });
        })(tabs[i], i);
      }
    },

    showTab: function (groupId, index) {
      var group = document.querySelector('[data-group-id="' + groupId + '"]');
      if (!group) return;

      var tabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
      var panels = group.querySelectorAll(".miki-editor-content");

      for (var i = 0; i < tabs.length; i++) {
        var isActive = i === index;
        tabs[i].classList.toggle("miki-editor-tab-active", isActive);
        tabs[i].setAttribute("aria-selected", isActive ? "true" : "false");
        tabs[i].setAttribute("tabindex", isActive ? "0" : "-1");
        if (panels[i]) {
          panels[i].classList.toggle("miki-editor-content-active", isActive);
          panels[i].hidden = !isActive;
        }
      }

      if (tabs[index]) tabs[index].focus();

      dispatch(group, "miki:editor:tabchanged", { groupId: groupId, index: index });
    },

    closeTab: function (groupId, index) {
      var group = document.querySelector('[data-group-id="' + groupId + '"]');
      if (!group) return;

      var tabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
      var panels = group.querySelectorAll(".miki-editor-content");

      if (index < 0 || index >= tabs.length) return;

      // Remove tab and panel
      if (tabs[index]) tabs[index].remove();
      if (panels[index]) panels[index].remove();

      // If we closed the active tab, activate the new last tab
      var remainingTabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
      if (remainingTabs.length > 0) {
        var newActiveIndex = Math.min(index, remainingTabs.length - 1);
        mikiEditorArea.showTab(groupId, newActiveIndex);
      }

      dispatch(group, "miki:editor:tabclosed", { groupId: groupId, index: index });
    },

    /* ---- Drag & Drop Tabs ---- */

    initDragDrop: function (editorArea) {
      var dragOverlay = null;

      function getTabFromGroup(groupId, index) {
        var group = document.querySelector('[data-group-id="' + groupId + '"]');
        if (!group) return null;
        var tabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
        return tabs[index] || null;
      }

      editorArea.addEventListener("dragover", function (e) {
        var tab = e.target.closest("[data-miki-tab=\"true\"]");
        if (!tab) return;

        var sourceGroupId = e.dataTransfer.types.indexOf("application/miki-tab-group") !== -1
          ? e.dataTransfer.getData("application/miki-tab-group")
          : null;

        if (!sourceGroupId) return;

        e.preventDefault();
        e.dataTransfer.dropEffect = "move";

        // Show drop indicator
        if (!dragOverlay) {
          dragOverlay = document.createElement("div");
          dragOverlay.className = "miki-editor-drag-overlay";
          document.body.appendChild(dragOverlay);
        }

        var rect = tab.getBoundingClientRect();
        var midX = rect.left + rect.width / 2;
        var midY = rect.top + rect.height / 2;
        var before = e.clientX < midX || (e.clientX >= midX && e.clientY < midY);

        dragOverlay.textContent = before ? "Insert before" : "Insert after";
        dragOverlay.style.left = (e.clientX + 12) + "px";
        dragOverlay.style.top = (e.clientY - 24) + "px";
        dragOverlay.classList.add("miki-visible");
      });

      editorArea.addEventListener("dragleave", function (e) {
        if (dragOverlay) {
          dragOverlay.classList.remove("miki-visible");
        }
      });

      editorArea.addEventListener("drop", function (e) {
        if (dragOverlay) {
          dragOverlay.classList.remove("miki-visible");
        }

        var sourceGroupId = e.dataTransfer.getData("application/miki-tab-group");
        var sourceIndex = parseInt(e.dataTransfer.getData("text/plain"), 10);

        if (isNaN(sourceIndex) || !sourceGroupId) return;

        var targetTab = e.target.closest("[data-miki-tab=\"true\"]");
        if (!targetTab) return;

        var targetGroupId = targetTab.getAttribute("data-miki-tab-group");
        var targetGroup = targetTab.closest("[data-miki-editor-group=\"true\"]");
        if (!targetGroup) return;

        var targetTabs = Array.from(targetGroup.querySelectorAll("[data-miki-tab=\"true\"]"));
        var targetIndex = targetTabs.indexOf(targetTab);

        var rect = targetTab.getBoundingClientRect();
        var midX = rect.left + rect.width / 2;
        var insertBefore = e.clientX < midX || (e.clientX >= midX && e.clientY < midY);
        if (insertBefore) {
          // keep targetIndex
        } else {
          targetIndex = targetIndex + 1;
        }

        // Don't do anything if dropping on itself in the same position
        if (sourceGroupId === targetGroupId && sourceIndex === targetIndex) return;

        dispatch(editorArea, "miki:editor:tabdrop", {
          sourceGroupId: sourceGroupId,
          sourceIndex: sourceIndex,
          targetGroupId: targetGroupId,
          targetIndex: targetIndex,
        });

        e.preventDefault();
      });
    },

    /* ---- Splitter ---- */

    initSplitter: function (editorArea, splitter) {
      var firstPane = splitter.previousElementSibling;
      var secondPane = splitter.nextElementSibling;
      if (!firstPane || !secondPane) return;

      var orientation = editorArea.getAttribute("data-orientation") || "horizontal";
      var minSize = parseInt(editorArea.getAttribute("data-min-size") || "150", 10);
      var isHorizontal = orientation === "horizontal";

      var dragging = false;
      var rafId = null;
      var pendingSize = null;

      // Cached at drag start to avoid repeated layout reads
      var startPos = 0;
      var firstStartSize = 0;
      var secondStartSize = 0;
      var containerSize = 0;
      var splitterSize = 0;

      function getPx(el, axis) {
        if (axis === "x") return el.offsetWidth;
        return el.offsetHeight;
      }

      function setPx(el, size, axis) {
        if (axis === "x") {
          el.style.width = size + "px";
          el.style.height = "";
        } else {
          el.style.height = size + "px";
          el.style.width = "";
        }
        el.style.flex = "none";
        el.style.flexBasis = "";
      }

      function resetPx(el, axis) {
        if (axis === "x") {
          el.style.width = "";
        } else {
          el.style.height = "";
        }
        el.style.flex = "";
        el.style.flexBasis = "";
      }

      function applySizes(firstSize, secondSize) {
        setPx(firstPane, firstSize, isHorizontal ? "x" : "y");
        setPx(secondPane, secondSize, isHorizontal ? "x" : "y");
      }

      function resetSizes() {
        resetPx(firstPane, isHorizontal ? "x" : "y");
        resetPx(secondPane, isHorizontal ? "x" : "y");
      }

      function computeMaxFirst() {
        return Math.max(minSize, containerSize - splitterSize - minSize);
      }

      function onDragStart(pos) {
        dragging = true;
        startPos = pos;
        firstStartSize = getPx(firstPane, isHorizontal ? "x" : "y");
        secondStartSize = getPx(secondPane, isHorizontal ? "x" : "y");
        containerSize = getPx(editorArea, isHorizontal ? "x" : "y");
        splitterSize = getPx(splitter, isHorizontal ? "x" : "y");
        splitter.classList.add("miki-splitter-dragging");
        editorArea.classList.add("miki-split-dragging");
        document.body.style.cursor = isHorizontal ? "col-resize" : "row-resize";
        document.body.style.userSelect = "none";

        on(document, "mousemove", onMouseMove);
        on(document, "mouseup", onMouseUp);
        on(document, "mouseleave", onMouseUp);
        on(document, "touchmove", onTouchMove, { passive: false });
        on(document, "touchend", onTouchEnd);
      }

      function onDragMove(pos) {
        if (!dragging) return;
        var delta = pos - startPos;
        var maxFirst = computeMaxFirst();
        var newFirst = Math.max(minSize, Math.min(maxFirst, firstStartSize + delta));
        var newSecond = Math.max(minSize, containerSize - splitterSize - newFirst);

        pendingSize = { first: newFirst, second: newSecond };

        if (!rafId) {
          rafId = requestAnimationFrame(function () {
            if (pendingSize) {
              applySizes(pendingSize.first, pendingSize.second);
              dispatch(editorArea, "miki:editor:resize", {
                orientation: orientation,
                firstSize: pendingSize.first,
              });
              pendingSize = null;
            }
            rafId = null;
          });
        }
      }

      function onDragEnd() {
        dragging = false;
        splitter.classList.remove("miki-splitter-dragging");
        editorArea.classList.remove("miki-split-dragging");
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
        resetSizes();

        if (rafId) {
          cancelAnimationFrame(rafId);
          rafId = null;
          pendingSize = null;
        }

        off(document, "mousemove", onMouseMove);
        off(document, "mouseup", onMouseUp);
        off(document, "mouseleave", onMouseUp);
        off(document, "touchmove", onTouchMove);
        off(document, "touchend", onTouchEnd);
      }

      function onMouseMove(e) {
        if (!dragging) return;
        e.preventDefault();
        var pos = isHorizontal ? e.clientX : e.clientY;
        onDragMove(pos);
      }

      function onMouseUp() {
        onDragEnd();
      }

      function onTouchMove(e) {
        if (!dragging) return;
        e.preventDefault();
        var touch = e.touches[0];
        var pos = isHorizontal ? touch.clientX : touch.clientY;
        onDragMove(pos);
      }

      function onTouchEnd() {
        onDragEnd();
      }

      on(splitter, "mousedown", function (e) {
        if (e.button !== 0) return;
        e.preventDefault();
        var pos = isHorizontal ? e.clientX : e.clientY;
        onDragStart(pos);
      });

      on(splitter, "touchstart", function (e) {
        if (e.touches.length !== 1) return;
        e.preventDefault();
        var touch = e.touches[0];
        var pos = isHorizontal ? touch.clientX : touch.clientY;
        onDragStart(pos);
      }, { passive: false });

      // Double-click to maximize/restore
      on(splitter, "dblclick", function () {
        if (editorArea.classList.contains("miki-split-maximized")) {
          editorArea.classList.remove("miki-split-maximized");
          resetSizes();
        } else {
          editorArea.classList.add("miki-split-maximized");
          var maxSize = computeMaxFirst();
          applySizes(maxSize, containerSize - splitterSize - maxSize);
        }

        dispatch(editorArea, "miki:editor:maximized", {
          maximized: editorArea.classList.contains("miki-split-maximized"),
        });
      });

      // Keyboard support
      on(splitter, "keydown", function (e) {
        var step = e.shiftKey ? 1 : 5;
        var currentSize = getPx(firstPane, isHorizontal ? "x" : "y");
        var maxFirst = computeMaxFirst();

        if (isHorizontal) {
          if (e.key === "ArrowLeft") {
            e.preventDefault();
            var newFirst = Math.max(minSize, currentSize - step);
            applySizes(newFirst, containerSize - splitterSize - newFirst);
          } else if (e.key === "ArrowRight") {
            e.preventDefault();
            var newFirst = Math.min(maxFirst, currentSize + step);
            applySizes(newFirst, containerSize - splitterSize - newFirst);
          }
        } else {
          if (e.key === "ArrowUp") {
            e.preventDefault();
            var newFirst = Math.max(minSize, currentSize - step);
            applySizes(newFirst, containerSize - splitterSize - newFirst);
          } else if (e.key === "ArrowDown") {
            e.preventDefault();
            var newFirst = Math.min(maxFirst, currentSize + step);
            applySizes(newFirst, containerSize - splitterSize - newFirst);
          }
        }
      });
    },
  };

  window.mikiEditorArea = mikiEditorArea;

  /* ===================== Auto-init ===================== */

  var widgetRegistry = window.widgetRegistry || [];

  // Register editor area widget
  widgetRegistry.push({
    selector: "[data-miki-editor-area=\"true\"]",
    init: mikiEditorArea.init,
    name: "editorArea",
  });

  if (!window.widgetRegistry) {
    window.widgetRegistry = widgetRegistry;
  }

})();
