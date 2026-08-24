(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDockablePanel = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      // Configurable settings (with sensible defaults)
      var snapThreshold = parseInt(el.getAttribute("data-snap-threshold") || "100", 10);
      var dockWidth = el.getAttribute("data-dock-width") || "300px";
      var dockHeight = el.getAttribute("data-dock-height") || "300px";
      var floatWidth = el.getAttribute("data-float-width") || "40vw";
      var floatHeight = el.getAttribute("data-float-height") || "50vh";

      // Persist original dock position so we can restore it
      var originalDock = el.getAttribute("data-miki-original-dock") || "in-page";
      if (!el.hasAttribute("data-miki-original-dock")) {
        el.setAttribute("data-miki-original-dock", originalDock);
      }

      // --- Action button event binding ---
      var buttons = el.querySelectorAll("[data-miki-dock-action]");
      for (var i = 0; i < buttons.length; i++) {
        var action = buttons[i].getAttribute("data-miki-dock-action");
        (function (btn, act) {
          on(btn, "click", function (e) {
            e.preventDefault();
            var panel = btn.closest(".miki-dockable-panel") || el;
            mikiDockablePanel[act](panel);
          });
        })(buttons[i], action);
      }

      // --- ESC to close when floating ---
      var escHandler = function (e) {
        if (e.key === "Escape" && el.getAttribute("data-miki-close-on-escape") !== "false") {
          mikiDockablePanel.close(el);
        }
      };
      on(el, "keydown", escHandler);

      // --- Snap zones (persistent, created once) ---
      var snapZones = [];

      function ensureSnapZones() {
        var edges = ["top", "left", "right", "bottom"];
        var labels = { top: "Dock Top", left: "Dock Left", right: "Dock Right", bottom: "Dock Bottom" };
        var positions = {
          top: { side: "top", align: "center" },
          left: { side: "left", align: "middle" },
          right: { side: "right", align: "middle" },
          bottom: { side: "bottom", align: "center" }
        };

        for (var i = 0; i < edges.length; i++) {
          var edge = edges[i];
          var zone = snapZones[i];
          if (!zone) {
            zone = document.createElement("div");
            zone.className = "miki-snap-zone miki-snap-" + edge;
            zone.setAttribute("data-miki-snap", edge);
            zone.textContent = labels[edge];
            zone.style.cssText =
              "position:fixed;z-index:9999;padding:12px 24px;background:rgba(79,70,229,0.92);" +
              "color:white;font-size:14px;font-weight:600;border-radius:8px;pointer-events:none;" +
              "opacity:0;transition:opacity 0.15s ease,transform 0.15s ease;";
            document.body.appendChild(zone);
            snapZones[i] = zone;
          }
        }
      }

      function positionSnapZones(mouseX, mouseY) {
        var vw = window.innerWidth;
        var vh = window.innerHeight;
        var activeZone = null;

        for (var i = 0; i < snapZones.length; i++) {
          var zone = snapZones[i];
          var edge = zone.getAttribute("data-miki-snap");
          var active = false;

          // Check threshold proximity for each edge
          if (edge === "top" && mouseY < snapThreshold) {
            zone.style.left = (vw / 2 - 60) + "px";
            zone.style.top = "10px";
            zone.style.right = "auto";
            zone.style.bottom = "auto";
            zone.style.transform = "translateX(0)";
            active = true;
          } else if (edge === "left" && mouseX < snapThreshold) {
            zone.style.left = "10px";
            zone.style.top = (vh / 2 - 30) + "px";
            zone.style.right = "auto";
            zone.style.bottom = "auto";
            zone.style.transform = "translateY(0)";
            active = true;
          } else if (edge === "right" && (vw - mouseX) < snapThreshold) {
            zone.style.right = "10px";
            zone.style.left = "auto";
            zone.style.top = (vh / 2 - 30) + "px";
            zone.style.bottom = "auto";
            zone.style.transform = "translateY(0)";
            active = true;
          } else if (edge === "bottom" && (vh - mouseY) < snapThreshold) {
            zone.style.left = (vw / 2 - 60) + "px";
            zone.style.right = "auto";
            zone.style.bottom = "10px";
            zone.style.top = "auto";
            zone.style.transform = "translateX(0)";
            active = true;
          }

          zone.style.opacity = active ? "1" : "0";
          zone.style.visibility = active ? "visible" : "hidden";
          if (active) activeZone = edge;
        }
        return activeZone;
      }

      function hideSnapZones() {
        for (var i = 0; i < snapZones.length; i++) {
          snapZones[i].style.opacity = "0";
          snapZones[i].style.visibility = "hidden";
        }
      }

      function checkSnap(mouseX, mouseY) {
        var vw = window.innerWidth;
        var vh = window.innerHeight;

        if (mouseY < snapThreshold) return "top";
        if (mouseX < snapThreshold) return "left";
        if (vw - mouseX < snapThreshold) return "right";
        if (vh - mouseY < snapThreshold) return "bottom";
        return null;
      }

      // --- Drag handling ---
      var header = el.querySelector(".miki-dock-header");
      if (header) {
        var dragState = {
          active: false,
          startX: 0,
          startY: 0,
          origLeft: 0,
          origTop: 0
        };

        function startDrag(e) {
          e.preventDefault();
          e.stopPropagation();

          // If docked or in-page, switch to floating first (centered)
          var wasDocked = !el.classList.contains("miki-dock-floating") && !el.classList.contains("miki-dock-in-page");
          var wasInPage = el.classList.contains("miki-dock-in-page");
          if (wasDocked || wasInPage) {
            mikiDockablePanel.detach(el);
          }

          ensureSnapZones();

          dragState.active = true;
          dragState.startX = e.clientX;
          dragState.startY = e.clientY;
          var rect = el.getBoundingClientRect();
          dragState.origLeft = rect.left;
          dragState.origTop = rect.top;

          header.classList.add("miki-dock-dragging");
          el.style.cursor = "grabbing";
          document.body.style.userSelect = "none";
          el.style.zIndex = "1001"; // Above other floating panels
        }

        function doDrag(e) {
          if (!dragState.active) return;
          e.preventDefault();

          var mouseX = e.clientX;
          var mouseY = e.clientY;
          var deltaX = mouseX - dragState.startX;
          var deltaY = mouseY - dragState.startY;

          // Move the panel with the cursor
          var newX = dragState.origLeft + deltaX;
          var newY = dragState.origTop + deltaY;

          // Constrain within viewport
          var panelW = el.offsetWidth;
          var panelH = el.offsetHeight;
          var vw = window.innerWidth;
          var vh = window.innerHeight;

          if (newX < 0) newX = 0;
          if (newY < 0) newY = 0;
          if (newX + panelW > vw) newX = vw - panelW;
          if (newY + panelH > vh) newY = vh - panelH;

          el.style.left = newX + "px";
          el.style.top = newY + "px";
          el.style.right = "auto";
          el.style.bottom = "auto";
          el.style.position = "fixed";
          el.style.transform = "none";

          // Show/hide snap zones
          positionSnapZones(mouseX, mouseY);
        }

        function endDrag(e) {
          if (!dragState.active) return;
          dragState.active = false;
          header.classList.remove("miki-dock-dragging");
          el.style.cursor = "";
          document.body.style.userSelect = "";
          hideSnapZones();

          // Check if we should snap to an edge on mouseup
          var snap = checkSnap(e.clientX, e.clientY);
          if (snap) {
            mikiDockablePanel.dockAt(el, snap);
          } else {
            // Stay floating at the new position
            el.classList.add("miki-dock-floating");
            el.setAttribute("data-miki-dock-state", "floating");
            el.setAttribute("data-miki-dock-position", "floating");
            el.style.position = "fixed";
            el.style.zIndex = "1000";
          }

          off(document, "mousemove", doDrag);
          off(document, "mouseup", endDrag);
        }

        on(header, "mousedown", function (e) {
          // Only start drag if not clicking a button
          if (e.target.closest("[data-miki-dock-action]")) return;
          startDrag(e);
          on(document, "mousemove", doDrag, { passive: false });
          on(document, "mouseup", endDrag);
        });
      }

      // Persist docked/floating state if a key is supplied
      try {
        var dockPersistKey = el.getAttribute("data-miki-dock-persist-key") || null;
        if (dockPersistKey && window.localStorage) {
          // Save current state whenever panel changes
          var saveDockState = function () {
            var stateObj = {
              position: el.getAttribute("data-miki-dock-position"),
              dockState: el.getAttribute("data-miki-dock-state"),
              rect: el.getBoundingClientRect ? el.getBoundingClientRect() : null
            };
            try { localStorage.setItem(dockPersistKey, JSON.stringify(stateObj)); } catch (e) {}
          };

          // Hook into actions that change state
          on(el, "miki:dockable:docked", saveDockState);
          on(el, "miki:dockable:detach", saveDockState);
          on(el, "miki:dockable:toggle", saveDockState);
          on(el, "miki:dockable:closed", saveDockState);
          on(el, "miki:dockable:shown", saveDockState);

          // On init, attempt to restore saved state
          var saved = null;
          try { saved = JSON.parse(localStorage.getItem(dockPersistKey)); } catch (e) { saved = null; }
          if (saved && saved.position) {
            // Apply saved position (use dockAt for edge positions)
            if (saved.position === "floating") {
              mikiDockablePanel.detach(el);
            } else if (saved.position === "in-page") {
              mikiDockablePanel.dockAt(el, "in-page");
            } else {
              mikiDockablePanel.dockAt(el, saved.position);
            }
          }
        }
      } catch (err) {
        /* ignore storage errors */
      }
    },

     // Dock the panel at a specific position
     dockAt: function (el, position) {
      var valid = ["top", "left", "right", "bottom", "floating", "in-page"];
      if (valid.indexOf(position) === -1) return;

      // Remove all dock classes
      el.classList.remove("miki-dock-top", "miki-dock-left", "miki-dock-right", "miki-dock-bottom", "miki-dock-floating", "miki-dock-in-page", "miki-dock-collapsed");

      // For in-page, don't add a position class (it stays in normal flow)
      if (position !== "in-page") {
        el.classList.add("miki-dock-" + position);
      }

      // Update data attributes
      el.setAttribute("data-miki-dock-position", position);
      el.setAttribute("data-miki-dock-state", position === "floating" ? "floating" : (position === "in-page" ? "in-page" : "docked"));

      // Clear ALL inline positioning styles — CSS classes handle positioning
      el.style.cssText = el.style.cssText.replace(/position\s*:\s*[^;]+;?/g, "");
      el.style.position = "";
      el.style.right = "";
      el.style.left = "";
      el.style.top = "";
      el.style.bottom = "";
      el.style.transform = "";
      el.style.maxWidth = "";
      el.style.maxHeight = "";
      el.style.width = "";
      el.style.height = "";
      el.style.zIndex = "";

      // Update indicator
      var indicator = el.querySelector(".miki-dock-indicator");
      if (indicator) {
        var icons = { in_page: "◎", top: "▲", left: "◀", right: "▶", bottom: "▼", floating: "◎" };
        var tooltips = { in_page: "In-page (inline)", top: "Docked top", left: "Docked left", right: "Docked right", bottom: "Docked bottom", floating: "Floating" };
        var iconKey = position === "in-page" ? "in_page" : position;
        indicator.textContent = icons[iconKey] || "◎";
        indicator.setAttribute("aria-label", tooltips[iconKey] || "");
        indicator.className = "miki-dock-indicator miki-dock-" + (position === "in-page" ? "in-page" : position);
      }

      // Update detach/anchor button aria-label
      var detachBtn = el.querySelector('[data-miki-dock-action="detach"]');
      if (detachBtn) {
        detachBtn.setAttribute("aria-label", position === "floating" || position === "in-page" ? "Dock panel" : "Float panel");
      }

      dispatch(el, "miki:dockable:docked", { position: position });
    },

    // Toggle collapsed/expanded state
    toggle: function (el) {
      el.classList.toggle("miki-dock-collapsed");
      var isOpen = !el.classList.contains("miki-dock-collapsed");
      var currentState = el.getAttribute("data-miki-dock-state");
      var newState = isOpen ? (currentState === "floating" ? "floating" : "docked") : "collapsed";
      el.setAttribute("data-miki-dock-state", newState);

      var toggleBtn = el.querySelector('[data-miki-dock-action="toggle"]');
      if (toggleBtn) {
        toggleBtn.setAttribute("aria-label", isOpen ? "Collapse panel" : "Expand panel");
        var icon = toggleBtn.querySelector(".miki-dock-toggle-icon");
        if (icon) icon.textContent = isOpen ? "▼" : "▶";
      }

      dispatch(el, "miki:dockable:toggle", { open: isOpen });
    },

    // Close (hide) the panel
    close: function (el) {
      el.style.display = "none";
      el.setAttribute("data-miki-dock-state", "closed");
      dispatch(el, "miki:dockable:closed", {});
    },

     // Show the panel (restore from closed)
     show: function (el) {
      el.style.display = "";
      var state = el.getAttribute("data-miki-dock-state") || "docked";
      if (state === "closed") {
        var dockPos = el.getAttribute("data-miki-dock-position") || "in-page";
        el.setAttribute("data-miki-dock-state", dockPos === "floating" ? "floating" : (dockPos === "in-page" ? "in-page" : "docked"));
      }
      dispatch(el, "miki:dockable:shown", {});
     },

      // Detach (float) or return to original position (in-page or docked)
     detach: function (el) {
      var wasFloating = el.classList.contains("miki-dock-floating");
      var dockWidth = el.getAttribute("data-float-width") || "40vw";
      var dockHeight = el.getAttribute("data-float-height") || "50vh";

      if (wasFloating) {
        // Return to original position (in-page or docked edge)
        var dockPos = el.getAttribute("data-miki-original-dock") || "in-page";
        el.classList.remove("miki-dock-floating");
        if (dockPos !== "in-page") {
          el.classList.add("miki-dock-" + dockPos);
        }
        el.setAttribute("data-miki-dock-state", dockPos === "floating" ? "floating" : (dockPos === "in-page" ? "in-page" : "docked"));
        el.setAttribute("data-miki-dock-position", dockPos);

        // Clear all inline positioning styles — CSS handles it
        el.style.position = "";
        el.style.zIndex = "";
        el.style.left = "";
        el.style.right = "";
        el.style.top = "";
        el.style.bottom = "";
        el.style.transform = "";
        el.style.maxWidth = "";
        el.style.maxHeight = "";
        el.style.width = "";
        el.style.height = "";
      } else {
        // Go floating (centered over viewport)
        el.setAttribute("data-miki-original-dock", el.getAttribute("data-miki-dock-position") || "in-page");
        el.classList.add("miki-dock-floating");
        el.classList.remove("miki-dock-top", "miki-dock-left", "miki-dock-right", "miki-dock-bottom", "miki-dock-in-page");
        el.setAttribute("data-miki-dock-state", "floating");
        el.setAttribute("data-miki-dock-position", "floating");

        // Apply configurable floating dimensions
        el.style.position = "fixed";
        el.style.zIndex = "1000";
        el.style.left = "50%";
        el.style.top = "50%";
        el.style.transform = "translate(-50%, -50%)";
        el.style.maxWidth = "90vw";
        el.style.maxHeight = "90vh";
        el.style.width = dockWidth;
        el.style.height = dockHeight;
      }

      // Update detach button aria-label
      var detachBtn = el.querySelector('[data-miki-dock-action="detach"]');
      if (detachBtn) {
        detachBtn.setAttribute("aria-label", wasFloating ? "Float panel" : "Dock panel");
      }

      dispatch(el, "miki:dockable:detach", { floating: !wasFloating });
    }
  };

  window.mikiDockablePanel = mikiDockablePanel;
})();
