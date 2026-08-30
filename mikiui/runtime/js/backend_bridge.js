(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.MikiBackend !== "undefined") return;

  /* ================================================================
   * MikiBackend — unified transport layer.
   *
   * Provides a single API for all platforms:
   *   - Web browser (standard fetch)
   *   - Desktop (pywebview direct call)
   *   - Mobile cloud (HTTPS fetch to remote backend)
   *   - Mobile on-device (Chaquopy @JavascriptInterface)
   *
   * The frontend NEVER knows which transport is active.
   * ================================================================ */

  var _config = {
    apiBase: "",
    wsBase: "",
    timeout: 30000,
  };

  var _pending = new Map();
  var _requestId = 0;

  function generateRequestId() {
    return "miki-req-" + (++_requestId) + "-" + Date.now().toString(36);
  }

  function isDesktop() {
    return typeof window.pywebview !== "undefined";
  }

  function isNative() {
    return typeof window.Capacitor !== "undefined";
  }

  function isChaquopy() {
    return typeof window.ChaquopyBridge !== "undefined";
  }

  function detectTransport() {
    if (isDesktop()) return "desktop";
    if (isChaquopy()) return "ondevice";
    if (isNative()) return "cloud";
    return "web";
  }

  function buildUrl(path) {
    if (path.indexOf("http://") === 0 || path.indexOf("https://") === 0) {
      return path;
    }
    var base = _config.apiBase || "";
    if (base && base.charAt(base.length - 1) === "/") {
      base = base.slice(0, -1);
    }
    var p = path.charAt(0) === "/" ? path : "/" + path;
    return base + p;
  }

  function buildWsUrl(path) {
    var base = _config.wsBase || "";
    if (!base) {
      // Derive WS base from apiBase
      var api = _config.apiBase || window.location.origin;
      if (api.indexOf("https://") === 0) {
        base = "wss://" + api.slice(8);
      } else if (api.indexOf("http://") === 0) {
        base = "ws://" + api.slice(7);
      } else {
        base = (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host;
      }
    }
    if (base.charAt(base.length - 1) === "/") {
      base = base.slice(0, -1);
    }
    var p = path.charAt(0) === "/" ? path : "/" + path;
    return base + p;
  }

  function webCall(method, path, data) {
    var url = buildUrl(path);
    var options = {
      method: method.toUpperCase(),
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    };
    if (data && method.toUpperCase() !== "GET") {
      options.body = JSON.stringify(data);
    }
    return fetch(url, options).then(function (response) {
      return response.json().catch(function () {
        return { status: response.status, ok: response.ok };
      });
    });
  }

  function desktopCall(method, path, data) {
    return new Promise(function (resolve, reject) {
      try {
        var payload = JSON.stringify({ method: method.toUpperCase(), path: path, data: data || null });
        window.pywebview.api.backendCall(payload).then(function (result) {
          try {
            resolve(JSON.parse(result));
          } catch (e) {
            resolve({ data: result, status: "ok" });
          }
        }).catch(reject);
      } catch (e) {
        reject(e);
      }
    });
  }

  function ondeviceCall(method, path, data) {
    return new Promise(function (resolve, reject) {
      try {
        var payload = JSON.stringify({ method: method.toUpperCase(), path: path, data: data || null });
        var result = window.ChaquopyBridge.backendCall(payload);
        try {
          resolve(JSON.parse(result));
        } catch (e) {
          resolve({ data: result, status: "ok" });
        }
      } catch (e) {
        reject(e);
      }
    });
  }

  function dispatchCall(method, path, data) {
    var transport = detectTransport();
    switch (transport) {
      case "desktop":
        return desktopCall(method, path, data);
      case "ondevice":
        return ondeviceCall(method, path, data);
      case "cloud":
      case "web":
      default:
        return webCall(method, path, data);
    }
  }

  /* --------------------------------------------------------
   * WebSocket subscription with platform-aware URL routing.
   * -------------------------------------------------------- */

  function subscribe(path, onMessage, onError) {
    var url = buildWsUrl(path);
    var ws;
    try {
      ws = new WebSocket(url);
    } catch (e) {
      if (onError) onError(e);
      return null;
    }

    ws.onmessage = function (event) {
      try {
        var data = JSON.parse(event.data);
        if (onMessage) onMessage(data);
      } catch (e) {
        if (onMessage) onMessage(event.data);
      }
    };

    ws.onerror = function (event) {
      if (onError) onError(event);
    };

    return {
      send: function (data) {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(typeof data === "string" ? data : JSON.stringify(data));
        }
      },
      close: function () {
        ws.close();
      },
      get readyState() {
        return ws.readyState;
      },
    };
  }

  /* --------------------------------------------------------
   * Public API
   * -------------------------------------------------------- */

  var MikiBackend = {
    /* Configuration */
    config: function (opts) {
      if (opts.apiBase !== undefined) _config.apiBase = opts.apiBase;
      if (opts.wsBase !== undefined) _config.wsBase = opts.wsBase;
      if (opts.timeout !== undefined) _config.timeout = opts.timeout;
      return Object.assign({}, _config);
    },

    get: function (path, data) { return dispatchCall("GET", path, data); },
    post: function (path, data) { return dispatchCall("POST", path, data); },
    put: function (path, data) { return dispatchCall("PUT", path, data); },
    patch: function (path, data) { return dispatchCall("PATCH", path, data); },
    delete: function (path, data) { return dispatchCall("DELETE", path, data); },
    call: function (method, path, data) { return dispatchCall(method, path, data); },

    /* WebSocket */
    subscribe: subscribe,

    /* Platform detection */
    isDesktop: isDesktop,
    isNative: isNative,
    isChaquopy: isChaquopy,
    transport: detectTransport,

    /* Utilities */
    buildUrl: buildUrl,
    buildWsUrl: buildWsUrl,
  };

  window.MikiBackend = MikiBackend;
})();
