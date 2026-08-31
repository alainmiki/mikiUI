(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.MikiApp !== "undefined") return;

  /* ================================================================
   * MikiApp - Application lifecycle management.
   *
   * Provides:
   * 1. State persistence across app pauses/resumes
   * 2. Automatic save/restore of form data
   * 3. Session management
   * 4. App visibility tracking
   * ================================================================ */

  var STATE_KEY = "mikiui_app_state";
  var SESSION_KEY = "mikiui_session";
  var FORM_DATA_KEY = "mikiui_form_data";

  var _state = {};
  var _session = {};
  var _formData = {};
  var _listeners = { pause: [], resume: [], foreground: [], background: [] };
  var _isInitialized = false;

  /* --------------------------------------------------------
   * Event handling.
   * -------------------------------------------------------- */

  function _emit(type, data) {
    var handlers = _listeners[type] || [];
    for (var i = 0; i < handlers.length; i++) {
      try { handlers[i](data); } catch (e) { /* ignore */ }
    }
  }

  function on(event, callback) {
    if (!_listeners[event]) _listeners[event] = [];
    _listeners[event].push(callback);
    return function () {
      var idx = _listeners[event].indexOf(callback);
      if (idx !== -1) _listeners[event].splice(idx, 1);
    };
  }

  /* --------------------------------------------------------
   * State persistence.
   * -------------------------------------------------------- */

  function saveState() {
    try {
      var stateToSave = {
        __timestamp: Date.now(),
        __version: 1,
        data: _state,
      };
      localStorage.setItem(STATE_KEY, JSON.stringify(stateToSave));
    } catch (e) { /* ignore quota errors */ }
    return Promise.resolve();
  }

  function loadState() {
    try {
      var saved = localStorage.getItem(STATE_KEY);
      if (saved) {
        var parsed = JSON.parse(saved);
        _state = parsed.data || {};
      }
    } catch (e) { /* ignore parse errors */ }
    return Promise.resolve(_state);
  }

  function clearState() {
    _state = {};
    try { localStorage.removeItem(STATE_KEY); } catch (e) { /* ignore */ }
    return Promise.resolve();
  }

  function setState(key, value) {
    _state[key] = value;
    return saveState();
  }

  function getState(key, defaultValue) {
    return _state[key] !== undefined ? _state[key] : (defaultValue !== undefined ? defaultValue : null);
  }

  function removeState(key) {
    delete _state[key];
    return saveState();
  }

  /* --------------------------------------------------------
   * Session management.
   * -------------------------------------------------------- */

  function saveSession() {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify({
        __timestamp: Date.now(),
        data: _session,
      }));
    } catch (e) { /* ignore */ }
    return Promise.resolve();
  }

  function loadSession() {
    try {
      var saved = localStorage.getItem(SESSION_KEY);
      if (saved) {
        var parsed = JSON.parse(saved);
        _session = parsed.data || {};
      }
    } catch (e) { /* ignore */ }
    return Promise.resolve(_session);
  }

  function clearSession() {
    _session = {};
    try { localStorage.removeItem(SESSION_KEY); } catch (e) { /* ignore */ }
    return Promise.resolve();
  }

  function setSession(key, value) {
    _session[key] = value;
    return saveSession();
  }

  function getSession(key, defaultValue) {
    return _session[key] !== undefined ? _session[key] : (defaultValue !== undefined ? defaultValue : null);
  }

  function removeSession(key) {
    delete _session[key];
    return saveSession();
  }

  /* --------------------------------------------------------
   * Form data persistence (auto-save/restore).
   * -------------------------------------------------------- */

  function saveFormData(formId) {
    var forms = document.querySelectorAll('form[data-persist="' + formId + '"], form[data-persist="all"]');
    forms.forEach(function (form) {
      var data = new FormData(form);
      var obj = {};
      data.forEach(function (value, key) {
        obj[key] = value;
      });
      _formData[formId || form.id || "default"] = obj;
    });
    try {
      localStorage.setItem(FORM_DATA_KEY, JSON.stringify(_formData));
    } catch (e) { /* ignore */ }
    return Promise.resolve();
  }

  function restoreFormData(formId) {
    try {
      var saved = localStorage.getItem(FORM_DATA_KEY);
      if (saved) {
        _formData = JSON.parse(saved);
      }
    } catch (e) { /* ignore */ }

    var data = _formData[formId || "default"];
    if (!data) return Promise.resolve();

    Object.keys(data).forEach(function (key) {
      var input = document.querySelector('[name="' + key + '"]');
      if (input) {
        if (input.type === "checkbox") {
          input.checked = data[key] === "on" || data[key] === true;
        } else if (input.type === "radio") {
          var radio = document.querySelector('[name="' + key + '"][value="' + data[key] + '"]');
          if (radio) radio.checked = true;
        } else {
          input.value = data[key];
        }
      }
    });
    return Promise.resolve();
  }

  function clearFormData(formId) {
    if (formId) {
      delete _formData[formId];
    } else {
      _formData = {};
    }
    try { localStorage.setItem(FORM_DATA_KEY, JSON.stringify(_formData)); } catch (e) { /* ignore */ }
    return Promise.resolve();
  }

  /* --------------------------------------------------------
   * App lifecycle handling.
   * -------------------------------------------------------- */

  function init() {
    if (_isInitialized) return;
    _isInitialized = true;

    // Load saved state
    loadState();
    loadSession();

    // Setup Capacitor lifecycle events
    if (typeof window.Capacitor !== "undefined" && window.Capacitor.Plugins.App) {
      var App = window.Capacitor.Plugins.App;

      App.addListener("pause", function () {
        saveState();
        saveSession();
        _emit("pause", { timestamp: Date.now() });
      });

      App.addListener("resume", function () {
        loadState();
        loadSession();
        _emit("resume", { timestamp: Date.now() });
      });

      App.addListener("appUrlOpen", function (data) {
        _emit("urlOpen", data);
      });
    }

    // Web fallback: use visibility API
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) {
        saveState();
        saveSession();
        _emit("background", { timestamp: Date.now() });
      } else {
        loadState();
        loadSession();
        _emit("foreground", { timestamp: Date.now() });
      }
    });

    // Auto-save forms on input
    document.addEventListener("input", function (e) {
      var form = e.target.closest("form[data-persist]");
      if (form) {
        var formId = form.dataset.persist === "all" ? form.id || "default" : form.dataset.persist;
        saveFormData(formId);
      }
    });
  }

  /* --------------------------------------------------------
   * Public API.
   * -------------------------------------------------------- */

  var MikiApp = {
    // Initialization
    init: init,

    // State (persists across sessions)
    getState: getState,
    setState: setState,
    removeState: removeState,
    clearState: clearState,
    saveState: saveState,
    loadState: loadState,

    // Session (cleared on app restart)
    getSession: getSession,
    setSession: setSession,
    removeSession: removeSession,
    clearSession: clearSession,
    saveSession: saveSession,
    loadSession: loadSession,

    // Form data persistence
    saveFormData: saveFormData,
    restoreFormData: restoreFormData,
    clearFormData: clearFormData,

    // Event listeners
    on: on,

    // Utility
    isNative: function () {
      return typeof window.Capacitor !== "undefined" && window.Capacitor.isNativePlatform();
    },
    getPlatform: function () {
      if (typeof window.Capacitor !== "undefined") {
        try { return window.Capacitor.getPlatform(); } catch (e) {}
      }
      return "web";
    },
  };

  // Auto-initialize
  if (document.readyState === "complete" || document.readyState === "interactive") {
    init();
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }

  window.MikiApp = MikiApp;
})();
