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

  /* ===================== Safe Action Dispatcher ===================== */
  var ALLOWED_ACTIONS = [
    "call", "callSafe", "dispatch", "emit", "on", "off",
    "toggle", "open", "close", "submit", "navigate", "toggleClass", "remove"
  ];

  function parseArgs(argsStr) {
    var args = [];
    var current = "";
    var depth = 0;
    var inString = false;
    var stringChar = "";

    for (var i = 0; i < argsStr.length; i++) {
      var c = argsStr[i];
      if (inString) {
        current += c;
        if (c === stringChar && argsStr[i - 1] !== "\\") {
          inString = false;
        }
      } else if (c === '"' || c === "'" || c === "`") {
        inString = true;
        stringChar = c;
        current += c;
      } else if (c === "(" || c === "[" || c === "{") {
        depth++;
        current += c;
      } else if (c === ")" || c === "]" || c === "}") {
        depth--;
        current += c;
      } else if (c === "," && depth === 0) {
        args.push(current.trim());
        current = "";
      } else {
        current += c;
      }
    }

    if (current.trim()) {
      args.push(current.trim());
    }

    return args;
  }

  function evaluateArg(arg, context) {
    arg = arg.trim();
    if (!arg) return undefined;

    if (
      (arg[0] === '"' && arg[arg.length - 1] === '"') ||
      (arg[0] === "'" && arg[arg.length - 1] === "'")
    ) {
      return arg.slice(1, -1);
    }

    if (
      !isNaN(arg) &&
      arg !== "" &&
      arg !== "true" &&
      arg !== "false" &&
      arg !== "null" &&
      arg !== "undefined"
    ) {
      return parseFloat(arg);
    }

    if (arg === "true") return true;
    if (arg === "false") return false;
    if (arg === "null") return null;
    if (arg === "undefined") return undefined;

    if (arg === "this") return context.el;
    if (arg === "event" || arg === "e") return context.event;
    if (arg === "window") return window;
    if (arg === "document") return document;

    return undefined;
  }

  function evaluateObjectLiteral(str, context) {
    str = str.trim();
    if (!str || str === "{}") return {};

    if (str[0] === "{" && str[str.length - 1] === "}") {
      str = str.slice(1, -1).trim();
    }

    var obj = {};
    var pairs = [];
    var current = "";
    var depth = 0;
    var inString = false;
    var stringChar = "";

    for (var i = 0; i < str.length; i++) {
      var c = str[i];
      if (inString) {
        current += c;
        if (c === stringChar && str[i - 1] !== "\\") {
          inString = false;
        }
      } else if (c === '"' || c === "'" || c === "`") {
        inString = true;
        stringChar = c;
        current += c;
      } else if (c === "(" || c === "[" || c === "{") {
        depth++;
        current += c;
      } else if (c === ")" || c === "]" || c === "}") {
        depth--;
        current += c;
      } else if (c === "," && depth === 0) {
        pairs.push(current.trim());
        current = "";
      } else {
        current += c;
      }
    }
    if (current.trim()) pairs.push(current.trim());

    for (var j = 0; j < pairs.length; j++) {
      var pair = pairs[j];
      var colonIdx = -1;
      var pd = 0;
      var pis = false;
      var psc = "";

      for (var k = 0; k < pair.length; k++) {
        var ch = pair[k];
        if (pis) {
          if (ch === psc && pair[k - 1] !== "\\") pis = false;
        } else if (ch === '"' || ch === "'" || ch === "`") {
          pis = true;
          psc = ch;
        } else if (ch === "(" || ch === "[" || ch === "{") {
          pd++;
        } else if (ch === ")" || ch === "]" || ch === "}") {
          pd--;
        } else if (ch === ":" && pd === 0) {
          colonIdx = k;
          break;
        }
      }

      if (colonIdx !== -1) {
        var key = pair.substring(0, colonIdx).trim();
        var val = pair.substring(colonIdx + 1).trim();

        if (
          (key[0] === '"' && key[key.length - 1] === '"') ||
          (key[0] === "'" && key[key.length - 1] === "'")
        ) {
          key = key.slice(1, -1);
        }

        obj[key] = evaluateArg(val, context);
      }
    }

    return obj;
  }

  function evaluateSafeExpression(expr, context) {
    if (!/^(this|event|self)(?:\.[a-zA-Z_$][\w$]*(?:\([^)]*\))?)*$/.test(expr)) {
      return undefined;
    }

    var tokens = [];
    var i = 0;
    while (i < expr.length) {
      if (expr[i] === ".") {
        i++;
        continue;
      }

      var nameStart = i;
      while (i < expr.length && /[a-zA-Z_$]/.test(expr[i])) {
        i++;
      }
      var name = expr.substring(nameStart, i);

      if (expr[i] === "(") {
        var depth = 1;
        var j = i + 1;
        while (j < expr.length && depth > 0) {
          if (expr[j] === "(") depth++;
          else if (expr[j] === ")") depth--;
          j++;
        }
        var argsStr = expr.substring(i + 1, j - 1);
        tokens.push({ type: "method", name: name, args: argsStr });
        i = j;
      } else {
        tokens.push({ type: "property", name: name });
      }
    }

    if (tokens.length === 0) return undefined;

    var obj;
    var root = tokens[0];
    if (root.name === "this") obj = context.el;
    else if (root.name === "event") obj = context.event;
    else if (root.name === "self") obj = context.el;
    else if (root.name === "window") obj = window;
    else if (root.name === "document") obj = document;
    else return undefined;

    for (var k = 1; k < tokens.length; k++) {
      if (obj == null) return undefined;
      var token = tokens[k];

      if (token.type === "property") {
        obj = obj[token.name];
      } else if (token.type === "method") {
        var args = parseArgs(token.args).map(function (a) {
          return evaluateArg(a, context);
        });
        if (typeof obj[token.name] === "function") {
          obj = obj[token.name].apply(obj, args);
        } else {
          return undefined;
        }
      }
    }

    return obj;
  }

  function executeSafeAction(eExpr, context) {
    var match = eExpr.match(/^mikiBridge\.([a-zA-Z_$][\w$]*)\s*\((.*)\)$/s);
    if (!match) {
      console.warn("MikiUI: Unauthorized action expression skipped:", eExpr);
      return;
    }

    var method = match[1];
    if (ALLOWED_ACTIONS.indexOf(method) === -1) {
      console.warn("MikiUI: Disallowed action method:", method);
      return;
    }

    var rawArgs = parseArgs(match[2]);

    switch (method) {
      case "call": {
        if (rawArgs.length < 2) return;
        var moduleName = evaluateArg(rawArgs[0], context);
        var fnName = evaluateArg(rawArgs[1], context);
        var restArgs = rawArgs.slice(2).map(function (a) {
          return evaluateArg(a, context);
        });
        return mikiBridge.call(moduleName, fnName, restArgs);
      }
      case "dispatch": {
        if (rawArgs.length < 2) return;
        var target = evaluateArg(rawArgs[0], context);
        var name = evaluateArg(rawArgs[1], context);
        var result = rawArgs[2] ? executeSafeAction(rawArgs[2], context) : undefined;
        var detail = rawArgs[3] ? evaluateObjectLiteral(rawArgs[3], context) : undefined;
        return mikiBridge.dispatch(target, name, result, detail);
      }
      case "callSafe": {
        if (rawArgs.length < 2) return;
        var fnBody = rawArgs[0].trim();
        var thisArg = evaluateArg(rawArgs[1], context);

        var expr = fnBody;
        var funcWrapMatch = fnBody.match(/^function\s*\([^)]*\)\s*\{([\s\S]*)\}$/);
        if (funcWrapMatch) {
          expr = funcWrapMatch[1].trim();
        }

        var callMatch = expr.match(/^mikiBridge\.call\s*\((.*)\)$/s);
        if (callMatch) {
          var callArgs = parseArgs(callMatch[1]);
          if (callArgs.length >= 2) {
            var mod = evaluateArg(callArgs[0], context);
            var fun = evaluateArg(callArgs[1], context);
            var rest = callArgs.slice(2).map(function (a) {
              return evaluateArg(a, context);
            });
            return mikiBridge.call(mod, fun, rest);
          }
        }

        try {
          var fn = new Function(expr);
          return fn.call(thisArg);
        } catch (err) {
          console.warn("MikiUI: callSafe execution error:", err.message);
          return undefined;
        }
      }
      default: {
        var methodArgs = rawArgs.map(function (a) {
          return evaluateArg(a, context);
        });
        return mikiBridge[method].apply(mikiBridge, methodArgs);
      }
    }
  }

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

      var _swapObserver = null;

      document.addEventListener("htmx:beforeSwap", function (evt) {
        var target = evt.detail && evt.detail.target ? evt.detail.target : null;
        if (!target || target.nodeType !== 1) return;

        _swapObserver = new MutationObserver(function (mutations) {
          mutations.forEach(function (mutation) {
            mutation.removedNodes.forEach(function (node) {
              if (node.nodeType === 1) {
                if (typeof window.mikiDestroy === "function") {
                  window.mikiDestroy(node);
                }
              }
            });
          });
        });

        _swapObserver.observe(target, { childList: true, subtree: true });
      });

      document.addEventListener("htmx:afterSwap", function (evt) {
        if (_swapObserver) {
          _swapObserver.disconnect();
          _swapObserver = null;
        }

        var target = evt.detail && evt.detail.target ? evt.detail.target : null;
        if (target) {
          mikiBridge.initElement(target);
        }
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
                executeSafeAction(eExpr, { el: el, event: e });
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
            var widget = widgets[j];
            var tag = widget && widget.dataset ? widget.dataset.mikiWidgetInit : null;
            if (tag === entry.name) continue;
            try {
              entry.init(widget);
              if (widget && widget.dataset) {
                widget.dataset.mikiWidgetInit = entry.name;
              }
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

    toggle: function (el) {
      if (mikiToggle && typeof mikiToggle.toggle === "function")
        return mikiToggle.toggle(el);
      if (mikiCollapsible && typeof mikiCollapsible.toggle === "function")
        return mikiCollapsible.toggle(el);
      if (mikiModal && typeof mikiModal.toggle === "function") return mikiModal.toggle(el);
      return undefined;
    },

    open: function (el) {
      if (mikiDialog && typeof mikiDialog.open === "function") return mikiDialog.open(el);
      if (mikiModal && typeof mikiModal.open === "function") return mikiModal.open(el);
      if (mikiDrawer && typeof mikiDrawer.open === "function") return mikiDrawer.open(el);
      if (mikiBottomSheet && typeof mikiBottomSheet.open === "function")
        return mikiBottomSheet.open(el);
      return undefined;
    },

    close: function (el) {
      if (mikiDialog && typeof mikiDialog.close === "function") return mikiDialog.close(el);
      if (mikiModal && typeof mikiModal.close === "function") return mikiModal.close(el);
      if (mikiDrawer && typeof mikiDrawer.close === "function") return mikiDrawer.close(el);
      if (mikiBottomSheet && typeof mikiBottomSheet.close === "function")
        return mikiBottomSheet.close(el);
      return undefined;
    },

    submit: function (el) {
      if (el && el.form) return el.form.submit();
      return undefined;
    },

    navigate: function (url) {
      if (typeof url === "string") window.location.href = url;
    },

    toggleClass: function (el, className) {
      if (el && className) el.classList.toggle(className);
    },

    remove: function (el) {
      if (el && el.parentNode) el.parentNode.removeChild(el);
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

