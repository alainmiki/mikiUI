/*!
 * MikiUI Runtime JavaScript v1.0
 * Dependency-free interactive widget runtime.
 * Works with or without Alpine.js / HTMX — every widget auto-initializes
 * from data-miki-* attributes.  Re-runs after every HTMX swap via the
 * "miki:swapped" custom event dispatched by htmx_runtime.js.
 *
 * ============================================================================
 * DOCUMENTATION — What each widget does and what data attributes it looks for
 * ============================================================================
 *
 * TABS (mikiTabs)
 *   data-miki-tabs="true"                   On the container <div>
 *   data-miki-tab-group="<id>"              Unique group ID (default: auto-generated)
 *   data-miki-tab-index="<n>"               On each tab button; shown when clicked
 *   data-miki-tab-panel="<id>-<n>"          ID of the panel to show
 *   .miki-tab-close                        Close button (optional, removes tab)
 *
 * DRAWER (mikiDrawer)
 *   data-miki-drawer="true"                On the drawer container
 *   data-miki-drawer-side="<left|right|top|bottom>"
 *   data-miki-drawer-esc-close="true"      ESC key to close (default: true)
 *   .miki-drawer-open                      Class toggles visibility
 *   [data-miki-drawer-close="true"]        Close button(s) inside
 *   [data-miki-drawer-overlay="true"]      Overlay click-to-close
 *   [data-miki-drawer-toggle="true"]       External toggle buttons (uses data-miki-drawer-target)
 *
 * SPLITVIEW (mikiSplitView)
 *   data-miki-splitview="true"             On the container
 *   data-orientation="<horizontal|vertical>"
 *   data-min-size="<px>"                   Minimum pane size
 *   .miki-splitter                         The draggable divider
 *   .miki-split-left / .miki-split-right   The two panes
 *
 * DOCKABLE PANEL (mikiDockablePanel)
 *   data-miki-dockable="true"              On the panel <section>
 *   data-miki-dock-state="<docked|floating|collapsed>"
 *   [data-miki-dock-action="<toggle|close|detach>"]
 *   .miki-dock-header                    Header with action buttons
 *   .miki-dock-body                      Collapsible content body
 *   .miki-dock-indicator                 Visual hint showing dock position
 *
 * DIALOG (native <dialog> + mikiDialog)
 *   <dialog class="miki-dialog" data-miki-dialog="true">
 *   data-miki-dialog-close-on-overlay="true"  Click outside to close
 *   data-miki-dialog-close-on-escape="true"   ESC key to close
 *   [data-miki-dialog-close="true"]          Close button(s) inside
 *
 * MODAL (mikiModal)
 *   data-miki-modal="true"                  On the overlay <div>
 *   data-miki-modal-open="true"            Initial visibility state
 *   [data-miki-modal-close="true"]         Close button(s)
 *   Click on overlay (outside panel) closes if data-miki-close-on-overlay="true"
 *   ESC closes if data-miki-close-on-escape="true"
 *
 * SLIDER (mikiSlider)
 *   data-miki-slider="true"              On wrapper <div>
 *   input[type="range"].miki-slider-input  The actual slider
 *   .miki-slider-value                   Live value display <span>
 *
 * DIAL (mikiDial)
 *   data-miki-dial="true"                On the dial container
 *   input[type="range"].miki-dial-input  The range input
 *   .miki-dial-value                      Value display <span>
 *   .miki-dial-knob                      Visual rotary knob (CSS-rotated)
 *
 * PROGRESS DIALOG (mikiProgressDialog)
 *   data-miki-progress-dialog="true"   On the <dialog>
 *   [data-miki-dialog-close="true"]     Close button
 *   <progress> or .miki-progress-bar    Progress visualization
 *
 * PROGRESS BAR (mikiProgress)
 *   data-miki-progress="true"            On the container
 *   .miki-progress-value                 Inner fill bar (width updated live)
 *
 * COLLAPSIBLE (mikiCollapsible)
 *   data-miki-collapsible="true"       Container
 *   [data-miki-collapsible-header="true"]  Header / toggle target
 *   .miki-collapsible-body              Content area (show/hide)
 *
 * MESSAGEBOX (mikiMessageBox)
 *   data-miki-messagebox="true"        Container
 *   [data-miki-messagebox-close="true"] Close button(s)
 *
 * FILE PICKER / DROPZONE (mikiDropzone)
 *   data-miki-dropzone="true"          Drop zone
 *   [data-miki-file-input="true"]      Hidden <input type="file">
 *   .miki-dropzone-label               File name display
 *
 * CAROUSEL (mikiCarousel)
 *   data-miki-carousel="true"          Container
 *   .miki-carousel-slide              Each slide
 *   .miki-carousel-dot                Dot indicator
 *   .miki-carousel-prev / .miki-carousel-next  Navigation buttons
 *
 * KANBAN (mikiKanban)
 *   data-miki-kanban="true"          Board container
 *   [data-miki-kanban-item="true"]   Draggable card
 *   .miki-kanban-column              Drop zone column
 *   Fires "miki:kanban:drop" custom event on drop.
 *
 * DATA GRID (mikiDataGrid)
 *   data-miki-datagrid="true"        Table container
 *   th[data-miki-sort-field="<key>"] Click to sort
 *   [data-miki-sort-indicator]    Sort direction indicator
 *   input[data-miki-search]       Global search
 *   input[data-miki-filter]       Column filter
 *   [data-miki-page="prev|next"]  Pagination buttons
 *   [data-miki-page-info]        Page info text
 *
 * CHAT (mikiChat)
 *   data-miki-chat="true"         Container
 *   .miki-chat-log                Scrollable message log
 *   [data-miki-chat-form="true"]  Message form
 *   .miki-chat-typing           Typing indicator
 *
 * CONTEXT WINDOW (mikiContextWindow)
 *   data-miki-context-window="true"   Container
 *   .miki-context-trigger          Trigger element (hover/click to show)
 *   .miki-context-menu             Menu content
 *   Click-away closes the menu.
 *
 * MENUBAR (mikiMenuBar)
 *   data-miki-menubar="true"      Nav element
 *   .miki-menu-title             Clickable menu header
 *   .miki-menu                  Dropdown menu
 *   Click-away closes open menus.
 *
 * ACCORDION (mikiAccordion)
 *   data-miki-accordion="true"  Container
 *   details > summary          Native disclosure (click to toggle)
 *   No JS required, but we add ESC-to-close for accessibility.
 */

