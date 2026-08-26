(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDial = {
    _resolve: function (el) {
      if (!el) return null;
      if (typeof el === "string") {
        return document.querySelector(el);
      }
      var dial = findClosest(el, "[data-miki-dial=\"true\"]");
      return dial || el;
    },

    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var input = container.querySelector('input[type="range"]');
      if (!input) return;

      var valueEl = container.querySelector(".miki-dial-value");
      var knob = container.querySelector(".miki-dial-knob");
      var track = container.querySelector(".miki-dial-track");
      var progress = container.querySelector(".miki-dial-progress");

      var min = parseFloat(input.min) || 0;
      var max = parseFloat(input.max) || 100;
      var step = parseFloat(input.step) || 1;
      var wrap = container.getAttribute("data-wrap") || "none";
      var size = parseInt(container.getAttribute("data-size") || "140", 10);

      function clamp(val) {
        return Math.max(min, Math.min(max, val));
      }

      function roundToStep(val) {
        var s = step > 0 ? step : 1;
        return Math.round(val / s) * s;
      }

      function setValue(val, dispatchEvent) {
        var oldVal = parseFloat(input.value) || min;
        val = clamp(roundToStep(parseFloat(val)));
        if (wrap === "hard" && (val > max || val < min)) {
          val = val > max ? min : max;
        }
        input.value = val;
        var strVal = val.toString();
        if (valueEl) valueEl.textContent = strVal;

        if (knob) {
          var pct = ((val - min) / (max - min)) * 100;
          var rot = (pct / 100) * 270 - 135;
          knob.style.transform = "rotate(" + rot + "deg)";
        }

        if (progress) {
          progress.style.background =
            "conic-gradient(" +
            "var(--miki-accent, #6366f1) 0% " + pct + "%," +
            "var(--miki-border, #e2e8f0) " + pct + "% 100%)";
        }

        if (dispatchEvent) {
          dispatch(input, "miki:dial:change", {
            value: val,
            oldValue: oldVal,
            min: min,
            max: max,
          });
        }
      }

      function onInput() {
        setValue(parseFloat(input.value), true);
      }

      /* Click-to-value: clicking on the track sets the value proportionally */
      function onTrackClick(e) {
        if (!track) return;
        var rect = track.getBoundingClientRect();
        var cx = rect.left + rect.width / 2;
        var cy = rect.top + rect.height / 2;
        var radius = Math.min(rect.width, rect.height) / 2;

        var x, y;
        if (e.touches && e.touches[0]) {
          x = e.touches[0].clientX;
          y = e.touches[0].clientY;
        } else {
          x = e.clientX;
          y = e.clientY;
        }

        var dx = x - cx;
        var dy = y - cy;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist > radius) {
          var angle = Math.atan2(dy, dx);
          x = cx + Math.cos(angle) * radius;
          y = cy + Math.sin(angle) * radius;
        }

        /* Compute angle: -135deg at top-left -> +135deg at top-right */
        var angle = Math.atan2(y - cy, x - cx);
        var angleDeg = (angle * 180 / Math.PI + 180); /* 0 to 360 */
        var arcStart = 135;
        var arcRange = 270;
        var pct = ((angleDeg - arcStart + 360) % 360) / arcRange;
        if (pct < 0) pct = 0;
        if (pct > 1) pct = 1;
        if (wrap === "hard" && pct < 0.02) pct = 0;
        var val = min + pct * (max - min);
        val = clamp(roundToStep(val));
        setValue(val, true);
        e.preventDefault();
      }

      /* Keyboard support */
      function onKeyDown(e) {
        var current = parseFloat(input.value) || min;
        var v = current;

        if (e.key === "ArrowUp" || e.key === "ArrowRight") {
          e.preventDefault();
          v = current + step;
        } else if (e.key === "ArrowDown" || e.key === "ArrowLeft") {
          e.preventDefault();
          v = current - step;
        } else if (e.key === "Home") {
          e.preventDefault();
          v = min;
        } else if (e.key === "End") {
          e.preventDefault();
          v = max;
        } else {
          return;
        }

        setValue(v, true);
      }

      on(input, "input", onInput);
      on(input, "change", onInput);
      on(input, "keydown", onKeyDown);

      if (track) {
        on(track, "touchstart", onTrackClick, { passive: false });
        on(track, "mousedown", function (e) {
          e.preventDefault();
          onTrackClick(e);
          var rafId = 0;
          function onDragMove(ev) {
            ev.preventDefault();
            if (rafId) cancelAnimationFrame(rafId);
            rafId = requestAnimationFrame(function () {
              onTrackClick(ev);
            });
          }
          function onDragEnd() {
            if (rafId) cancelAnimationFrame(rafId);
            off(document, "mousemove", onDragMove);
            off(document, "mouseup", onDragEnd);
            off(document, "touchmove", onDragMove);
            off(document, "touchend", onDragEnd);
          }
          on(document, "mousemove", onDragMove, { passive: false });
          on(document, "mouseup", onDragEnd);
          on(document, "touchmove", onDragMove, { passive: false });
          on(document, "touchend", onDragEnd);
        });
      }

      /* Expose API */
      container.mikiDial = {
        setValue: function (v, dispatch) { setValue(v, dispatch !== false); },
        getValue: function () { return parseFloat(input.value) || min; },
        setMin: function (v) { input.min = v; min = parseFloat(v); },
        setMax: function (v) { input.max = v; max = parseFloat(v); },
        setStep: function (v) { input.step = v; step = parseFloat(v); },
      };

      /* Initialize values */
      setValue(parseFloat(input.value) || min, false);
    },

    setValue: function (el, value, dispatch) {
      var dial = mikiDial._resolve(el);
      if (dial && dial.mikiDial) {
        dial.mikiDial.setValue(value, dispatch);
      }
    },

    getValue: function (el) {
      var dial = mikiDial._resolve(el);
      if (dial && dial.mikiDial) {
        return dial.mikiDial.getValue();
      }
      return null;
    }
  };

  window.mikiDial = mikiDial;
})();
