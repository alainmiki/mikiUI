(function () {
  "use strict";

  var miki = window.miki || {};

  /* ===================== MikiUI Bridge =====================
   * Centralized event dispatch and widget-function lookup.
   *
   * All component/widget interactivity routes through mikiBridge so that:
   *   - Missing modules do not throw ReferenceErrors (safe .call / .callSafe)
   *   - DOM events, CustomEvents, HTMX swaps, SSE, and WebSocket
   *     messages are handled through one consistent API.
   *   - Auto-init works on dynamically injected content.
   */

  /* Track elements that have already had their data-miki-on bound to
     prevent duplicate handlers when initAll runs multiple times. */
  var _boundElements = (typeof WeakSet !== "undefined") ? new WeakSet() : null;

  var mikiBridge = {
    /* -- Safe widget function lookup -- */

    /**
     * Safely call a widget function like "mikiTabs.show".
     * Returns undefined (no throw) if the module or method is missing.
     */
    call: function (moduleName, fnName) {
      var module = window[moduleName];
      if (!module || typeof module[fnName] !== "function") {
        return undefined;
      }
      var args = Array.prototype.slice.call(arguments, 2);
      return module[fnName].apply(module, args);
    },

    /**
     * Check whether a widget module and method are available.
     */
    has: function (moduleName, fnName) {
      var module = window[moduleName];
      return !!(module && typeof module[fnName] === "function");
    },

    /**
     * Execute a function in a try/catch, returning its result or undefined.
     * The *thisArg* is bound as `this` inside the function.
     * Used by the auto-generated dispatch handlers from data-miki-on.
     */
    callSafe: function (fn, thisArg) {
      try {
        return fn.call(thisArg);
      } catch (e) {
        return undefined;
      }
    },

    /* -- Event dispatching -- */

    /**
     * Dispatch a CustomEvent on a target element.
     *   target: DOM element, window, or document
     *   name:   event name (without "miki:" prefix -- it is added)
     *   result: value returned by the action expression (passed through)
     *   detail: detail payload (object)
     */
    dispatch: function (target, name, result, detail) {
      if (!target) return result;
      var eventName = name.indexOf(":") === 0 ? name : "miki:" + name;
      var event = new CustomEvent(eventName, {
        detail: detail || {},
        bubbles: true,
        cancelable: true,
      });
      target.dispatchEvent(event);
      return result;
    },

    /**
     * Dispatch a global event (on window).
     */
    emit: function (name, detail) {
      return mikiBridge.dispatch(window, name, undefined, detail);
    },

    /* -- Event listening -- */

    on: function (el, event, handler, opts) {
      miki.on(el, event, handler, opts);
    },

    off: function (el, event, handler, opts) {
      miki.off(el, event, handler, opts);
    },

    /* -- HTMX integration -- */

    /**
     * Listen for HTMX swap completion and re-init MikiUI widgets
     * in the swapped content.
     */
    initHtmxRuntime: function () {
      var htmxAvailable = typeof htmx !== "undefined" && htmx;
      if (htmxAvailable && typeof htmx.addInitCallback === "function") {
        htmx.addInitCallback(function (elt) {
          mikiBridge.initElement(elt);
        });
      }

      document.addEventListener("htmx:afterSwap", function (evt) {
        var target = evt.detail && evt.detail.target ? evt.detail.target : null;
        if (target) {
          mikiBridge.initElement(target);
        }
      });

      document.addEventListener("htmx:afterOnLoad", function () {
        mikiBridge.initAll();
      });
    },

    /* -- SSE integration -- */

    /**
     * Connect to a Server-Sent Events endpoint and dispatch
     * miki:sse:<channel> events for each message.
     */
    connectSSE: function (url, channel) {
      var evtSource = new EventSource(url);
      evtSource.addEventListener("message", function (event) {
        var data = event.data;
        try {
          data = JSON.parse(event.data);
        } catch (e) {
          /* keep raw string */
        }
        mikiBridge.emit(channel || "sse", data);
      });
      return evtSource;
    },

    /* -- WebSocket integration -- */

    /**
     * Connect to a WebSocket and dispatch miki:ws:<channel> events.
     * Returns the WebSocket instance.
     */
    connectWebSocket: function (url, channel) {
      var ws = new WebSocket(url);
      var chan = channel || "ws";

      ws.addEventListener("open", function () {
        mikiBridge.emit(chan + ":open", {});
      });
      ws.addEventListener("message", function (event) {
        var data = event.data;
        try {
          data = JSON.parse(event.data);
        } catch (e) {
          /* keep raw string */
        }
        mikiBridge.emit(chan + ":message", data);
      });
      ws.addEventListener("close", function () {
        mikiBridge.emit(chan + ":close", {});
      });
      ws.addEventListener("error", function (event) {
        mikiBridge.emit(chan + ":error", event);
      });

      return ws;
    },

    /* -- Auto-init from data attributes -- */

    /**
     * Parse a ``data-miki-on`` attribute and bind event listeners.
     * Each binding is ``eventName::jsExpression``.
     * Multiple bindings are separated by ``~|``.
     */
    applyBindings: function (el) {
      if (!el || !el.getAttribute) return;
      if (_boundElements && _boundElements.has(el)) return;
      var raw = el.getAttribute("data-miki-on");
      if (!raw) return;
      if (_boundElements) _boundElements.add(el);

      var bindings = raw.split("~|");
      for (var i = 0; i < bindings.length; i++) {
        var binding = bindings[i].trim();
        if (!binding) continue;

        var sep = binding.indexOf("::");
        if (sep === -1) continue;

        var eventName = binding.substring(0, sep).trim();
        var expr = binding.substring(sep + 2).trim();

        if (eventName && expr) {
          (function (eName, eExpr) {
            miki.on(el, eName, function (e) {
              try {
                var fn = new Function("event", "return (" + eExpr + ");");
                fn.call(el, e);
              } catch (err) {
                /* Silently ignore handler errors */
              }
            });
          })(eventName, expr);
        }
      }
    },

    /**
     * Initialize MikiUI behaviour on a single element (and its children).
     */
    initElement: function (root) {
      if (!root) return;

      /* 1. Widget auto-init (data-miki-* attributes) */
      if (root.nodeType === 1) {
        mikiBridge.initWidgets(root);
      }

      /* 2. Apply data-miki-on bindings */
      mikiBridge.applyBindings(root);

      /* 3. Traverse children with data-miki-on */
      if (root.nodeType === 1) {
        var children = root.querySelectorAll("*[data-miki-on]");
        for (var i = 0; i < children.length; i++) {
          mikiBridge.applyBindings(children[i]);
        }
      }
    },

    /**
     * Initialize all widgets matching the registry selectors within a scope.
     */
    initWidgets: function (scope) {
      var registry = window.__mikiInitRegistry;
      if (!registry) return;

      for (var i = 0; i < registry.length; i++) {
        var entry = registry[i];
        if (entry.init && typeof entry.init === "function") {
          var widgets;
          if (scope === document) {
            widgets = document.querySelectorAll(entry.selector);
          } else if (scope.matches) {
            widgets = scope.matches(entry.selector)
              ? [scope]
              : scope.querySelectorAll(entry.selector);
          } else {
            widgets = [];
          }
          for (var j = 0; j < widgets.length; j++) {
            try {
              entry.init(widgets[j]);
            } catch (e) {
              /* Widget init failed -- do not break the page */
            }
          }
        }
      }
    },

    /**
     * Initialize everything on the page (full scan).
     */
    initAll: function () {
      mikiBridge.initWidgets(document);
      mikiBridge.initElement(document.body);
    },

    /* -- Registry management -- */

    /**
     * Register a widget init function for auto-initialization.
     *   selector: CSS selector to find widget elements
     *   name:     widget name (for debugging)
     *   init:     init function(element)
     */
    register: function (selector, name, init) {
      if (!window.__mikiInitRegistry) {
        window.__mikiInitRegistry = [];
      }
      window.__mikiInitRegistry.push({ selector: selector, name: name, init: init });
    },
  };

  window.mikiBridge = mikiBridge;

  /* Export to miki namespace as well */
  if (miki) {
    miki.bridge = mikiBridge;
  }

  /* If called before document ready, defer -- otherwise auto-init */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      mikiBridge.initAll();
      mikiBridge.initHtmxRuntime();
    });
  } else {
    mikiBridge.initAll();
    mikiBridge.initHtmxRuntime();
  }
})();