(function () {
  "use strict";

  /* ===================== Utility helpers ===================== */

  function on(el, event, handler, opts) {
    el.addEventListener(event, handler, opts || false);
  }

  function off(el, event, handler, opts) {
    el.removeEventListener(event, handler, opts || false);
  }

  function findClosest(el, selector) {
    return el ? el.closest(selector) : null;
  }

  function generateId(prefix) {
    return prefix + "-" + Math.random().toString(36).slice(2, 10);
  }

  function dispatch(el, name, detail) {
    el.dispatchEvent(
      new CustomEvent(name, { detail: detail || {}, bubbles: true, cancelable: true })
    );
  }

  /* ===================== Dialog / Modal ===================== */

  /* ---- Focus trap helper ---- */

  function mikiFocusTrap(container, opts) {
    opts = opts || {};

    function getFocusable(el) {
      return el.querySelectorAll(
        'a[href], area[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), iframe, object, embed, ' +
        '[tabindex]:not([tabindex="-1"]), [contenteditable]'
      );
    }

    // Save the currently focused element so we can restore focus on close
    var active = document.activeElement;
    if (active && active !== document.body) {
      if (!active.id) active.id = generateId("miki-tabexit");
      container.dataset.mikiFocusTrapReturn = active.id;
    }

    function trap(e) {
      // Don't trap if the container is no longer open/visible
      var isOpen = container.hasAttribute("open") ||
        container.getAttribute("data-miki-modal-open") === "true" ||
        container.getAttribute("data-miki-dialog") === "true";
      var isDisplayed = container.style.display !== "none" && container.style.display !== "";
      if (!isOpen && !isDisplayed) return;

      var focusable = getFocusable(container);
      if (!focusable.length) return;

      var first = focusable[0];
      var last = focusable[focusable.length - 1];

      // Check if focus is still inside the container
      var inside = container.contains(document.activeElement);
      if (!inside) {
        // Focus left the container — bring it back to first
        e.preventDefault();
        first.focus();
        return;
      }

      if (e.key === "Tab") {
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault();
            last.focus();
          }
        } else {
          if (document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      }
    }

    container.dataset.mikiFocusTrapped = "true";
    on(document, "keydown", trap);
  }

  var mikiDialog = {
    init: function (dlg) {
      if (dlg.dataset.mikiInit === "true") return;
      dlg.dataset.mikiInit = "true";

      // ESC to close
      on(dlg, "keydown", function (e) {
        if (e.key === "Escape" && dlg.open) {
          var closeOnEsc = dlg.getAttribute("data-miki-dialog-close-on-escape");
          if (closeOnEsc === null || closeOnEsc === "true") {
            mikiDialog.close(dlg);
          }
        }
      });

      // Click on backdrop
      if (dlg.getAttribute("data-miki-dialog-close-on-overlay") === "true") {
        on(dlg, "click", function (e) {
          if (e.target === dlg) {
            mikiDialog.close(dlg);
          }
        });
      }

      // Close buttons inside the dialog
      var closeBtns = dlg.querySelectorAll("[data-miki-dialog-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          on(btn, "click", function (e) {
            e.preventDefault();
            mikiDialog.close(dlg);
          });
        })(closeBtns[i]);
      }
    },

    show: function (dlg) {
      // Save the currently-focused element so we can restore focus later
      var active = document.activeElement;
      if (active && active !== document.body && active.id) {
        dlg.setAttribute("data-miki-dialog-trigger", active.id);
      } else {
        var _id = active && active.tagName ? active.tagName.toLowerCase() + "-trigger" : "dialog-trigger";
        dlg.setAttribute("data-miki-dialog-trigger", _id);
      }

      if (typeof dlg.showModal === "function") {
        dlg.showModal();
      } else {
        dlg.setAttribute("open", "");
        dlg.style.display = "block";
      }

      // Focus trap (skip if already trapped)
      if (dlg.dataset.mikiFocusTrapped !== "true") {
        mikiFocusTrap(dlg);
      }

      // Focus first focusable element inside the dialog
      var focusable = dlg.querySelectorAll(
        'a[href], area[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length > 0) {
        focusable[0].focus();
      }

      dlg.dispatchEvent(new CustomEvent("miki:dialog:opened"));
    },

    close: function (dlg) {
      if (typeof dlg.close === "function") {
        dlg.close();
      } else {
        dlg.removeAttribute("open");
        dlg.style.display = "none";
      }

      // Restore focus to trigger element
      var triggerId = dlg.getAttribute("data-miki-dialog-trigger");
      if (triggerId) {
        var trigger = document.getElementById(triggerId);
        if (trigger && typeof trigger.focus === "function") {
          trigger.focus();
        }
      }
      // Clean up focus trap
      dlg.dataset.mikiFocusTrapped = "false";

      dlg.dispatchEvent(new CustomEvent("miki:dialog:closed"));
    },

    toggle: function (dlg) {
      if (dlg.open) {
        mikiDialog.close(dlg);
      } else {
        mikiDialog.show(dlg);
      }
    }
  };

  window.mikiDialog = mikiDialog;

  /* ===================== Modal ===================== */

  var mikiModal = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var isOpen = el.getAttribute("data-miki-modal-open") === "true";
      if (!isOpen) {
        el.style.display = "none";
      }

      // Close buttons
      var closeBtns = el.querySelectorAll("[data-miki-modal-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          on(btn, "click", function (e) {
            e.preventDefault();
            mikiModal.close(el);
          });
        })(closeBtns[i]);
      }

      // Click on overlay (outside panel) closes
      if (el.getAttribute("data-miki-close-on-overlay") !== "false") {
        on(el, "click", function (e) {
          if (e.target === el) {
            mikiModal.close(el);
          }
        });
      }

      // ESC key
      on(el, "keydown", function (e) {
        if (e.key === "Escape" && el.getAttribute("data-miki-close-on-escape") !== "false") {
          mikiModal.close(el);
        }
      });
    },

    show: function (el) {
      el.style.display = "flex";
      el.setAttribute("data-miki-modal-open", "true");
      el.setAttribute("aria-hidden", "false");

      // Focus trap (skip if already trapped)
      if (el.dataset.mikiFocusTrapped !== "true") {
        mikiFocusTrap(el);
      }

      var focusable = el.querySelectorAll(
        'a[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length > 0) {
        focusable[0].focus();
      }

      el.dispatchEvent(new CustomEvent("miki:modal:opened"));
    },

    close: function (el) {
      el.style.display = "none";
      el.setAttribute("data-miki-modal-open", "false");
      el.setAttribute("aria-hidden", "true");
      el.dataset.mikiFocusTrapped = "false";
      // Restore focus to the element that opened the modal
      if (el.dataset.mikiFocusTrapReturn) {
        var ret = document.getElementById(el.dataset.mikiFocusTrapReturn);
        if (ret) ret.focus();
        delete el.dataset.mikiFocusTrapReturn;
      }
      el.dispatchEvent(new CustomEvent("miki:modal:closed"));
    },

    toggle: function (el) {
      if (el.getAttribute("data-miki-modal-open") === "true") {
        mikiModal.close(el);
      } else {
        mikiModal.show(el);
      }
    }
  };

  window.mikiModal = mikiModal;

  /* ===================== Tabs ===================== */

  var mikiTabs = {
    show: function (groupId, index) {
      var i = parseInt(index, 10);
      var pagesContainer = document.getElementById(groupId + "-pages");
      var tablist = document.getElementById(groupId + "-tablist");

      // Show/hide panels
      if (pagesContainer) {
        for (var j = 0; j < pagesContainer.children.length; j++) {
          pagesContainer.children[j].style.display = j === i ? "block" : "none";
          pagesContainer.children[j].setAttribute("aria-hidden", j !== i ? "true" : "false");
        }
      }

      // Also handle individual panel elements by ID (for the Div-based tabs)
      var panel = document.getElementById(groupId + "-panel-" + i);
      if (panel) {
        panel.style.display = "block";
        panel.setAttribute("aria-hidden", "false");
      }
      // Hide other panels
      for (var n = 0; n < 100; n++) {
        if (n === i) continue;
        var otherPanel = document.getElementById(groupId + "-panel-" + n);
        if (otherPanel) {
          otherPanel.style.display = "none";
          otherPanel.setAttribute("aria-hidden", "true");
        }
        if (!otherPanel && n > 0) break;
      }

      // Update tab buttons
      if (tablist) {
        for (var k = 0; k < tablist.children.length; k++) {
          tablist.children[k].classList.toggle("miki-tab-active", k === i);
          tablist.children[k].setAttribute("aria-selected", k === i ? "true" : "false");
          tablist.children[k].setAttribute("tabindex", k === i ? "0" : "-1");
        }
      }

      // Sync hidden Section elements with [role=tabpanel]
      var allPanels = document.querySelectorAll('[role="tabpanel"][id^="' + groupId + '-panel-"]');
      for (var p = 0; p < allPanels.length; p++) {
        allPanels[p].hidden = p !== i;
        allPanels[p].setAttribute("aria-hidden", p !== i ? "true" : "false");
      }

      dispatch(document, "miki:tabs:changed", { group: groupId, index: i });
    },

    showAlpineFallback: function (groupId, index) {
      var i = parseInt(index, 10);
      var pages = document.getElementById(groupId + "-pages");
      if (pages) {
        for (var j = 0; j < pages.children.length; j++) {
          pages.children[j].style.display = j === i ? "block" : "none";
        }
      }
      var tablist = document.getElementById(groupId + "-tablist");
      if (tablist) {
        for (var k = 0; k < tablist.children.length; k++) {
          tablist.children[k].classList.toggle("miki-tab-active", k === i);
          tablist.children[k].setAttribute("aria-selected", k === i ? "true" : "false");
        }
      }
    },

    activate: function (groupId, index) {
      mikiTabs.show(groupId, index);
    },

    close: function (groupId, index) {
      var panel = document.getElementById(groupId + "-panel-" + index);
      if (panel) panel.remove();
      var tab = document.getElementById(groupId + "-tab-" + index);
      if (tab) tab.remove();
      dispatch(document, "miki:tabs:closed", { group: groupId, index: parseInt(index, 10) });
    },

    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      // Find all tab buttons within this container
      var tabs = container.querySelectorAll('[role="tab"]');
      for (var i = 0; i < tabs.length; i++) {
        (function (tab, idx) {
          on(tab, "click", function (e) {
            e.preventDefault();
            var group = tab.getAttribute("data-miki-tab-group") || tab.getAttribute("aria-controls");
            if (group) {
              var dashIndex = group.lastIndexOf("-panel-");
              var groupId = dashIndex !== -1 ? group.substring(0, dashIndex) : group;
              var panelIdx = dashIndex !== -1 ? parseInt(group.substring(dashIndex + 7), 10) : idx;
              mikiTabs.show(groupId || "miki-tabs", panelIdx);
            }
          });

          // Keyboard navigation
          on(tab, "keydown", function (e) {
            var tablist = tab.parentNode;
            var allTabs = Array.from(tablist.children);
            var currentIndex = allTabs.indexOf(tab);

            if (e.key === "ArrowRight" || e.key === "ArrowDown") {
              e.preventDefault();
              var next = (currentIndex + 1) % allTabs.length;
              allTabs[next].focus();
              allTabs[next].click();
            } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
              e.preventDefault();
              var prev = (currentIndex - 1 + allTabs.length) % allTabs.length;
              allTabs[prev].focus();
              allTabs[prev].click();
            } else if (e.key === "Home") {
              e.preventDefault();
              allTabs[0].focus();
              allTabs[0].click();
            } else if (e.key === "End") {
              e.preventDefault();
              allTabs[allTabs.length - 1].focus();
              allTabs[allTabs.length - 1].click();
            } else if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              tab.click();
            }
          });
        })(tabs[i], i);
      }
    }
  };

  window.mikiTabs = mikiTabs;

  /* ===================== Drawer ===================== */

  var mikiDrawer = {
    open: function (el) {
      var drawer = findClosest(el, ".miki-drawer");
      if (drawer) {
        drawer.classList.add("miki-drawer-open");
        drawer.setAttribute("aria-hidden", "false");
        dispatch(drawer, "miki:drawer:opened", {});
      }
    },

    close: function (el) {
      var drawer = findClosest(el, ".miki-drawer");
      if (drawer) {
        drawer.classList.remove("miki-drawer-open");
        drawer.setAttribute("aria-hidden", "true");
        dispatch(drawer, "miki:drawer:closed", {});
      }
    },

    toggle: function (el) {
      var drawer = findClosest(el, ".miki-drawer");
      if (!drawer) {
        // Try target selector
        var target = el.getAttribute("data-miki-drawer-target");
        if (target) {
          drawer = document.querySelector(target);
        }
        if (!drawer) {
          drawer = document.querySelector(".miki-drawer");
        }
      }
      if (drawer) {
        drawer.classList.toggle("miki-drawer-open");
        var isOpen = drawer.classList.contains("miki-drawer-open");
        drawer.setAttribute("aria-hidden", !isOpen);
        dispatch(drawer, "miki:drawer:toggled", { open: isOpen });
      }
    },

    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      // ESC to close drawer
      on(el, "keydown", function (e) {
        if (e.key === "Escape" && el.getAttribute("data-miki-drawer-esc-close") !== "false") {
          mikiDrawer.close(el);
        }
      });

      // Overlay click-to-close
      var overlay = el.querySelector("[data-miki-drawer-overlay=\"true\"]");
      if (overlay) {
        on(overlay, "click", function () {
          mikiDrawer.close(el);
        });
      }

      // Close buttons
      var closeBtns = el.querySelectorAll("[data-miki-drawer-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          on(btn, "click", function (e) {
            e.preventDefault();
            mikiDrawer.close(el);
          });
        })(closeBtns[i]);
      }
    },

    open: function (el) {
      var drawer = findClosest(el, ".miki-drawer");
      if (drawer) {
        drawer.classList.add("miki-drawer-open");
        drawer.setAttribute("aria-hidden", "false");
        var focusable = drawer.querySelectorAll(
          'a[href], input:not([disabled]):not([type="hidden"]), ' +
          'select:not([disabled]), textarea:not([disabled]), ' +
          'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        if (focusable.length > 0) focusable[0].focus();
        mikiFocusTrap(drawer);
        dispatch(drawer, "miki:drawer:opened", {});
      }
    },

    close: function (el) {
      var drawer = findClosest(el, ".miki-drawer");
      if (drawer) {
        drawer.classList.remove("miki-drawer-open");
        drawer.setAttribute("aria-hidden", "true");
        drawer.dataset.mikiFocusTrapped = "false";
        dispatch(drawer, "miki:drawer:closed", {});
      }
    }
  };

  window.mikiDrawer = mikiDrawer;

  /* ===================== SplitView ===================== */

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

  /* ===================== Dockable Panel ===================== */

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

  /* ===================== Slider ===================== */

  var mikiSlider = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var input = container.querySelector('input[type="range"]');
      if (!input) return;

      var valueEl = container.querySelector(".miki-slider-value");
      if (!valueEl) {
        // Create a value display if it doesn't exist
        valueEl = document.createElement("span");
        valueEl.className = "miki-slider-value";
        valueEl.textContent = input.value;
        container.appendChild(valueEl);
      }

      function updateValue() {
        valueEl.textContent = input.value;
        dispatch(input, "miki:slider:change", { value: input.value });
      }

      on(input, "input", updateValue);
      on(input, "change", updateValue);

      // Keyboard: PageUp/PageDown for 10-step increments
      on(input, "keydown", function (e) {
        var min = parseFloat(input.min) || 0;
        var max = parseFloat(input.max) || 100;
        var step = parseFloat(input.step) || 1;
        var current = parseFloat(input.value) || 0;

        if (e.key === "PageUp") {
          e.preventDefault();
          input.value = Math.min(max, current + step * 10);
          updateValue();
        } else if (e.key === "PageDown") {
          e.preventDefault();
          input.value = Math.max(min, current - step * 10);
          updateValue();
        }
      });

      // Initial fill styling
      mikiSlider.updateFill(input);
      on(input, "input", function () { mikiSlider.updateFill(input); });
    },

    updateFill: function (input) {
      var percent = ((parseFloat(input.value) - parseFloat(input.min || 0)) /
        (parseFloat(input.max || 100) - parseFloat(input.min || 0))) * 100;
      input.style.setProperty("--miki-slider-fill", percent + "%");
    }
  };

  window.mikiSlider = mikiSlider;

  /* ===================== Dial ===================== */

  var mikiDial = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var input = container.querySelector('input[type="range"]');
      if (!input) return;

      var valueEl = container.querySelector(".miki-dial-value");
      var knob = container.querySelector(".miki-dial-knob");

      function update() {
        var val = input.value;
        if (valueEl) valueEl.textContent = val;
        if (knob) {
          var percent = ((parseFloat(val) - parseFloat(input.min || 0)) /
            (parseFloat(input.max || 100) - parseFloat(input.min || 0))) * 100;
          var rotation = (percent / 100) * 270 - 135; // -135 to +135 degrees
          knob.style.transform = "rotate(" + rotation + "deg)";
        }
        dispatch(input, "miki:dial:change", { value: val });
      }

      on(input, "input", update);
      on(input, "change", update);

      // Keyboard support
      on(input, "keydown", function (e) {
        var min = parseFloat(input.min) || 0;
        var max = parseFloat(input.max) || 100;
        var step = parseFloat(input.step) || 1;
        var current = parseFloat(input.value) || 0;

        if (e.key === "ArrowUp" || e.key === "ArrowRight") {
          e.preventDefault();
          input.value = Math.min(max, current + step);
          update();
        } else if (e.key === "ArrowDown" || e.key === "ArrowLeft") {
          e.preventDefault();
          input.value = Math.max(min, current - step);
          update();
        } else if (e.key === "Home") {
          e.preventDefault();
          input.value = min;
          update();
        } else if (e.key === "End") {
          e.preventDefault();
          input.value = max;
          update();
        }
      });

      update();
    }
  };

  window.mikiDial = mikiDial;

  /* ===================== Progress Bar ===================== */

  var mikiProgress = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var value = parseFloat(el.getAttribute("data-value") || el.getAttribute("value") || 0);
      var max = parseFloat(el.getAttribute("data-max") || el.getAttribute("max") || 100);
      var percent = max > 0 ? (value / max) * 100 : 0;

      // Style native <progress> element
      var nativeProgress = el.querySelector("progress");
      if (nativeProgress) {
        nativeProgress.value = value;
        nativeProgress.max = max;
      }

      // Style custom progress bar
      var fill = el.querySelector(".miki-progress-value");
      if (fill) {
        fill.style.width = percent + "%";
      }

      el.setAttribute("data-miki-progress-percent", Math.round(percent) + "%");
      dispatch(el, "miki:progress:init", { value: value, max: max, percent: percent });
    },

    set: function (el, value, max) {
      max = max || 100;
      var percent = max > 0 ? (value / max) * 100 : 0;

      var nativeProgress = el.querySelector("progress");
      if (nativeProgress) {
        nativeProgress.value = value;
        nativeProgress.max = max;
      }

      var fill = el.querySelector(".miki-progress-value");
      if (fill) {
        fill.style.width = percent + "%";
      }

      el.setAttribute("data-value", value);
      el.setAttribute("data-max", max);
      el.setAttribute("data-miki-progress-percent", Math.round(percent) + "%");
      dispatch(el, "miki:progress:change", { value: value, max: max, percent: percent });
    }
  };

  window.mikiProgress = mikiProgress;

  /* ===================== Progress Dialog ===================== */

  var mikiProgressDialog = {
    init: function (dlg) {
      if (dlg.dataset.mikiInit === "true") return;
      dlg.dataset.mikiInit = "true";

      // Delegate to mikiDialog for backdrop/ESC handling
      mikiDialog.init(dlg);

      var value = parseFloat(dlg.getAttribute("data-value") || 0);
      var max = parseFloat(dlg.getAttribute("data-max") || 100);

      var bar = dlg.querySelector(".miki-progress-bar, progress");
      if (bar) {
        if (bar.tagName === "PROGRESS") {
          bar.value = value;
          bar.max = max;
        } else {
          var fill = bar.querySelector(".miki-progress-value");
          if (fill) {
            var percent = max > 0 ? (value / max) * 100 : 0;
            fill.style.width = percent + "%";
          }
        }
      }
    },

    setValue: function (dlg, value) {
      var max = parseFloat(dlg.getAttribute("data-max") || 100);
      var bar = dlg.querySelector(".miki-progress-bar, progress");
      if (bar) {
        if (bar.tagName === "PROGRESS") {
          bar.value = value;
        } else {
          var fill = bar.querySelector(".miki-progress-value");
          if (fill) {
            var percent = max > 0 ? (value / max) * 100 : 0;
            fill.style.width = percent + "%";
          }
        }
      }
      dlg.setAttribute("data-value", value);
      dispatch(dlg, "miki:progressdialog:value", { value: value, max: max });
    }
  };

  window.mikiProgressDialog = mikiProgressDialog;

  /* ===================== Collapsible / Accordion ===================== */

  var mikiCollapsible = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var header = el.querySelector("[data-miki-collapsible-header=\"true\"]");
      if (header) {
        on(header, "click", function () {
          mikiCollapsible.toggle(el);
        });
        on(header, "keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            mikiCollapsible.toggle(el);
          }
        });
      }

      // Accordion: only one open at a time
      if (el.getAttribute("data-miki-accordion") === "true") {
        var allInGroup = document.querySelectorAll(
          '[data-miki-accordion-group="' + (el.getAttribute("data-miki-accordion-group") || "") + '"][data-miki-collapsible="true"]'
        );
        // Group auto-init handled below
      }
    },

    toggle: function (el) {
      if (el.classList.contains("miki-collapsible-open")) {
        mikiCollapsible.close(el);
      } else {
        mikiCollapsible.open(el);
      }
    },

    open: function (el) {
      // Close siblings if within an accordion group
      var group = el.getAttribute("data-miki-accordion-group");
      if (group) {
        var siblings = document.querySelectorAll(
          '[data-miki-accordion-group="' + group + '"][data-miki-collapsible="true"]'
        );
        for (var i = 0; i < siblings.length; i++) {
          if (siblings[i] !== el) {
            siblings[i].classList.remove("miki-collapsible-open");
            siblings[i].classList.add("miki-collapsible-closed");
            siblings[i].setAttribute("data-miki-state", "closed");
          }
        }
      }

      el.classList.remove("miki-collapsible-closed");
      el.classList.add("miki-collapsible-open");
      el.setAttribute("data-miki-state", "open");

      var header = el.querySelector("[data-miki-collapsible-header=\"true\"]");
      if (header) {
        header.setAttribute("aria-expanded", "true");
      }

      var toggle = el.querySelector(".miki-collapsible-toggle");
      if (toggle) {
        toggle.textContent = "▼";
      }

      dispatch(el, "miki:collapsible:opened", {});
    },

    close: function (el) {
      el.classList.remove("miki-collapsible-open");
      el.classList.add("miki-collapsible-closed");
      el.setAttribute("data-miki-state", "closed");

      var header = el.querySelector("[data-miki-collapsible-header=\"true\"]");
      if (header) {
        header.setAttribute("aria-expanded", "false");
      }

      var toggle = el.querySelector(".miki-collapsible-toggle");
      if (toggle) {
        toggle.textContent = "▶";
      }

      dispatch(el, "miki:collapsible:closed", {});
    }
  };

  window.mikiCollapsible = mikiCollapsible;

  /* ===================== Accordion ===================== */

  var mikiAccordion = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var groupId = container.getAttribute("data-miki-accordion-group") || generateId("miki-accordion");
      container.setAttribute("data-miki-accordion-group", groupId);

      var items = container.querySelectorAll("[data-miki-collapsible-header=\"true\"]");
      for (var i = 0; i < items.length; i++) {
        var header = items[i];
        var parent = header.closest("[data-miki-collapsible=\"true\"]");
        if (parent) {
          parent.setAttribute("data-miki-accordion-group", groupId);
        }
      }

      // Initialize each collapsible in the accordion
      var collapsibles = container.querySelectorAll("[data-miki-collapsible=\"true\"]");
      for (var j = 0; j < collapsibles.length; j++) {
        mikiCollapsible.init(collapsibles[j]);
      }
    }
  };

  window.mikiAccordion = mikiAccordion;

  /* ===================== DataGrid ===================== */

  var mikiDataGrid = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var headers = el.querySelectorAll("th[data-miki-sort-field]");
      for (var i = 0; i < headers.length; i++) {
        (function (th) {
          var field = th.getAttribute("data-miki-sort-field");
          on(th, "click", function () {
            mikiDataGrid.sort(el, field);
          });
          on(th, "keydown", function (e) {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              mikiDataGrid.sort(el, field);
            }
          });
        })(headers[i]);
      }

      var searchInput = el.querySelector('input[data-miki-search]');
      if (searchInput) {
        var searchTimer = null;
        on(searchInput, "input", function () {
          clearTimeout(searchTimer);
          searchTimer = setTimeout(function () {
            if (el.getAttribute("data-miki-htmx-get")) {
              mikiDataGrid.htmxFetch(el);
            } else {
              mikiDataGrid.applyFilter(el);
            }
          }, 300);
        });
      }

      var filters = el.querySelectorAll('input[data-miki-filter]');
      for (var j = 0; j < filters.length; j++) {
        on(filters[j], "input", function () {
          if (el.getAttribute("data-miki-htmx-get")) {
            mikiDataGrid.htmxFetch(el);
          } else {
            mikiDataGrid.applyFilter(el);
          }
        });
      }

      // Search field select change
      var fieldSelect = el.querySelector('select[name="search_field"]');
      if (fieldSelect) {
        on(fieldSelect, "change", function () {
          if (el.getAttribute("data-miki-htmx-get")) {
            mikiDataGrid.htmxFetch(el);
          } else {
            mikiDataGrid.applyFilter(el);
          }
        });
      }

      mikiDataGrid.updatePaginationState(el);

      var pagination = el.querySelector("[data-miki-pagination]");
      if (pagination) {
        var prevBtn = pagination.querySelector('[data-miki-page="prev"]');
        var nextBtn = pagination.querySelector('[data-miki-page="next"]');
        if (prevBtn) {
          on(prevBtn, "click", function (e) {
            e.preventDefault();
            mikiDataGrid.prevPage(el);
          });
        }
        if (nextBtn) {
          on(nextBtn, "click", function (e) {
            e.preventDefault();
            mikiDataGrid.nextPage(el);
          });
        }
      }
    },

    sort: function (el, field) {
      var tbody = el.querySelector("tbody");
      if (!tbody) return;

      var headers = el.querySelectorAll("th[data-miki-sort-field]");
      var colIndex = -1;
      for (var i = 0; i < headers.length; i++) {
        if (headers[i].getAttribute("data-miki-sort-field") === field) {
          colIndex = i;
          break;
        }
      }
      if (colIndex < 0) return;

      var currentField = el.getAttribute("data-miki-sort-field") || "";
      var currentDir = el.getAttribute("data-miki-sort-dir") || "asc";
      var dir = currentField === field ? (currentDir === "asc" ? "desc" : "asc") : "asc";

      el.setAttribute("data-miki-sort-field", field);
      el.setAttribute("data-miki-sort-dir", dir);

      var isNumeric = false;
      for (var h = 0; h < headers.length; h++) {
        if (headers[h].getAttribute("data-miki-sort-field") === field) {
          isNumeric = headers[h].classList.contains("miki-th-number");
          break;
        }
      }

      var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
      var multiplier = dir === "asc" ? 1 : -1;

      rows.sort(function (a, b) {
        var aText = a.cells[colIndex] ? a.cells[colIndex].textContent : "";
        var bText = b.cells[colIndex] ? b.cells[colIndex].textContent : "";
        if (isNumeric) {
          var aNum = parseFloat(aText) || 0;
          var bNum = parseFloat(bText) || 0;
          return aNum < bNum ? -1 * multiplier : aNum > bNum ? 1 * multiplier : 0;
        }
        var aLower = aText.toLowerCase();
        var bLower = bText.toLowerCase();
        return aLower < bLower ? -1 * multiplier : aLower > bLower ? 1 * multiplier : 0;
      });

      rows.forEach(function (r) { tbody.appendChild(r); });

      // Update sort indicators
      for (var k = 0; k < headers.length; k++) {
        var indicator = headers[k].querySelector("[data-miki-sort-indicator]");
        var hField = headers[k].getAttribute("data-miki-sort-field");
        if (indicator) {
          if (hField === field) {
            indicator.textContent = dir === "asc" ? "▲" : "▼";
            indicator.setAttribute("data-dir", dir);
          } else {
            indicator.textContent = "▲";
            indicator.setAttribute("data-dir", "none");
          }
        }
        headers[k].setAttribute("aria-sort",
          hField === field ? (dir === "asc" ? "ascending" : "descending") : "none"
        );
      }

      dispatch(el, "miki:datagrid:sorted", { field: field, dir: dir });
    },

    applyFilter: function (el) {
      var tbody = el.querySelector("tbody");
      if (!tbody) return;

      var searchInput = el.querySelector('input[data-miki-search]');
      var searchQuery = searchInput ? searchInput.value.toLowerCase() : "";
      var fieldSelect = el.querySelector('select[name="search_field"]');
      var selectedField = fieldSelect ? fieldSelect.value : "";
      var filterInputs = el.querySelectorAll('input[data-miki-filter]');

      var rows = tbody.querySelectorAll("tr");
      var headers = el.querySelectorAll("th[data-miki-sort-field]");

      // Build field-to-column-index map for targeted search
      var fieldColMap = {};
      for (var h = 0; h < headers.length; h++) {
        var hf = headers[h].getAttribute("data-miki-sort-field");
        if (hf) fieldColMap[hf] = h;
      }

      for (var i = 0; i < rows.length; i++) {
        var rowText = rows[i].textContent.toLowerCase();
        var match = true;

        if (searchQuery) {
          if (selectedField && fieldColMap[selectedField] !== undefined) {
            var colIdx = fieldColMap[selectedField];
            var cellText = rows[i].cells[colIdx] ? rows[i].cells[colIdx].textContent.toLowerCase() : "";
            if (!cellText.includes(searchQuery)) {
              match = false;
            }
          } else {
            if (!rowText.includes(searchQuery)) {
              match = false;
            }
          }
        }

        if (match) {
          for (var j = 0; j < filterInputs.length; j++) {
            var jq = filterInputs[j].value.toLowerCase();
            if (jq) {
              var th = null;
              for (var k = 0; k < headers.length; k++) {
                var fi = headers[k].querySelector('input[data-miki-filter]');
                if (fi === filterInputs[j]) {
                  th = headers[k];
                  break;
                }
              }
              if (th) {
                var colIdx = Array.prototype.indexOf.call(headers, th);
                if (colIdx >= 0 && rows[i].cells[colIdx]) {
                  var cellText = rows[i].cells[colIdx].textContent.toLowerCase();
                  if (!cellText.includes(jq)) {
                    match = false;
                    break;
                  }
                }
              } else {
                if (!rowText.includes(jq)) {
                  match = false;
                  break;
                }
              }
            }
          }
        }

        rows[i].style.display = match ? "" : "none";
      }

      dispatch(el, "miki:datagrid:filtered", { query: searchQuery });
    },

    updatePaginationState: function (el) {
      var info = el.querySelector("[data-miki-page-info]");
      if (!info) return;

      var match = info.textContent.match(/Page\s*(\d+)\s*of\s*(\d+)/);
      if (!match) return;

      var currentPage = parseInt(match[1], 10);
      var totalPages = parseInt(match[2], 10);

      var prevBtn = el.querySelector('[data-miki-page="prev"]');
      var nextBtn = el.querySelector('[data-miki-page="next"]');

      if (prevBtn) prevBtn.disabled = currentPage <= 1;
      if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
    },

    prevPage: function (el) {
      var info = el.querySelector("[data-miki-page-info]");
      if (!info) return;
      var match = info.textContent.match(/Page\s*(\d+)\s*of\s*(\d+)/);
      if (!match) return;
      var currentPage = parseInt(match[1], 10);
      var totalPages = parseInt(match[2], 10);
      if (currentPage > 1) {
        if (el.getAttribute("data-miki-htmx-get")) {
          mikiDataGrid.htmxFetch(el, currentPage - 2);
        } else {
          dispatch(el, "miki:datagrid:navigate", { page: currentPage - 2, totalPages: totalPages });
        }
      }
    },

    nextPage: function (el) {
      var info = el.querySelector("[data-miki-page-info]");
      if (!info) return;
      var match = info.textContent.match(/Page\s*(\d+)\s*of\s*(\d+)/);
      if (!match) return;
      var currentPage = parseInt(match[1], 10);
      var totalPages = parseInt(match[2], 10);
      if (currentPage < totalPages) {
        if (el.getAttribute("data-miki-htmx-get")) {
          mikiDataGrid.htmxFetch(el, currentPage);
        } else {
          dispatch(el, "miki:datagrid:navigate", { page: currentPage, totalPages: totalPages });
        }
      }
    },

    htmxFetch: function (el, pageNum) {
      var url = el.getAttribute("data-miki-htmx-get");
      if (!url) return;

      var params = new URLSearchParams();
      var sortField = el.getAttribute("data-miki-sort-field") || "";
      if (sortField) params.set("sort_field", sortField);
      var sortDir = el.getAttribute("data-miki-sort-dir") || "";
      if (sortDir) params.set("sort_dir", sortDir);
      var searchInput = el.querySelector('input[data-miki-search]');
      if (searchInput && searchInput.value) params.set("search", searchInput.value);
      var fieldSelect = el.querySelector('select[name="search_field"]');
      if (fieldSelect && fieldSelect.value) params.set("search_field", fieldSelect.value);
      if (pageNum !== undefined) params.set("page", pageNum);

      var target = el.getAttribute("data-miki-htmx-target") || el.id;
      if (!target) return;

      var fullUrl = url + (url.indexOf("?") === -1 ? "?" : "&") + params.toString();

      var xhr = new XMLHttpRequest();
      xhr.open("GET", fullUrl, true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            var targetEl = document.querySelector(target);
            if (targetEl) {
              targetEl.innerHTML = xhr.responseText;
              initAll(targetEl);
            }
          }
          dispatch(el, "miki:datagrid:fetched", { page: pageNum, success: xhr.status === 200 });
        }
      };
      xhr.send();
    }
  };

  window.mikiDataGrid = mikiDataGrid;

  /* ===================== Kanban Board ===================== */

  var mikiKanban = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var items = el.querySelectorAll('[data-miki-kanban-item="true"]');
      var columns = el.querySelectorAll(".miki-kanban-column");

      for (var i = 0; i < items.length; i++) {
        (function (item) {
          item.setAttribute("draggable", "true");
          on(item, "dragstart", function (e) {
            mikiKanban.draggedItem = item;
            item.classList.add("miki-kanban-dragging");
            e.dataTransfer.effectAllowed = "move";
          });
          on(item, "dragend", function () {
            item.classList.remove("miki-kanban-dragging");
            mikiKanban.draggedItem = null;
          });
        })(items[i]);
      }

      for (var j = 0; j < columns.length; j++) {
        (function (column) {
          on(column, "dragover", function (e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = "move";
            column.classList.add("miki-drag-over");
          });
          on(column, "dragleave", function () {
            column.classList.remove("miki-drag-over");
          });
          on(column, "drop", function (e) {
            e.preventDefault();
            column.classList.remove("miki-drag-over");
            var dragged = mikiKanban.draggedItem;
            if (dragged && dragged !== column) {
              column.appendChild(dragged);
              var columnName = column.getAttribute("data-miki-kanban-column") || "";
              var fromColumn = "";
              var parentCol = dragged.closest(".miki-kanban-column");
              if (parentCol) {
                fromColumn = parentCol.getAttribute("data-miki-kanban-column") || "";
              }
              dispatch(el, "miki:kanban:drop", {
                item: dragged.textContent.trim(),
                fromColumn: fromColumn,
                toColumn: columnName
              });
            }
          });
        })(columns[j]);
      }
    },

    draggedItem: null
  };

  window.mikiKanban = mikiKanban;

  /* ===================== Chat UI ===================== */

  var mikiChat = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var log = el.querySelector(".miki-chat-log");
      var form = el.querySelector('[data-miki-chat-form="true"]');
      var input = form ? form.querySelector('input[name="message"]') : null;
      var typingIndicator = el.querySelector(".miki-chat-typing");

      if (log) {
        mikiChat.scrollToBottom(el);
      }

      if (input && form) {
        var typingTimer = null;
        var isTyping = false;

        on(input, "input", function () {
          if (typingIndicator) {
            if (!isTyping) {
              isTyping = true;
              typingIndicator.style.display = "block";
            }
            clearTimeout(typingTimer);
            typingTimer = setTimeout(function () {
              isTyping = false;
              typingIndicator.style.display = "none";
              mikiChat.scrollToBottom(el);
            }, 300);
          }
        });

        on(form, "keydown", function (e) {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            var btn = form.querySelector('button[type="submit"]') || form.querySelector("button");
            if (btn) btn.click();
          }
        });
      }

      // Auto-scroll observer
      if (log) {
        var observer = new MutationObserver(function () {
          mikiChat.scrollToBottom(el);
        });
        observer.observe(log, { childList: true, subtree: true });
        el.dataset.mikiObserver = "active";
      }
    },

    scrollToBottom: function (el) {
      var log = el.querySelector(".miki-chat-log");
      if (log) {
        log.scrollTop = log.scrollHeight;
      }
    },

    toggleTyping: function (el, show) {
      var indicator = el.querySelector(".miki-chat-typing");
      if (indicator) {
        indicator.style.display = show ? "block" : "none";
        mikiChat.scrollToBottom(el);
      }
    }
  };

  window.mikiChat = mikiChat;

  /* ===================== File Picker / Dropzone ===================== */

  var mikiDropzone = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var fileInput = el.querySelector('[data-miki-file-input="true"]');
      if (!fileInput) return;

      on(el, "click", function () {
        fileInput.click();
      });

      on(el, "keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          fileInput.click();
        }
      });

      var prevent = function (e) {
        e.preventDefault();
        e.stopPropagation();
      };

      on(el, "dragenter", function (e) {
        prevent(e);
        el.classList.add("miki-drag-over");
      });

      on(el, "dragover", function (e) {
        prevent(e);
        el.classList.add("miki-drag-over");
      });

      on(el, "dragleave", function (e) {
        prevent(e);
        el.classList.remove("miki-drag-over");
      });

      on(el, "drop", function (e) {
        prevent(e);
        el.classList.remove("miki-drag-over");
        var files = e.dataTransfer.files;
        if (files && files.length > 0) {
          fileInput.files = files;
          el.setAttribute("data-files", files.length);
          // Update the visible label with the dropped file names
          var label = el.querySelector(".miki-dropzone-label");
          if (label) {
            var names = [];
            for (var i = 0; i < files.length; i++) {
              names.push(files[i].name);
            }
            label.textContent = names.length === 1
              ? names[0]
              : names.join(", ") + " (" + files.length + " files)";
            label.classList.add("miki-has-files");
          }
          dispatch(el, "miki:files:dropped", { files: files });
        }
      });

      on(fileInput, "change", function () {
        if (fileInput.files && fileInput.files.length > 0) {
          var label = el.querySelector(".miki-dropzone-label");
          if (label) {
            var names = [];
            for (var i = 0; i < fileInput.files.length; i++) {
              names.push(fileInput.files[i].name);
            }
            label.textContent = names.length === 1
              ? names[0]
              : names.join(", ") + " (" + fileInput.files.length + " files)";
            label.classList.add("miki-has-files");
          }
          el.setAttribute("data-files", fileInput.files.length);
          dispatch(el, "miki:files:selected", { files: fileInput.files });
        }
      });
    }
  };

  window.mikiDropzone = mikiDropzone;

  /* ===================== Carousel ===================== */

  var mikiCarousel = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      el.setAttribute("data-miki-current-index", "0");

      var slides = el.querySelectorAll(".miki-carousel-slide");
      var dots = el.querySelectorAll(".miki-carousel-dot");

      var prevBtn = el.querySelector(".miki-carousel-prev");
      var nextBtn = el.querySelector(".miki-carousel-next");

      if (nextBtn) {
        on(nextBtn, "click", function () { mikiCarousel.next(el); });
      }
      if (prevBtn) {
        on(prevBtn, "click", function () { mikiCarousel.prev(el); });
      }

      for (var i = 0; i < dots.length; i++) {
        (function (dot, idx) {
          dot.setAttribute("data-index", idx);
          on(dot, "click", function () { mikiCarousel.goTo(el, idx); });
        })(dots[i], i);
      }

      var autoplay = el.getAttribute("data-autoplay") === "true";
      if (autoplay) {
        var interval = parseInt(el.getAttribute("data-interval") || "4000", 10);
        mikiCarousel.startAutoplay(el, interval);
      }

      on(el, "mouseenter", function () {
        mikiCarousel.stopAutoplay(el);
      });
      on(el, "mouseleave", function () {
        if (el.getAttribute("data-autoplay") === "true") {
          var interval = parseInt(el.getAttribute("data-interval") || "4000", 10);
          mikiCarousel.startAutoplay(el, interval);
        }
      });

      // Keyboard navigation
      on(el, "keydown", function (e) {
        if (e.key === "ArrowLeft") {
          e.preventDefault();
          mikiCarousel.prev(el);
        } else if (e.key === "ArrowRight") {
          e.preventDefault();
          mikiCarousel.next(el);
        }
      });
    },

    next: function (el) {
      var slides = el.querySelectorAll(".miki-carousel-slide");
      if (!slides.length) return;
      var current = parseInt(el.getAttribute("data-miki-current-index") || "0", 10);
      var next = (current + 1) % slides.length;
      mikiCarousel.goTo(el, next);
    },

    prev: function (el) {
      var slides = el.querySelectorAll(".miki-carousel-slide");
      if (!slides.length) return;
      var current = parseInt(el.getAttribute("data-miki-current-index") || "0", 10);
      var prev = (current - 1 + slides.length) % slides.length;
      mikiCarousel.goTo(el, prev);
    },

    goTo: function (el, index) {
      var slides = el.querySelectorAll(".miki-carousel-slide");
      var dots = el.querySelectorAll(".miki-carousel-dot");
      if (index < 0) index = slides.length - 1;
      if (index >= slides.length) index = 0;

      for (var i = 0; i < slides.length; i++) {
        if (i === index) {
          slides[i].classList.remove("miki-carousel-slide-hidden");
        } else {
          slides[i].classList.add("miki-carousel-slide-hidden");
        }
      }

      for (var j = 0; j < dots.length; j++) {
        if (j === index) {
          dots[j].classList.add("miki-carousel-dot-active");
        } else {
          dots[j].classList.remove("miki-carousel-dot-active");
        }
      }

      el.setAttribute("data-miki-current-index", index);
      dispatch(el, "miki:carousel:changed", { index: index });
    },

    startAutoplay: function (el, interval) {
      if (el.dataset.mikiAutoplayId) {
        clearInterval(parseInt(el.dataset.mikiAutoplayId, 10));
      }
      el.classList.remove("paused");
      var id = setInterval(function () {
        mikiCarousel.next(el);
      }, interval);
      el.dataset.mikiAutoplayId = String(id);
    },

    stopAutoplay: function (el) {
      if (el.dataset.mikiAutoplayId) {
        clearInterval(parseInt(el.dataset.mikiAutoplayId, 10));
        delete el.dataset.mikiAutoplayId;
      }
      el.classList.add("paused");
    }
  };

  window.mikiCarousel = mikiCarousel;

  /* ===================== Message Box ===================== */

  var mikiMessageBox = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var closeBtns = el.querySelectorAll("[data-miki-messagebox-close=\"true\"]");
      for (var i = 0; i < closeBtns.length; i++) {
        (function (btn) {
          on(btn, "click", function (e) {
            e.preventDefault();
            mikiMessageBox.close(el);
          });
        })(closeBtns[i]);
      }

      // ESC to close
      on(el, "keydown", function (e) {
        if (e.key === "Escape") {
          mikiMessageBox.close(el);
        }
      });

      // Click on overlay background
      if (el.getAttribute("data-miki-close-on-overlay") !== "false") {
        on(el, "click", function (e) {
          if (e.target === el) {
            mikiMessageBox.close(el);
          }
        });
      }
    },

    close: function (el) {
      el.style.display = "none";
      el.setAttribute("data-miki-messagebox-open", "false");
      el.setAttribute("aria-hidden", "true");
      el.dataset.mikiFocusTrapped = "false";
      dispatch(el, "miki:messagebox:closed", {});
    },

    show: function (el) {
      el.style.display = "flex";
      el.setAttribute("data-miki-messagebox-open", "true");
      el.setAttribute("aria-hidden", "false");

      // Focus trap
      var focusable = el.querySelectorAll(
        'a[href], input:not([disabled]):not([type="hidden"]), ' +
        'select:not([disabled]), textarea:not([disabled]), ' +
        'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      if (focusable.length > 0) {
        focusable[0].focus();
      }
      mikiFocusTrap(el);

      dispatch(el, "miki:messagebox:opened", {});
    }
  };

  window.mikiMessageBox = mikiMessageBox;

  /* ===================== Toggle Button ===================== */

  var mikiToggle = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      // The toggle button's inner icon is a child <i> or span
      var iconEl = el.querySelector(".miki-toggle-icon") || el.firstElementChild;

      function swap() {
        var iconOn = el.getAttribute("data-miki-icon-on");
        var iconOff = el.getAttribute("data-miki-icon-off");
        var isOn = el.getAttribute("data-miki-state") === "on";
        var newState = isOn ? "off" : "on";
        var newIcon = isOn ? iconOff : iconOn;
        if (iconEl) iconEl.textContent = newIcon;
        el.setAttribute("data-miki-state", newState);
        el.setAttribute("aria-pressed", isOn ? "false" : "true");

        var labelOn = el.getAttribute("data-miki-aria-label-on");
        var labelOff = el.getAttribute("data-miki-aria-label-off");
        var newLabel = isOn ? labelOff : labelOn;
        if (newLabel) el.setAttribute("aria-label", newLabel);

        dispatch(el, "miki:toggle:changed", { state: newState });
      }

      on(el, "click", function (e) {
        e.preventDefault();
        swap();
      });

      // Initialize state
      if (!el.getAttribute("data-miki-state")) {
        el.setAttribute("data-miki-state", "on");
        el.setAttribute("aria-pressed", "true");
      }
    }
  };

  window.mikiToggle = mikiToggle;

  /* ===================== Searchable Select ===================== */

  var mikiSearchableSelect = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      // Wrap native select in a container with a filter input
      var filterInput = document.createElement("input");
      filterInput.type = "text";
      filterInput.className = "miki-searchable-filter";
      filterInput.placeholder = "Type to filter...";
      filterInput.setAttribute("autocomplete", "off");

      var wrapper = document.createElement("div");
      wrapper.className = "miki-searchable-wrapper";
      wrapper.style.position = "relative";
      wrapper.style.display = "inline-block";
      wrapper.style.width = el.style.width || "100%";

      el.parentNode.insertBefore(wrapper, el);
      wrapper.appendChild(filterInput);
      wrapper.appendChild(el);

      on(filterInput, "input", function () {
        var filter = filterInput.value.toLowerCase();
        var options = el.querySelectorAll("option");
        var matchFound = false;
        for (var i = 0; i < options.length; i++) {
          var text = options[i].textContent.toLowerCase();
          if (text.indexOf(filter) > -1) {
            options[i].style.display = "";
            matchFound = true;
          } else {
            options[i].style.display = "none";
          }
        }
      });
    }
  };

  window.mikiSearchableSelect = mikiSearchableSelect;

  /* ===================== Context Window ===================== */

  var mikiContextWindow = {
    init: function (container) {
      if (container.dataset.mikiInit === "true") return;
      container.dataset.mikiInit = "true";

      var trigger = container.querySelector(".miki-context-trigger");
      var menu = container.querySelector(".miki-context-menu");

      if (!menu) return;

      var isOpen = false;

      function toggle() {
        if (isOpen) {
          close();
        } else {
          open();
        }
      }

      function open() {
        menu.style.display = "block";
        isOpen = true;
        container.setAttribute("data-miki-context-open", "true");

        // Position the menu
        var rect = menu.getBoundingClientRect();
        var viewport = {
          width: window.innerWidth,
          height: window.innerHeight
        };

        if (rect.right > viewport.width) {
          menu.style.left = "auto";
          menu.style.right = "0";
        }
        if (rect.bottom > viewport.height) {
          menu.style.top = "auto";
          menu.style.bottom = "100%";
        }
      }

      function close() {
        menu.style.display = "none";
        isOpen = false;
        container.setAttribute("data-miki-context-open", "false");
      }

      if (trigger) {
        on(trigger, "click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          toggle();
        });
        on(trigger, "keydown", function (e) {
          if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
            e.preventDefault();
            toggle();
          }
        });
      }

      // Click-away to close
      on(document, "click", function () {
        if (isOpen) {
          close();
        }
      });

      // ESC to close
      on(document, "keydown", function (e) {
        if (e.key === "Escape" && isOpen) {
          close();
        }
      });

      // Menu keyboard navigation
      if (menu) {
        on(menu, "keydown", function (e) {
          var items = Array.from(menu.querySelectorAll('[role="menuitem"]'));
          var currentIndex = items.indexOf(document.activeElement);

          if (e.key === "ArrowDown") {
            e.preventDefault();
            var next = (currentIndex + 1) % items.length;
            items[next].focus();
          } else if (e.key === "ArrowUp") {
            e.preventDefault();
            var prev = (currentIndex - 1 + items.length) % items.length;
            items[prev].focus();
          } else if (e.key === "Escape") {
            close();
          }
        });
      }
    }
  };

  window.mikiContextWindow = mikiContextWindow;

  /* ===================== Menu Bar ===================== */

  var mikiMenuBar = {
    init: function (navBar) {
      if (navBar.dataset.mikiInit === "true") return;
      navBar.dataset.mikiInit = "true";

      var titles = navBar.querySelectorAll(".miki-menu-title");
      var menus = navBar.querySelectorAll(".miki-menu");

      for (var i = 0; i < titles.length; i++) {
        (function (title) {
          on(title, "click", function (e) {
            e.stopPropagation();
            var menu = title.nextElementSibling;
            if (menu && menu.classList.contains("miki-menu")) {
              // Close all other menus
              var allMenus = navBar.querySelectorAll(".miki-menu");
              for (var j = 0; j < allMenus.length; j++) {
                if (allMenus[j] !== menu) {
                  allMenus[j].style.display = "none";
                }
              }
              menu.style.display = menu.style.display === "block" ? "none" : "block";
            }
          });

          on(title, "keydown", function (e) {
            if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
              e.preventDefault();
              var menu = title.nextElementSibling;
              if (menu && menu.classList.contains("miki-menu")) {
                menu.style.display = "block";
                var firstItem = menu.querySelector('.miki-menu-item');
                if (firstItem) firstItem.focus();
              }
            }
          });
        })(titles[i]);
      }

      // Click-away to close all menus
      on(document, "click", function () {
        for (var k = 0; k < menus.length; k++) {
          menus[k].style.display = "none";
        }
      });

      // ESC to close menus
      on(document, "keydown", function (e) {
        if (e.key === "Escape") {
          for (var m = 0; m < menus.length; m++) {
            menus[m].style.display = "none";
          }
        }
      });
    }
  };

  window.mikiMenuBar = mikiMenuBar;

  /* ===================== Auto-init System ===================== */

  var widgetRegistry = [
    { selector: '[data-miki-tabs="true"]', init: mikiTabs.init, name: "tabs" },
    { selector: '[data-miki-dialog="true"]', init: mikiDialog.init, name: "dialog" },
    { selector: '[data-miki-modal="true"]', init: mikiModal.init, name: "modal" },
    { selector: '[data-miki-slider="true"]', init: mikiSlider.init, name: "slider" },
    { selector: '[data-miki-dial="true"]', init: mikiDial.init, name: "dial" },
    { selector: '[data-miki-progress="true"]', init: mikiProgress.init, name: "progress" },
    { selector: '[data-miki-progress-dialog="true"]', init: mikiProgressDialog.init, name: "progressDialog" },
    { selector: '[data-miki-collapsible="true"]', init: mikiCollapsible.init, name: "collapsible" },
    { selector: '[data-miki-accordion="true"]', init: mikiAccordion.init, name: "accordion" },
    { selector: '[data-miki-datagrid="true"]', init: mikiDataGrid.init, name: "dataGrid" },
    { selector: '[data-miki-kanban="true"]', init: mikiKanban.init, name: "kanban" },
    { selector: '[data-miki-chat="true"]', init: mikiChat.init, name: "chat" },
    { selector: '[data-miki-dropzone="true"]', init: mikiDropzone.init, name: "dropzone" },
    { selector: '[data-miki-carousel="true"]', init: mikiCarousel.init, name: "carousel" },
    { selector: '[data-miki-messagebox="true"]', init: mikiMessageBox.init, name: "messageBox" },
    { selector: '[data-miki-context-window="true"]', init: mikiContextWindow.init, name: "contextWindow" },
    { selector: '[data-miki-menubar="true"]', init: mikiMenuBar.init, name: "menuBar" },
    { selector: '[data-miki-dockable="true"]', init: mikiDockablePanel.init, name: "dockable" },
    { selector: '[data-miki-splitview="true"]', init: mikiSplitView.init, name: "splitView" },
    { selector: '[data-miki-drawer="true"]', init: mikiDrawer.init, name: "drawer" },
    { selector: '[data-miki-toggle="true"]', init: mikiToggle.init, name: "toggle" },
    { selector: '[data-miki-searchable="true"]', init: mikiSearchableSelect.init, name: "searchable" },
  ];

  function initAll(scope) {
    scope = scope || document;

    for (var i = 0; i < widgetRegistry.length; i++) {
      var widgets = scope.querySelectorAll(widgetRegistry[i].selector);
      for (var j = 0; j < widgets.length; j++) {
        widgetRegistry[i].init(widgets[j]);
      }
    }

    // Drawer close buttons (inside the drawer container)
    var drawerCloseBtns = scope.querySelectorAll("[data-miki-drawer-close=\"true\"]");
    for (var d = 0; d < drawerCloseBtns.length; d++) {
      drawerCloseBtns[d].dataset.mikiInit = "true";
    }

    // Drawer overlay click-to-close
    var drawerOverlays = scope.querySelectorAll("[data-miki-drawer-overlay=\"true\"]");
    for (var o = 0; o < drawerOverlays.length; o++) {
      if (drawerOverlays[o].dataset.mikiInit === "true") continue;
      drawerOverlays[o].dataset.mikiInit = "true";
      (function (overlay) {
        on(overlay, "click", function () {
          var drawer = overlay.closest(".miki-drawer");
          if (drawer) {
            drawer.classList.remove("miki-drawer-open");
            drawer.setAttribute("aria-hidden", "true");
          }
        });
      })(drawerOverlays[o]);
    }

    // Drawer toggle buttons (external)
    var drawerToggles = scope.querySelectorAll("[data-miki-drawer-toggle=\"true\"]");
    for (var t = 0; t < drawerToggles.length; t++) {
      if (drawerToggles[t].dataset.mikiInit === "true") continue;
      drawerToggles[t].dataset.mikiInit = "true";
      (function (btn) {
        on(btn, "click", function (e) {
          e.preventDefault();
          var target = btn.getAttribute("data-miki-drawer-target");
          var drawer;
          if (target) {
            drawer = document.querySelector(target);
          } else {
            drawer = btn.closest(".miki-drawer") || document.querySelector(".miki-drawer");
          }
          if (drawer) {
            drawer.classList.toggle("miki-drawer-open");
            var isOpen = drawer.classList.contains("miki-drawer-open");
            drawer.setAttribute("aria-hidden", !isOpen);
            dispatch(drawer, "miki:drawer:toggled", { open: isOpen });
          }
        });
      })(drawerToggles[t]);
    }

    // Dockable panel action buttons (already bound via init, but handle
    // dynamically-added buttons)
    var dockActions = scope.querySelectorAll("[data-miki-dock-action]");
    for (var u = 0; u < dockActions.length; u++) {
      if (dockActions[u].dataset.mikiInit === "true") continue;
      dockActions[u].dataset.mikiInit = "true";
      (function (btn) {
        var action = btn.getAttribute("data-miki-dock-action");
        on(btn, "click", function (e) {
          e.preventDefault();
          var panel = btn.closest(".miki-dockable-panel");
          if (!panel) return;
          if (action === "toggle") mikiDockablePanel.toggle(panel);
          else if (action === "close") mikiDockablePanel.close(panel);
          else if (action === "detach") mikiDockablePanel.detach(panel);
        });
      })(dockActions[u]);
    }
  }

  /* ---- Global convenience functions (called from onclick attrs) ---- */

  window.mikiCloseDialog = function (btn) {
    var dlg = btn.closest("dialog");
    if (dlg) mikiDialog.close(dlg);
  };

  window.mikiClose = {
    dialog: function (btn) {
      var dlg = btn.closest("dialog");
      if (dlg) mikiDialog.close(dlg);
    },
    modal: function (btn) {
      var modal = btn.closest(".miki-modal");
      if (modal) mikiModal.close(modal);
    }
  };

  /* ---- Auto-init on DOM ready ---- */

  window.MikiUI = {
    init: initAll,
    initAll: initAll,
    version: "1.0",
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initAll();
    });
  } else {
    initAll();
  }

  /* ---- Re-init on HTMX swaps ---- */
  document.addEventListener("miki:swapped", function () {
    initAll();
  });

  /* ---- Re-init on standard HTMX events (fallback) ---- */
  document.addEventListener("htmx:afterSwap", function () {
    initAll();
  });

})();
