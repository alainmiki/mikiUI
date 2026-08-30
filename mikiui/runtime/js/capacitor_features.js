(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.MikiFeatures !== "undefined") return;

  /* ================================================================
   * MikiFeatures — Capacitor plugin JS wrappers with Web API fallback.
   *
   * Each feature checks for Capacitor plugin availability first,
   * then falls back to standard Web APIs (where available), and finally
   * to a no-op with a console warning.
   *
   * This ensures the same code works on web, desktop, and mobile.
   * ================================================================ */

  function hasCapacitor() {
    return typeof window.Capacitor !== "undefined" && window.Capacitor.isNativePlatform();
  }

  /* --------------------------------------------------------
   * Camera — Capacitor Camera plugin or getUserMedia fallback.
   * -------------------------------------------------------- */

  function takePhoto(options) {
    options = options || {};
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("Camera")) {
      var camera = window.Capacitor.Plugins.Camera;
      return camera.getPhoto(Object.assign(
        { quality: 90, allowEditing: false, resultType: "uri", source: "prompt" },
        options
      ));
    }
    // Web fallback: use getUserMedia
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      return navigator.mediaDevices.getUserMedia({ video: true }).then(function (stream) {
        var video = document.createElement("video");
        video.srcObject = stream;
        video.play();
        return new Promise(function (resolve) {
          video.addEventListener("loadeddata", function () {
            var canvas = document.createElement("canvas");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext("2d").drawImage(video, 0, 0);
            stream.getTracks().forEach(function (t) { t.stop(); });
            resolve({ dataUrl: canvas.toDataURL("image/jpeg", 0.9) });
          });
        });
      });
    }
    return Promise.reject(new Error("Camera not available on this platform"));
  }

  /* --------------------------------------------------------
   * Geolocation — Capacitor Geolocation or navigator.geolocation.
   * -------------------------------------------------------- */

  function getCurrentPosition(options) {
    options = options || {};
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("Geolocation")) {
      return window.Capacitor.Plugins.Geolocation.getCurrentPosition(options);
    }
    if (navigator.geolocation) {
      return new Promise(function (resolve, reject) {
        navigator.geolocation.getCurrentPosition(resolve, reject, Object.assign(
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 },
          options
        ));
      });
    }
    return Promise.reject(new Error("Geolocation not available on this platform"));
  }

  /* --------------------------------------------------------
   * Notifications — Capacitor LocalNotifications or Web Notifications.
   * -------------------------------------------------------- */

  function scheduleNotification(options) {
    options = options || {};
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("LocalNotifications")) {
      return window.Capacitor.Plugins.LocalNotifications.schedule({
        notifications: [Object.assign({ title: "", body: "", id: Date.now() }, options)],
      });
    }
    if ("Notification" in window) {
      if (Notification.permission === "granted") {
        new Notification(options.title || "Notification", { body: options.body });
        return Promise.resolve();
      }
      if (Notification.permission !== "denied") {
        return Notification.requestPermission().then(function (perm) {
          if (perm === "granted") {
            new Notification(options.title || "Notification", { body: options.body });
          }
        });
      }
    }
    return Promise.reject(new Error("Notifications not available on this platform"));
  }

  /* --------------------------------------------------------
   * Haptics — Capacitor Haptics or Vibration API.
   * -------------------------------------------------------- */

  function hapticImpact(style) {
    style = style || "medium";
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("Haptics")) {
      window.Capacitor.Plugins.Haptics.impact({ style: style });
    } else if ("vibrate" in navigator) {
      var duration = style === "light" ? 10 : style === "heavy" ? 50 : 30;
      navigator.vibrate(duration);
    }
  }

  function hapticVibrate(duration) {
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("Haptics")) {
      window.Capacitor.Plugins.Haptics.vibrate({ duration: duration });
    } else if ("vibrate" in navigator) {
      navigator.vibrate(duration);
    }
  }

  /* --------------------------------------------------------
   * Clipboard — Capacitor Clipboard or navigator.clipboard.
   * -------------------------------------------------------- */

  function copyToClipboard(text) {
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("Clipboard")) {
      return window.Capacitor.Plugins.Clipboard.write({ string: text });
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand("copy");
        resolve();
      } catch (e) {
        reject(e);
      } finally {
        document.body.removeChild(ta);
      }
    });
  }

  function readClipboard() {
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("Clipboard")) {
      return window.Capacitor.Plugins.Clipboard.read().then(function (r) { return r.value; });
    }
    if (navigator.clipboard && navigator.clipboard.readText) {
      return navigator.clipboard.readText();
    }
    return Promise.reject(new Error("Clipboard read not available"));
  }

  /* --------------------------------------------------------
   * Share — Capacitor Share or Web Share API.
   * -------------------------------------------------------- */

  function shareContent(options) {
    options = options || {};
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("Share")) {
      return window.Capacitor.Plugins.Share.share(options);
    }
    if (navigator.share) {
      return navigator.share(options);
    }
    return Promise.reject(new Error("Share not available on this platform"));
  }

  /* --------------------------------------------------------
   * Status Bar — Capacitor StatusBar (mobile only).
   * -------------------------------------------------------- */

  function setStatusBarStyle(style) {
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("StatusBar")) {
      window.Capacitor.Plugins.StatusBar.setStyle({ style: style });
    }
  }

  function setStatusBarColor(color) {
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("StatusBar")) {
      window.Capacitor.Plugins.StatusBar.setBackgroundColor({ color: color });
    }
  }

  /* --------------------------------------------------------
   * Network — Capacitor Network or navigator.onLine.
   * -------------------------------------------------------- */

  function getNetworkStatus() {
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("Network")) {
      return window.Capacitor.Plugins.Network.getStatus();
    }
    return Promise.resolve({ connected: navigator.onLine, connectionType: "unknown" });
  }

  function onNetworkChange(callback) {
    if (hasCapacitor() && window.Capacitor.isPluginAvailable("Network")) {
      window.Capacitor.Plugins.Network.addListener("networkStatusChange", callback);
    } else {
      window.addEventListener("online", function () { callback({ connected: true }); });
      window.addEventListener("offline", function () { callback({ connected: false }); });
    }
  }

  /* --------------------------------------------------------
   * Public API
   * -------------------------------------------------------- */

  var MikiFeatures = {
    takePhoto: takePhoto,
    getCurrentPosition: getCurrentPosition,
    scheduleNotification: scheduleNotification,
    hapticImpact: hapticImpact,
    hapticVibrate: hapticVibrate,
    copyToClipboard: copyToClipboard,
    readClipboard: readClipboard,
    shareContent: shareContent,
    setStatusBarStyle: setStatusBarStyle,
    setStatusBarColor: setStatusBarColor,
    getNetworkStatus: getNetworkStatus,
    onNetworkChange: onNetworkChange,
  };

  window.MikiFeatures = MikiFeatures;
})();
