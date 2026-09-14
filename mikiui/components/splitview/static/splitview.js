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

    openFile: function (groupId, label, content, icon) {
      var group = document.querySelector('[data-group-id="' + groupId + '"]');
      if (!group) return null;

      var tabbar = group.querySelector(".miki-editor-tabbar");
      var container = group.querySelector(".miki-editor-content-container");
      if (!tabbar || !container) return null;

      var tabs = tabbar.querySelectorAll("[data-miki-tab=\"true\"]");
      var newIndex = tabs.length;

      var tabId = groupId + "-tab-" + newIndex;
      var panelId = groupId + "-panel-" + newIndex;

      var tabContentParts = [];
      if (icon) {
        tabContentParts.push('<span class="miki-editor-tab-icon">' + icon + '</span>');
      }
      tabContentParts.push(label);

      var closeBtn = '<button type="button" class="miki-editor-tab-close" role="button" aria-label="Close tab" data-miki-tab-close="true" data-miki-tab-group="' + groupId + '" data-miki-tab-index="' + newIndex + '">×</button>';
      tabContentParts.push(closeBtn);

      var tabHtml = '<div class="miki-editor-tab" role="tab" id="' + tabId + '" aria-selected="true" aria-controls="' + panelId + '" tabindex="0" data-miki-tab="true" data-miki-tab-group="' + groupId + '" data-miki-tab-index="' + newIndex + '">' + tabContentParts.join("") + '</div>';

      var panelHtml = '<div class="miki-editor-content miki-editor-content-active" id="' + panelId + '">' + content + '</div>';

      tabbar.insertAdjacentHTML("beforeend", tabHtml);
      container.insertAdjacentHTML("beforeend", panelHtml);

      var newTab = tabbar.querySelector('[data-miki-tab-index="' + newIndex + '"]');
      if (newTab) {
        mikiEditorArea._bindTabEvents(newTab, newIndex);
      }

      mikiEditorArea.showTab(groupId, newIndex, true);
      dispatch(group, "miki:editor:fileopened", { groupId: groupId, index: newIndex, label: label });

      return newIndex;
    },

    _bindTabEvents: function (tab, idx) {
      on(tab, "click", function (e) {
        if (e.target.closest('[data-miki-tab-close="true"]')) return;
        var groupId = tab.getAttribute("data-miki-tab-group");
        mikiEditorArea.showTab(groupId, parseInt(tab.getAttribute("data-miki-tab-index") || String(idx), 10));
      });

      var closeBtn = tab.querySelector('[data-miki-tab-close="true"]');
      if (closeBtn) {
        on(closeBtn, "click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          var groupId = tab.getAttribute("data-miki-tab-group");
          mikiEditorArea.closeTab(groupId, parseInt(tab.getAttribute("data-miki-tab-index") || String(idx), 10));
        });
      }

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
    },

    /* ---- Group / Tabs ---- */

    initGroup: function (group) {
      var tabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
      for (var i = 0; i < tabs.length; i++) {
        (function (tab, idx) {
          function getCurrentIndex() {
            return parseInt(tab.getAttribute("data-miki-tab-index") || String(idx), 10);
          }

          // Tab click
          on(tab, "click", function (e) {
            if (e.target.closest('[data-miki-tab-close="true"]')) return;
            var groupId = tab.getAttribute("data-miki-tab-group");
            mikiEditorArea.showTab(groupId, getCurrentIndex());
          });

          // Close button
          var closeBtn = tab.querySelector('[data-miki-tab-close="true"]');
          if (closeBtn) {
            on(closeBtn, "click", function (e) {
              e.preventDefault();
              e.stopPropagation();
              var groupId = tab.getAttribute("data-miki-tab-group");
              mikiEditorArea.closeTab(groupId, getCurrentIndex());
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
        })(tabs[i], i);
      }
    },

    showTab: function (groupId, index, focus) {
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

      if (focus && tabs[index]) tabs[index].focus();

      dispatch(group, "miki:editor:tabchanged", { groupId: groupId, index: index });
    },

    closeTab: function (groupId, index) {
      var group = document.querySelector('[data-group-id="' + groupId + '"]');
      if (!group) return;

      var tabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
      var panels = group.querySelectorAll(".miki-editor-content");

      if (index < 0 || index >= tabs.length) return;

      // Remember which tab was active before removal
      var wasActive = tabs[index] && tabs[index].classList.contains("miki-editor-tab-active");

      // Remove tab and panel
      if (tabs[index]) tabs[index].remove();
      if (panels[index]) panels[index].remove();

      // Re-index remaining tabs
      mikiEditorArea._reindexGroup(group);

      // Activate a neighbor if we removed the active tab
      var remainingTabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
      if (remainingTabs.length > 0 && wasActive) {
        var newActiveIndex = Math.min(index, remainingTabs.length - 1);
        mikiEditorArea.showTab(groupId, newActiveIndex);
      }

      dispatch(group, "miki:editor:tabclosed", { groupId: groupId, index: index });
    },

    _reindexGroup: function (group) {
      var gid = group.getAttribute("data-group-id");
      var tabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
      for (var i = 0; i < tabs.length; i++) {
        tabs[i].setAttribute("data-miki-tab-index", String(i));
        tabs[i].id = gid + "-tab-" + i;
        var closeBtn = tabs[i].querySelector("[data-miki-tab-close=\"true\"]");
        if (closeBtn) {
          closeBtn.setAttribute("data-miki-tab-index", String(i));
        }
      }
      var panels = group.querySelectorAll(".miki-editor-content");
      for (var j = 0; j < panels.length; j++) {
        panels[j].id = gid + "-panel-" + j;
      }
    },

    /* ---- Drag & Drop Tabs ---- */

    initDragDrop: function (editorArea) {
      var DRAG_THRESHOLD = 4;
      var HOLD_DELAY = 180;
      var pointerId = null;
      var startX = 0;
      var startY = 0;
      var startTime = 0;
      var dragTab = null;
      var dragGroupId = null;
      var dragIndex = null;
      var dragging = false;
      var ghost = null;
      var dropIndicator = null;
      var holdTimer = null;
      var rafId = null;

      function getAllEditorAreas() {
        return Array.from(document.querySelectorAll('[data-miki-editor-area="true"]'));
      }

      function getTabGroup(tab) {
        return tab.closest('[data-miki-editor-group="true"]');
      }

      function getGroupId(group) {
        return group.getAttribute("data-group-id");
      }

      function getTabIndex(tab) {
        return parseInt(tab.getAttribute("data-miki-tab-index") || "0", 10);
      }

      function createGhost(tab) {
        var g = document.createElement("div");
        g.className = "miki-editor-drag-ghost";
        g.textContent = tab.textContent.trim();
        g.style.width = tab.offsetWidth + "px";
        document.body.appendChild(g);
        return g;
      }

      function createDropIndicator() {
        var d = document.createElement("div");
        d.className = "miki-editor-drop-indicator";
        document.body.appendChild(d);
        return d;
      }

      function positionGhost(e) {
        if (!ghost) return;
        ghost.style.left = (e.clientX - ghost.offsetWidth / 2) + "px";
        ghost.style.top = (e.clientY - 12) + "px";
      }

      function showDropIndicator(targetTab, before) {
        if (!dropIndicator) dropIndicator = createDropIndicator();
        var rect = targetTab.getBoundingClientRect();
        if (before) {
          dropIndicator.style.left = rect.left + "px";
          dropIndicator.style.width = "2px";
        } else {
          dropIndicator.style.left = (rect.left + rect.width) + "px";
          dropIndicator.style.width = "2px";
        }
        dropIndicator.style.top = rect.top + "px";
        dropIndicator.style.height = rect.height + "px";
        dropIndicator.classList.add("miki-visible");
      }

      function hideDropIndicator() {
        if (dropIndicator) dropIndicator.classList.remove("miki-visible");
      }

      function getDropTarget(x, y) {
        var areas = getAllEditorAreas();
        var prevDisplay = ghost ? ghost.style.display : "";
        if (ghost) ghost.style.display = "none";
        var result = null;
        for (var a = 0; a < areas.length; a++) {
          var area = areas[a];
          var rect = area.getBoundingClientRect();
          if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
            var tab = document.elementFromPoint(x, y);
            if (tab) {
              var editorTab = tab.closest("[data-miki-tab=\"true\"]");
              if (editorTab) {
                result = editorTab;
                break;
              }
            }
          }
        }
        if (ghost) ghost.style.display = prevDisplay;
        return result;
      }

      function moveTab(sourceGroup, sourceIndex, targetGroup, targetIndex) {
        var srcTabs = sourceGroup.querySelectorAll("[data-miki-tab=\"true\"]");
        var srcPanels = sourceGroup.querySelectorAll(".miki-editor-content");
        if (sourceIndex >= srcTabs.length) return;

        var mvTab = srcTabs[sourceIndex];
        var mvPanel = srcPanels[sourceIndex];
        if (!mvTab) return;

        if (sourceGroup === targetGroup) {
          var allTabs = sourceGroup.querySelectorAll("[data-miki-tab=\"true\"]");
          var allPanels = sourceGroup.querySelectorAll(".miki-editor-content");
          var adjusted = targetIndex > sourceIndex ? targetIndex - 1 : targetIndex;
          var refTab = allTabs[adjusted] || null;
          var refPanel = allPanels[adjusted] || null;

          if (refTab) {
            mvTab.parentNode.insertBefore(mvTab, refTab);
            if (mvPanel && refPanel) mvPanel.parentNode.insertBefore(mvPanel, refPanel);
          } else {
            mvTab.parentNode.appendChild(mvTab);
            if (mvPanel) mvPanel.parentNode.appendChild(mvPanel);
          }
          mikiEditorArea._reindexGroup(sourceGroup);
          mikiEditorArea.showTab(getGroupId(sourceGroup), adjusted, true);
        } else {
          mvTab.remove();
          if (mvPanel) mvPanel.remove();
          mikiEditorArea._reindexGroup(sourceGroup);

          var tTabbar = targetGroup.querySelector(".miki-editor-tabbar");
          var tContainer = targetGroup.querySelector(".miki-editor-content-container");
          if (tTabbar && tContainer) {
            var tTabs = tTabbar.querySelectorAll("[data-miki-tab=\"true\"]");
            var tPanels = tContainer.querySelectorAll(".miki-editor-content");
            var refT = tTabs[targetIndex] || null;
            var refP = tPanels[targetIndex] || null;
            if (refT) {
              tTabbar.insertBefore(mvTab, refT);
              if (mvPanel && refP) tContainer.insertBefore(mvPanel, refP);
            } else {
              tTabbar.appendChild(mvTab);
              if (mvPanel) tContainer.appendChild(mvPanel);
            }
          }
          mikiEditorArea._reindexGroup(targetGroup);
          var newTargetIdx = Math.min(targetIndex, targetGroup.querySelectorAll("[data-miki-tab=\"true\"]").length - 1);
          mikiEditorArea.showTab(getGroupId(targetGroup), newTargetIdx < 0 ? 0 : newTargetIdx, true);

          var srcRemaining = sourceGroup.querySelectorAll("[data-miki-tab=\"true\"]");
          if (srcRemaining.length) {
            mikiEditorArea.showTab(getGroupId(sourceGroup), Math.min(sourceIndex, srcRemaining.length - 1), false);
          }
        }
      }

      function onPointerDown(e) {
        var tab = e.target.closest("[data-miki-tab=\"true\"]");
        if (!tab || e.button !== 0) return;
        if (tab.classList.contains("miki-dragging")) return;

        pointerId = e.pointerId;
        startX = e.clientX;
        startY = e.clientY;
        startTime = Date.now();
        dragTab = tab;
        dragGroupId = getGroupId(getTabGroup(tab));
        dragIndex = getTabIndex(tab);
        dragging = false;

        holdTimer = setTimeout(function () {
          if (pointerId === null) return;
          dragging = true;
          dragTab.classList.add("miki-dragging");
          dragTab.style.opacity = "0.4";
          ghost = createGhost(dragTab);
          positionGhost(e);
          document.body.style.cursor = "grabbing";
          dragTab.setPointerCapture(e.pointerId);
        }, HOLD_DELAY);
      }

      function onPointerMove(e) {
        if (pointerId === null) return;
        if (pointerId !== e.pointerId) return;

        var dx = e.clientX - startX;
        var dy = e.clientY - startY;

        if (!dragging) {
          if (Math.abs(dx) > DRAG_THRESHOLD || Math.abs(dy) > DRAG_THRESHOLD) {
            clearTimeout(holdTimer);
            holdTimer = null;
            dragging = true;
            if (dragTab) {
              dragTab.classList.add("miki-dragging");
              dragTab.style.opacity = "0.4";
              ghost = createGhost(dragTab);
              positionGhost(e);
              document.body.style.cursor = "grabbing";
              dragTab.setPointerCapture(e.pointerId);
            }
          }
          return;
        }

        if (ghost) positionGhost(e);

        var target = getDropTarget(e.clientX, e.clientY);
        if (target && target !== dragTab) {
          var rect = target.getBoundingClientRect();
          var midX = rect.left + rect.width / 2;
          showDropIndicator(target, e.clientX < midX);
        } else {
          hideDropIndicator();
        }
      }

      function onPointerUp(e) {
        if (pointerId === null) return;
        if (pointerId !== e.pointerId) return;

        clearTimeout(holdTimer);
        holdTimer = null;

        var wasDragging = dragging;
        var tab = dragTab;

        pointerId = null;
        dragging = false;
        hideDropIndicator();

        if (ghost) {
          document.body.removeChild(ghost);
          ghost = null;
        }
        document.body.style.cursor = "";

        if (tab) {
          tab.classList.remove("miki-dragging");
          tab.style.opacity = "";
        }

        if (wasDragging && tab) {
          var target = getDropTarget(e.clientX, e.clientY);
          if (target && target !== tab) {
            var targetGroup = getTabGroup(target);
            var targetIndex = getTabIndex(target);
            var sourceGroup = getTabGroup(tab);
            var rect = target.getBoundingClientRect();
            var adjustedTargetIndex = targetIndex + (e.clientX >= rect.left + rect.width / 2 ? 1 : 0);
            moveTab(sourceGroup, dragIndex, targetGroup, adjustedTargetIndex);
          }
        }

        dragTab = null;
        dragGroupId = null;
        dragIndex = null;
      }

      editorArea.addEventListener("pointerdown", onPointerDown);
      editorArea.addEventListener("pointermove", onPointerMove);
      editorArea.addEventListener("pointerup", onPointerUp);
      editorArea.addEventListener("pointercancel", onPointerUp);
      editorArea.addEventListener("lostpointercapture", function () {
        if (dragging) onPointerUp({ clientX: startX, clientY: startY, pointerId: pointerId });
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

