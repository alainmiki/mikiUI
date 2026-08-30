(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.MikiEvents !== "undefined") return;

  /* ================================================================
   * MikiEvents — bidirectional JS <-> Python event bus.
   *
   * Allows JavaScript to emit events that Python handlers can listen to,
   * and Python to push events to JavaScript. Works across all platforms
   * (web, desktop, mobile-cloud, mobile-ondevice).
   *
   * Usage:
   *   // JS -> Python
   *   MikiEvents.emit('location_changed', { lat: 48.8566, lng: 2.3522 });
   *
   *   // Python -> JS (pushed via WebSocket)
   *   MikiEvents.on('notification', (data) => { ... });
   * ================================================================ */

  var _listeners = {};
  var _pyHandlers = {};
  var _ws = null;
  var _eventQueue = [];
  var _isConnected = false;

  function on(event, handler) {
    if (!_listeners[event]) _listeners[event] = [];
    _listeners[event].push(handler);
    return function () {
      var idx = _listeners[event].indexOf(handler);
      if (idx !== -1) _listeners[event].splice(idx, 1);
    };
  }

  function off(event, handler) {
    if (!_listeners[event]) return;
    var idx = _listeners[event].indexOf(handler);
    if (idx !== -1) _listeners[event].splice(idx, 1);
  }

  function emit(event, data) {
    // Dispatch to local JS listeners
    _dispatch(event, data);
    // Forward to Python backend
    _sendToPython(event, data);
  }

  function _dispatch(event, data) {
    var handlers = _listeners[event] || [];
    for (var i = 0; i < handlers.length; i++) {
      try { handlers[i](data); } catch (e) { /* ignore */ }
    }
  }

  function _sendToPython(event, data) {
    var payload = JSON.stringify({ type: "event", event: event, data: data, timestamp: Date.now() });
    if (_ws && _ws.readyState === WebSocket.OPEN) {
      _ws.send(payload);
    } else {
      // Queue for later delivery
      _eventQueue.push(payload);
      // Also try HTTP fallback
      _httpFallback(event, data);
    }
  }

  function _httpFallback(event, data) {
    if (typeof window.MikiBackend !== "undefined") {
      window.MikiBackend.post("/_miki/events", { event: event, data: data }).catch(function () {
        /* ignore — event will be queued */
      });
    }
  }

  /* --------------------------------------------------------
   * Python -> JS event reception.
   * -------------------------------------------------------- */

  function handlePythonEvent(event, data) {
    _dispatch(event, data);
  }

  /* --------------------------------------------------------
   * WebSocket connection for real-time events.
   * -------------------------------------------------------- */

  function connect(wsUrl) {
    if (_ws) { _ws.close(); }
    try {
      _ws = new WebSocket(wsUrl);
    } catch (e) {
      console.warn("[MikiEvents] WebSocket connection failed:", e);
      return;
    }

    _ws.onopen = function () {
      _isConnected = true;
      // Flush queued events
      while (_eventQueue.length > 0) {
        var payload = _eventQueue.shift();
        _ws.send(payload);
      }
    };

    _ws.onmessage = function (e) {
      try {
        var msg = JSON.parse(e.data);
        if (msg.type === "event" && msg.event) {
          handlePythonEvent(msg.event, msg.data);
        }
      } catch (err) {
        /* ignore malformed messages */
      }
    };

    _ws.onclose = function () {
      _isConnected = false;
    };

    _ws.onerror = function () {
      _isConnected = false;
    };
  }

  function disconnect() {
    if (_ws) {
      _ws.close();
      _ws = null;
    }
    _isConnected = false;
  }

  /* --------------------------------------------------------
   * Auto-connect if MikiWebSocket is available.
   * -------------------------------------------------------- */

  function autoConnect() {
    if (typeof window.MikiWebSocket !== "undefined") {
      var basePath = "/_miki/events/ws";
      if (typeof window.MikiBackend !== "undefined") {
        var cfg = window.MikiBackend.config();
        if (cfg.wsBase) {
          _ws = window.MikiWebSocket.connect(basePath);
          return;
        }
      }
      connect(basePath);
    }
  }

  // Attempt auto-connect on load
  if (document.readyState === "complete") {
    autoConnect();
  } else {
    document.addEventListener("DOMContentLoaded", autoConnect);
  }

  /* --------------------------------------------------------
   * Public API
   * -------------------------------------------------------- */

  var MikiEvents = {
    on: on,
    off: off,
    emit: emit,
    connect: connect,
    disconnect: disconnect,
    handlePythonEvent: handlePythonEvent,
    get isConnected() { return _isConnected; },
  };

  window.MikiEvents = MikiEvents;
})();
