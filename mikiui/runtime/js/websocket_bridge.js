(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.MikiWebSocket !== "undefined") return;

  /* ================================================================
   * MikiWebSocket — platform-aware WebSocket URL selection.
   *
   * Automatically selects the correct WebSocket URL based on:
   *   - Current platform (web/desktop/mobile-cloud/mobile-ondevice)
   *   - Configured backend URL
   *   - Fallback to same-origin
   *
   * Also handles reconnection with exponential backoff.
   * ================================================================ */

  var DEFAULTS = {
    maxReconnectAttempts: 5,
    baseDelay: 1000,
    maxDelay: 30000,
    pingInterval: 25000,
  };

  function detectPlatform() {
    if (typeof window.pywebview !== "undefined") return "desktop";
    if (typeof window.ChaquopyBridge !== "undefined") return "ondevice";
    if (typeof window.Capacitor !== "undefined") return "cloud";
    return "web";
  }

  function deriveWsUrl(apiBase, path) {
    var base = apiBase || "";

    // If apiBase is already a ws:// or wss:// URL, use it directly
    if (base.indexOf("ws://") === 0 || base.indexOf("wss://") === 0) {
      return base.replace(/\/$/, "") + (path.charAt(0) === "/" ? path : "/" + path);
    }

    // Derive WS scheme from HTTP scheme
    var wsScheme = "ws://";
    if (base.indexOf("https://") === 0) {
      wsScheme = "wss://";
      base = base.slice(8);
    } else if (base.indexOf("http://") === 0) {
      base = base.slice(7);
    } else {
      // No scheme — use current origin
      var origin = window.location.origin;
      wsScheme = origin.indexOf("https:") === 0 ? "wss://" : "ws://";
      base = window.location.host;
    }

    // Remove trailing slash from base
    base = base.replace(/\/$/, "");
    var p = path.charAt(0) === "/" ? path : "/" + path;
    return wsScheme + base + p;
  }

  function getPlatformDefaults() {
    var platform = detectPlatform();
    switch (platform) {
      case "desktop":
        return { wsBase: "ws://127.0.0.1:8000" };
      case "ondevice":
        return { wsBase: "ws://127.0.0.1:8080" };
      case "cloud":
      case "web":
      default:
        return {};
    }
  }

  /* --------------------------------------------------------
   * Managed WebSocket connection with auto-reconnect.
   * -------------------------------------------------------- */

  function ManagedWebSocket(url, options) {
    options = options || {};
    var _ws = null;
    var _attempts = 0;
    var _closed = false;
    var _pingTimer = null;
    var _listeners = { open: [], message: [], close: [], error: [] };

    var _config = {
      maxReconnectAttempts: options.maxReconnectAttempts || DEFAULTS.maxReconnectAttempts,
      baseDelay: options.baseDelay || DEFAULTS.baseDelay,
      maxDelay: options.maxDelay || DEFAULTS.maxDelay,
      pingInterval: options.pingInterval !== undefined ? options.pingInterval : DEFAULTS.pingInterval,
    };

    function connect() {
      if (_closed) return;
      try {
        _ws = new WebSocket(url);
      } catch (e) {
        _emit("error", e);
        scheduleReconnect();
        return;
      }

      _ws.onopen = function () {
        _attempts = 0;
        _emit("open");
        if (_config.pingInterval > 0) {
          _pingTimer = setInterval(function () {
            if (_ws && _ws.readyState === WebSocket.OPEN) {
              _ws.send("__ping__");
            }
          }, _config.pingInterval);
        }
      };

      _ws.onmessage = function (event) {
        if (event.data === "__pong__" || event.data === "__ping__") return;
        _emit("message", event.data);
      };

      _ws.onclose = function (event) {
        if (_pingTimer) { clearInterval(_pingTimer); _pingTimer = null; }
        _emit("close", event);
        if (!_closed) scheduleReconnect();
      };

      _ws.onerror = function (event) {
        _emit("error", event);
      };
    }

    function scheduleReconnect() {
      if (_closed || _attempts >= _config.maxReconnectAttempts) return;
      _attempts++;
      var delay = Math.min(_config.baseDelay * Math.pow(2, _attempts - 1), _config.maxDelay);
      setTimeout(function () {
        if (!_closed) connect();
      }, delay);
    }

    function _emit(type, data) {
      for (var i = 0; i < _listeners[type].length; i++) {
        try { _listeners[type][i](data); } catch (e) { /* ignore listener errors */ }
      }
    }

    connect();

    return {
      send: function (data) {
        if (_ws && _ws.readyState === WebSocket.OPEN) {
          _ws.send(typeof data === "string" ? data : JSON.stringify(data));
        }
      },
      close: function () {
        _closed = true;
        if (_pingTimer) { clearInterval(_pingTimer); _pingTimer = null; }
        if (_ws) _ws.close();
      },
      on: function (type, handler) {
        if (_listeners[type]) _listeners[type].push(handler);
      },
      off: function (type, handler) {
        if (!_listeners[type]) return;
        var idx = _listeners[type].indexOf(handler);
        if (idx !== -1) _listeners[type].splice(idx, 1);
      },
      get readyState() { return _ws ? _ws.readyState : WebSocket.CLOSED; },
      get url() { return url; },
    };
  }

  /* --------------------------------------------------------
   * Public API
   * -------------------------------------------------------- */

  var MikiWebSocket = {
    detectPlatform: detectPlatform,
    deriveWsUrl: deriveWsUrl,
    getPlatformDefaults: getPlatformDefaults,

    connect: function (path, options) {
      var apiBase = (window.MikiBackend && window.MikiBackend.config().apiBase) || "";
      var url = deriveWsUrl(apiBase, path);
      return ManagedWebSocket(url, options);
    },

    connectUrl: function (url, options) {
      return ManagedWebSocket(url, options);
    },
  };

  window.MikiWebSocket = MikiWebSocket;
})();
