(function () {
  "use strict";

  var miki = window.miki || {};

  /* Only define if the full implementation from the component's
     static/splitview.js hasn't already been loaded. */
  if (typeof window.mikiEditorArea !== "undefined") return;

  var mikiEditorArea = {
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

      if (tabs[index]) tabs[index].remove();
      if (panels[index]) panels[index].remove();

      var remainingTabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
      if (remainingTabs.length > 0) {
        var newActiveIndex = Math.min(index, remainingTabs.length - 1);
        mikiEditorArea.showTab(groupId, newActiveIndex);
      }

      dispatch(group, "miki:editor:tabclosed", { groupId: groupId, index: index });
    },

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
    },

    initGroup: function (group) {
      var tabs = group.querySelectorAll("[data-miki-tab=\"true\"]");
      for (var i = 0; i < tabs.length; i++) {
        (function (tab, idx) {
          on(tab, "click", function (e) {
            if (e.target.closest("[data-miki-tab-close=\"true\"]")) return;
            var groupId = tab.getAttribute("data-miki-tab-group");
            mikiEditorArea.showTab(groupId, idx);
          });

          var closeBtn = tab.querySelector("[data-miki-tab-close=\"true\"]");
          if (closeBtn) {
            on(closeBtn, "click", function (e) {
              e.preventDefault();
              e.stopPropagation();
              var groupId = tab.getAttribute("data-miki-tab-group");
              mikiEditorArea.closeTab(groupId, idx);
            });
          }

          on(tab, "keydown", function (e) {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              var groupId = tab.getAttribute("data-miki-tab-group");
              mikiEditorArea.showTab(groupId, idx);
            }
          });
        })(tabs[i], i);
      }
    },

    initSplitter: function (editorArea, splitter) {
      var firstPane = splitter.previousElementSibling;
      var secondPane = splitter.nextElementSibling;
      if (!firstPane || !secondPane) return;

      var orientation = editorArea.getAttribute("data-orientation") || "horizontal";
      var minSize = parseInt(editorArea.getAttribute("data-min-size") || "150", 10);
      var isHorizontal = orientation === "horizontal";

      var dragging = false;
      var startPos = 0;
      var firstStartSize = 0;
      var containerSize = 0;
      var splitterSize = 0;

      function getPx(el, axis) {
        return axis === "x" ? el.offsetWidth : el.offsetHeight;
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
      }

      function resetPx(el, axis) {
        if (axis === "x") el.style.width = "";
        else el.style.height = "";
        el.style.flex = "";
      }

      function onDragStart(pos) {
        dragging = true;
        startPos = pos;
        firstStartSize = getPx(firstPane, isHorizontal ? "x" : "y");
        containerSize = getPx(editorArea, isHorizontal ? "x" : "y");
        splitterSize = getPx(splitter, isHorizontal ? "x" : "y");
        splitter.classList.add("miki-splitter-dragging");
        document.body.style.cursor = isHorizontal ? "col-resize" : "row-resize";
        document.body.style.userSelect = "none";

        on(document, "mousemove", onMouseMove);
        on(document, "mouseup", onMouseUp);
        on(document, "touchmove", onTouchMove, { passive: false });
        on(document, "touchend", onTouchEnd);
      }

      function onDragMove(pos) {
        if (!dragging) return;
        var delta = pos - startPos;
        var maxFirst = Math.max(minSize, containerSize - splitterSize - minSize);
        var newFirst = Math.max(minSize, Math.min(maxFirst, firstStartSize + delta));

        if (isHorizontal) {
          firstPane.style.width = newFirst + "px";
          firstPane.style.flex = "none";
          secondPane.style.flex = "1 1 0";
          secondPane.style.width = "";
        } else {
          firstPane.style.height = newFirst + "px";
          firstPane.style.flex = "none";
          secondPane.style.flex = "1 1 0";
          secondPane.style.height = "";
        }
        dispatch(editorArea, "miki:editor:resize", {
          orientation: orientation,
          firstSize: newFirst
        });
      }

      function onDragEnd() {
        dragging = false;
        splitter.classList.remove("miki-splitter-dragging");
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
        resetPx(firstPane, isHorizontal ? "x" : "y");
        resetPx(secondPane, isHorizontal ? "x" : "y");
        off(document, "mousemove", onMouseMove);
        off(document, "mouseup", onMouseUp);
        off(document, "touchmove", onTouchMove);
        off(document, "touchend", onTouchEnd);
      }

      function onMouseMove(e) {
        if (!dragging) return;
        e.preventDefault();
        var pos = isHorizontal ? e.clientX : e.clientY;
        onDragMove(pos);
      }

      function onTouchMove(e) {
        if (!dragging || e.touches.length !== 1) return;
        e.preventDefault();
        var touch = e.touches[0];
        var pos = isHorizontal ? touch.clientX : touch.clientY;
        onDragMove(pos);
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
    }
  };

  window.mikiEditorArea = mikiEditorArea;
})();
