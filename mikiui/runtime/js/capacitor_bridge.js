(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.MikiCapacitor !== "undefined") return;

  /* ================================================================
   * MikiCapacitor — platform detection and Capacitor plugin wrappers.
   *
   * Detects the runtime environment (web, desktop, Capacitor native)
   * and provides unified access to native device features through
   * Capacitor plugins.
   * ================================================================ */

  var _plugins = {};
  var _isReady = false;
  var _readyCallbacks = [];

  function isCapacitor() {
    return typeof window.Capacitor !== "undefined" && window.Capacitor.isNativePlatform();
  }

  function isPluginAvailable(name) {
    if (!isCapacitor()) return false;
    return window.Capacitor.isPluginAvailable(name);
  }

  function getPlatform() {
    if (typeof window.pywebview !== "undefined") return "desktop";
    if (!isCapacitor()) return "web";
    try {
      return window.Capacitor.getPlatform();
    } catch (e) {
      return "web";
    }
  }

  function onReady(callback) {
    if (_isReady) {
      callback();
    } else {
      _readyCallbacks.push(callback);
    }
  }

  function _setReady() {
    _isReady = true;
    for (var i = 0; i < _readyCallbacks.length; i++) {
      try { _readyCallbacks[i](); } catch (e) { /* ignore */ }
    }
    _readyCallbacks = [];
  }

  /* --------------------------------------------------------
   * Safe plugin access — returns a no-op proxy if plugin missing.
   * -------------------------------------------------------- */

  function getPlugin(name) {
    if (_plugins[name]) return _plugins[name];
    if (!isPluginAvailable(name)) {
      return _createNoOpPlugin(name);
    }
    try {
      var plugin = window.Capacitor.Plugins[name];
      _plugins[name] = plugin;
      return plugin;
    } catch (e) {
      return _createNoOpPlugin(name);
    }
  }

  function _createNoOpPlugin(name) {
    return new Proxy({}, {
      get: function (_target, prop) {
        return function () {
          console.warn("[MikiCapacitor] Plugin '" + name + "' not available. Method '" + String(prop) + "' is a no-op.");
          return Promise.resolve();
        };
      }
    });
  }

  /* --------------------------------------------------------
   * Native feature wrappers.
   * -------------------------------------------------------- */

  var Camera = {
    isAvailable: function () { return isPluginAvailable("Camera"); },
    takePicture: function (options) {
      return getPlugin("Camera").getPhoto(Object.assign(
        { quality: 90, allowEditing: false, resultType: "uri" },
        options || {}
      ));
    },
    checkPermissions: function () { return getPlugin("Camera").checkPermissions(); },
    requestPermissions: function () { return getPlugin("Camera").requestPermissions(); },
  };

  var Geolocation = {
    isAvailable: function () { return isPluginAvailable("Geolocation"); },
    getCurrentPosition: function (options) {
      return getPlugin("Geolocation").getCurrentPosition(options);
    },
    watchPosition: function (options, callback) {
      return getPlugin("Geolocation").watchPosition(options, callback);
    },
  };

  var PushNotifications = {
    isAvailable: function () { return isPluginAvailable("PushNotifications"); },
    register: function () { return getPlugin("PushNotifications").register(); },
    getDeliveredNotifications: function () {
      return getPlugin("PushNotifications").getDeliveredNotifications();
    },
  };

  var LocalNotifications = {
    isAvailable: function () { return isPluginAvailable("LocalNotifications"); },
    schedule: function (options) {
      return getPlugin("LocalNotifications").schedule(options);
    },
  };

  var Haptics = {
    isAvailable: function () { return isPluginAvailable("Haptics"); },
    impact: function (options) { return getPlugin("Haptics").impact(options || { style: "medium" }); },
    vibrate: function (options) { return getPlugin("Haptics").vibrate(options || { duration: 300 }); },
  };

  var Clipboard = {
    isAvailable: function () { return isPluginAvailable("Clipboard"); },
    read: function () { return getPlugin("Clipboard").read(); },
    write: function (options) { return getPlugin("Clipboard").write(options); },
  };

  var StatusBar = {
    isAvailable: function () { return isPluginAvailable("StatusBar"); },
    setStyle: function (options) { return getPlugin("StatusBar").setStyle(options); },
    setBackgroundColor: function (options) { return getPlugin("StatusBar").setBackgroundColor(options); },
  };

  var Network = {
    isAvailable: function () { return isPluginAvailable("Network"); },
    getStatus: function () { return getPlugin("Network").getStatus(); },
    addListener: function (event, callback) {
      return getPlugin("Network").addListener(event, callback);
    },
  };

  var Share = {
    isAvailable: function () { return isPluginAvailable("Share"); },
    share: function (options) { return getPlugin("Share").share(options); },
  };

  var Filesystem = {
    isAvailable: function () { return isPluginAvailable("Filesystem"); },
    readFile: function (options) { return getPlugin("Filesystem").readFile(options); },
    writeFile: function (options) { return getPlugin("Filesystem").writeFile(options); },
    deleteFile: function (options) { return getPlugin("Filesystem").deleteFile(options); },
  };

  /* --------------------------------------------------------
   * Initialize — detect platform and set ready state.
   * -------------------------------------------------------- */

  function init() {
    if (isCapacitor()) {
      document.addEventListener("DOMContentLoaded", function () {
        _setReady();
      });
      setTimeout(_setReady, 5000);
    } else {
      _setReady();
    }
  }

  init();

  /* --------------------------------------------------------
   * Public API
   * -------------------------------------------------------- */

  var MikiCapacitor = {
    isCapacitor: isCapacitor,
    isNative: isCapacitor,
    getPlatform: getPlatform,
    isPluginAvailable: isPluginAvailable,
    onReady: onReady,
    get isReady() { return _isReady; },
    getPlugin: getPlugin,
    plugins: {
      Camera: Camera,
      Geolocation: Geolocation,
      PushNotifications: PushNotifications,
      LocalNotifications: LocalNotifications,
      Haptics: Haptics,
      Clipboard: Clipboard,
      StatusBar: StatusBar,
      Network: Network,
      Share: Share,
      Filesystem: Filesystem,
    },
  };

  window.MikiCapacitor = MikiCapacitor;
})();
