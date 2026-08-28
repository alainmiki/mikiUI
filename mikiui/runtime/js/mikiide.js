(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.mikiIDE !== "undefined") return;

  /* ---------------------------------------------------------------
   * IDEEditor — lightweight code editor with line-number gutter.
   *
   * Features:
   *  - Line-number gutter that scrolls in sync with the textarea.
   *  - Dynamic gutter width based on line count.
   *  - Tab key inserts spaces (configurable tabSize, default 4).
   *  - Auto-indent on newline (carries leading whitespace).
   *  - Basic undo/redo stack (Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z).
   *  - CustomEvents: miki:ide:input { text }, miki:ide:scroll.
   *  - Public API: mikiIDE.setValue(el, text), mikiIDE.getValue(el),
   *    mikiIDE.insert(el, text).
   * --------------------------------------------------------------- */

  var UNDO_LIMIT = 100;

  function mikiIDE() {}

  mikiIDE.init = function (el) {
    if (!el || el.dataset.mikiIdeInit === "true") return;
    el.dataset.mikiIdeInit = "true";

    var area = el.querySelector(".miki-ide-area");
    var gutter = el.querySelector(".miki-ide-gutter");
    if (!area) return;

    var tabSize = parseInt(el.getAttribute("data-tab-size") || "4", 10) || 4;

    /* --- Undo / redo --- */
    var undoStack = [];
    var redoStack = [];
    var lastValue = area.value;
    var suppressUndo = false;

    function snapshot() {
      undoStack.push(lastValue);
      if (undoStack.length > UNDO_LIMIT) undoStack.shift();
      redoStack.length = 0;
      lastValue = area.value;
    }

    /* --- Gutter sync --- */
    function updateGutter() {
      if (!gutter) return;
      var lines = area.value.split("\n");
      var count = lines.length;
      var html = "";
      for (var i = 1; i <= count; i++) {
        html += i + "\n";
      }
      gutter.innerHTML = html;

      /* Dynamic gutter width: enough for the biggest line number */
      var digits = String(count).length;
      gutter.style.width = (Math.max(2.5, digits * 0.7 + 1.2)) + "rem";
    }

    function syncScroll() {
      if (gutter) gutter.scrollTop = area.scrollTop;
    }

    on(area, "input", function () {
      if (!suppressUndo && area.value !== lastValue) {
        undoStack.push(lastValue);
        if (undoStack.length > UNDO_LIMIT) undoStack.shift();
        redoStack.length = 0;
      }
      suppressUndo = false;
      lastValue = area.value;
      updateGutter();
      dispatch(el, "miki:ide:input", { text: area.value });
    });

    on(area, "scroll", syncScroll);

    on(area, "keydown", function (e) {
      /* Tab handling */
      if (e.key === "Tab") {
        e.preventDefault();
        var start = area.selectionStart;
        var end = area.selectionEnd;
        var val = area.value;
        var insert = "";
        for (var s = 0; s < tabSize; s++) { insert += " "; }

        if (start === end) {
          area.value = val.slice(0, start) + insert + val.slice(end);
          area.selectionStart = area.selectionEnd = start + tabSize;
        } else {
          /* Indent / outdent selected lines */
          var before = val.slice(0, start);
          var lineStart = before.lastIndexOf("\n") + 1;
          var selected = val.slice(lineStart, end);
          var replaced;
          if (e.shiftKey) {
            /* Outdent: remove up to tabSize leading spaces per line */
            replaced = selected.replace(new RegExp("^ {1," + tabSize + "}", "gm"), "");
          } else {
            replaced = selected.replace(/^/gm, insert);
          }
          area.value = val.slice(0, lineStart) + replaced + val.slice(end);
          var delta = replaced.length - selected.length;
          area.selectionStart = start;
          area.selectionEnd = end + delta;
        }
        area.dispatchEvent(new Event("input", { bubbles: true }));
        return;
      }

      /* Auto-indent on Enter */
      if (e.key === "Enter") {
        var selStart = area.selectionStart;
        var val2 = area.value;
        var lineBeg = val2.lastIndexOf("\n", selStart - 1) + 1;
        var lineText = val2.slice(lineBeg, selStart);
        var leading = lineText.match(/^\s*/)[0];
        if (leading.length) {
          e.preventDefault();
          var insert2 = "\n" + leading;
          area.value = val2.slice(0, selStart) + insert2 + val2.slice(area.selectionEnd);
          var newPos = selStart + insert2.length;
          area.selectionStart = area.selectionEnd = newPos;
          area.dispatchEvent(new Event("input", { bubbles: true }));
        }
        return;
      }

      /* Undo / Redo */
      var mod = e.ctrlKey || e.metaKey;
      if (mod && (e.key === "z" || e.key === "Z")) {
        e.preventDefault();
        if (e.shiftKey) {
          /* Redo */
          if (redoStack.length) {
            undoStack.push(area.value);
            suppressUndo = true;
            area.value = redoStack.pop();
            area.dispatchEvent(new Event("input", { bubbles: true }));
          }
        } else {
          /* Undo */
          if (undoStack.length) {
            redoStack.push(area.value);
            suppressUndo = true;
            area.value = undoStack.pop();
            area.selectionStart = area.selectionEnd = area.value.length;
            area.dispatchEvent(new Event("input", { bubbles: true }));
          }
        }
      }
    });

    updateGutter();
  };

  mikiIDE.setValue = function (el, text) {
    var area = el && el.querySelector ? el.querySelector(".miki-ide-area") : null;
    if (area) { area.value = text; area.dispatchEvent(new Event("input", { bubbles: true })); }
  };

  mikiIDE.getValue = function (el) {
    var area = el && el.querySelector ? el.querySelector(".miki-ide-area") : null;
    return area ? area.value : "";
  };

  mikiIDE.insert = function (el, text) {
    var area = el && el.querySelector ? el.querySelector(".miki-ide-area") : null;
    if (!area) return;
    var start = area.selectionStart;
    var end = area.selectionEnd;
    var val = area.value;
    area.value = val.slice(0, start) + text + val.slice(end);
    area.selectionStart = area.selectionEnd = start + text.length;
    area.dispatchEvent(new Event("input", { bubbles: true }));
  };

  window.mikiIDE = mikiIDE;
})();
