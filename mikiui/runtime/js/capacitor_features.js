(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.MikiFeatures !== "undefined") return;

  /* ================================================================
   * MikiFeatures — Complete Capacitor plugin wrappers.
   *
   * Every function has:
   * 1. Real Capacitor implementation (when plugin available)
   * 2. Web API fallback (when available)
   * 3. Graceful error handling with helpful messages
   * ================================================================ */

  function hasCapacitor() {
    return typeof window.Capacitor !== "undefined" && window.Capacitor.isNativePlatform();
  }

  function getPlugin(name) {
    if (!hasCapacitor()) return null;
    try {
      if (!window.Capacitor.isPluginAvailable(name)) return null;
      return window.Capacitor.Plugins[name] || null;
    } catch (e) {
      return null;
    }
  }

  /* ================================================================
   * PERMISSION HANDLING
   * ================================================================ */

  var PermissionStatus = {
    GRANTED: "granted",
    DENIED: "denied",
    PROMPT: "prompt",
    RESTRICTED: "restricted",
  };

  function requestPermission(permissionName) {
    var plugin = getPlugin("Permissions");
    if (plugin && plugin[permissionName]) {
      return plugin[permissionName].request().then(function (result) {
        return result.state === "granted";
      });
    }
    // Web fallback for notifications
    if (permissionName === "notifications" && "Notification" in window) {
      if (Notification.permission === "granted") return Promise.resolve(true);
      if (Notification.permission === "denied") return Promise.resolve(false);
      return Notification.requestPermission().then(function (p) { return p === "granted"; });
    }
    return Promise.resolve(true);
  }

  function checkPermission(permissionName) {
    var plugin = getPlugin("Permissions");
    if (plugin && plugin[permissionName]) {
      return plugin[permissionName].check().then(function (result) {
        return result.state;
      });
    }
    if (permissionName === "notifications" && "Notification" in window) {
      return Promise.resolve(Notification.permission);
    }
    return Promise.resolve("granted");
  }

  /* ================================================================
   * CAMERA
   * ================================================================ */

  function takePhoto(options) {
    options = options || {};
    var camera = getPlugin("Camera");
    if (camera) {
      return camera.getPhoto(Object.assign(
        { quality: 90, allowEditing: false, resultType: "uri", source: "prompt" },
        options
      )).catch(function (err) {
        if (err.message && err.message.indexOf("permission") !== -1) {
          return requestPermission("camera").then(function (granted) {
            if (granted) return camera.getPhoto(options);
            throw new Error("Camera permission denied. Please enable camera access in Settings.");
          });
        }
        throw err;
      });
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
            resolve({ dataUrl: canvas.toDataURL("image/jpeg", 0.9), path: null, webPath: null });
          });
        });
      }).catch(function (err) {
        throw new Error("Camera not available: " + (err.message || "Unknown error"));
      });
    }
    throw new Error("Camera not available on this platform");
  }

  function pickImages(options) {
    options = options || {};
    var camera = getPlugin("Camera");
    if (camera) {
      return camera.pickImages(Object.assign({ limit: 10, quality: 90 }, options));
    }
    // Web fallback: file input
    return new Promise(function (resolve) {
      var input = document.createElement("input");
      input.type = "file";
      input.accept = "image/*";
      input.multiple = true;
      input.onchange = function () {
        var files = Array.from(input.files || []);
        resolve({ photos: files.map(function (f) { return { webPath: URL.createObjectURL(f), path: null }; }) });
      };
      input.click();
    });
  }

  function pickMedia(options) {
    options = options || {};
    var camera = getPlugin("Camera");
    if (camera) {
      return camera.pickMedia(Object.assign({ limit: 10 }, options));
    }
    return pickImages(options);
  }

  /* ================================================================
   * GEOLOCATION
   * ================================================================ */

  function getCurrentPosition(options) {
    options = options || {};
    var geo = getPlugin("Geolocation");
    if (geo) {
      return geo.getCurrentPosition(options).catch(function (err) {
        if (err.message && err.message.indexOf("permission") !== -1) {
          return requestPermission("geolocation").then(function (granted) {
            if (granted) return geo.getCurrentPosition(options);
            throw new Error("Location permission denied. Please enable location access in Settings.");
          });
        }
        throw err;
      });
    }
    if (navigator.geolocation) {
      return new Promise(function (resolve, reject) {
        navigator.geolocation.getCurrentPosition(resolve, reject, Object.assign(
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 },
          options
        ));
      });
    }
    throw new Error("Geolocation not available on this platform");
  }

  function watchPosition(options, callback) {
    var geo = getPlugin("Geolocation");
    if (geo) {
      return geo.watchPosition(options || {}, callback);
    }
    if (navigator.geolocation) {
      var id = navigator.geolocation.watchPosition(
        function (pos) { callback(pos, null); },
        function (err) { callback(null, err); },
        Object.assign({ enableHighAccuracy: true, timeout: 10000 }, options || {})
      );
      return Promise.resolve({ value: id });
    }
    throw new Error("Geolocation not available on this platform");
  }

  function clearWatch(watchId) {
    var geo = getPlugin("Geolocation");
    if (geo) {
      return geo.clearWatch({ id: watchId });
    }
    if (navigator.geolocation && watchId) {
      navigator.geolocation.clearWatch(watchId.value || watchId);
    }
    return Promise.resolve();
  }

  /* ================================================================
   * NOTIFICATIONS
   * ================================================================ */

  function scheduleNotification(options) {
    options = options || {};
    var notify = getPlugin("LocalNotifications");
    if (notify) {
      return notify.schedule({
        notifications: [Object.assign({
          title: options.title || "",
          body: options.body || "",
          id: options.id || Date.now(),
          sound: options.sound || null,
          attachments: options.attachments || [],
          actionTypeId: options.actionTypeId || "",
          extra: options.extra || null,
        }, options.schedule ? { schedule: options.schedule } : {})],
      }).catch(function (err) {
        if (err.message && err.message.indexOf("permission") !== -1) {
          return requestPermission("notifications").then(function (granted) {
            if (granted) return notify.schedule({ notifications: [options] });
            throw new Error("Notification permission denied.");
          });
        }
        throw err;
      });
    }
    if ("Notification" in window) {
      if (Notification.permission === "granted") {
        new Notification(options.title || "Notification", { body: options.body, icon: options.icon });
        return Promise.resolve();
      }
      if (Notification.permission !== "denied") {
        return Notification.requestPermission().then(function (perm) {
          if (perm === "granted") {
            new Notification(options.title || "Notification", { body: options.body, icon: options.icon });
          }
        });
      }
    }
    throw new Error("Notifications not available on this platform");
  }

  function cancelNotification(id) {
    var notify = getPlugin("LocalNotifications");
    if (notify) {
      return notify.cancel({ notifications: [{ id: id }] });
    }
    return Promise.resolve();
  }

  function getPendingNotifications() {
    var notify = getPlugin("LocalNotifications");
    if (notify) {
      return notify.getPending();
    }
    return Promise.resolve({ notifications: [] });
  }

  function registerNotifications() {
    var notify = getPlugin("LocalNotifications");
    if (notify) {
      return notify.registerActionTypes({ types: [] });
    }
    return Promise.resolve();
  }

  /* ================================================================
   * PUSH NOTIFICATIONS
   * ================================================================ */

  function registerForPush() {
    var push = getPlugin("PushNotifications");
    if (!push) {
      throw new Error("Push notifications not available. Add @capacitor/push-notifications plugin.");
    }
    return push.register().then(function () {
      return push.getDeliveredNotifications();
    });
  }

  function getPushToken() {
    var push = getPlugin("PushNotifications");
    if (!push) {
      throw new Error("Push notifications not available. Add @capacitor/push-notifications plugin.");
    }
    return new Promise(function (resolve, reject) {
      var resolved = false;
      push.addListener("registration", function (token) {
        if (!resolved) { resolved = true; resolve(token.value); }
      });
      push.addListener("registrationError", function (err) {
        if (!resolved) { resolved = true; reject(new Error("Push registration failed: " + err.error)); }
      });
      push.register().catch(function (err) {
        if (!resolved) { resolved = true; reject(err); }
      });
    });
  }

  function onPushReceived(callback) {
    var push = getPlugin("PushNotifications");
    if (push) {
      push.addListener("pushNotificationReceived", callback);
    }
  }

  function onPushAction(callback) {
    var push = getPlugin("PushNotifications");
    if (push) {
      push.addListener("pushNotificationActionPerformed", callback);
    }
  }

  function getDeliveredNotifications() {
    var push = getPlugin("PushNotifications");
    if (push) {
      return push.getDeliveredNotifications();
    }
    return Promise.resolve({ notifications: [] });
  }

  function removeDeliveredNotifications(notifications) {
    var push = getPlugin("PushNotifications");
    if (push) {
      return push.removeDeliveredNotifications({ notifications: notifications });
    }
    return Promise.resolve();
  }

  function removeAllDeliveredNotifications() {
    var push = getPlugin("PushNotifications");
    if (push) {
      return push.removeAllDeliveredNotifications();
    }
    return Promise.resolve();
  }

  /* ================================================================
   * HAPTICS
   * ================================================================ */

  function hapticImpact(style) {
    style = style || "medium";
    var haptics = getPlugin("Haptics");
    if (haptics) {
      haptics.impact({ style: style });
    } else if ("vibrate" in navigator) {
      var duration = style === "light" ? 10 : style === "heavy" ? 50 : 30;
      navigator.vibrate(duration);
    }
  }

  function hapticVibrate(duration) {
    var haptics = getPlugin("Haptics");
    if (haptics) {
      haptics.vibrate({ duration: duration });
    } else if ("vibrate" in navigator) {
      navigator.vibrate(duration);
    }
  }

  function hapticSelection() {
    var haptics = getPlugin("Haptics");
    if (haptics) {
      haptics.selectionStart();
      haptics.selectionChanged();
      haptics.selectionEnd();
    } else if ("vibrate" in navigator) {
      navigator.vibrate(10);
    }
  }

  /* ================================================================
   * CLIPBOARD
   * ================================================================ */

  function copyToClipboard(text) {
    var clipboard = getPlugin("Clipboard");
    if (clipboard) {
      return clipboard.write({ string: text });
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
    var clipboard = getPlugin("Clipboard");
    if (clipboard) {
      return clipboard.read().then(function (r) { return r.value; });
    }
    if (navigator.clipboard && navigator.clipboard.readText) {
      return navigator.clipboard.readText();
    }
    throw new Error("Clipboard read not available on this platform");
  }

  /* ================================================================
   * SHARE
   * ================================================================ */

  function shareContent(options) {
    options = options || {};
    var share = getPlugin("Share");
    if (share) {
      return share.share(options);
    }
    if (navigator.share) {
      return navigator.share(options);
    }
    throw new Error("Share not available on this platform");
  }

  function canShare() {
    if (hasCapacitor() && getPlugin("Share")) return Promise.resolve(true);
    return Promise.resolve(typeof navigator.share === "function");
  }

  /* ================================================================
   * STATUS BAR
   * ================================================================ */

  function setStatusBarStyle(style) {
    var statusBar = getPlugin("StatusBar");
    if (statusBar) {
      return statusBar.setStyle({ style: style });
    }
    return Promise.resolve();
  }

  function setStatusBarColor(color) {
    var statusBar = getPlugin("StatusBar");
    if (statusBar) {
      return statusBar.setBackgroundColor({ color: color });
    }
    return Promise.resolve();
  }

  function showStatusBar() {
    var statusBar = getPlugin("StatusBar");
    if (statusBar) return statusBar.show();
    return Promise.resolve();
  }

  function hideStatusBar() {
    var statusBar = getPlugin("StatusBar");
    if (statusBar) return statusBar.hide();
    return Promise.resolve();
  }

  function setStatusBarVisible(visible) {
    return visible ? showStatusBar() : hideStatusBar();
  }

  /* ================================================================
   * NETWORK
   * ================================================================ */

  function getNetworkStatus() {
    var network = getPlugin("Network");
    if (network) {
      return network.getStatus();
    }
    return Promise.resolve({ connected: navigator.onLine, connectionType: navigator.onLine ? "wifi" : "none" });
  }

  function onNetworkChange(callback) {
    var network = getPlugin("Network");
    if (network) {
      return network.addListener("networkStatusChange", callback);
    }
    window.addEventListener("online", function () { callback({ connected: true, connectionType: "wifi" }); });
    window.addEventListener("offline", function () { callback({ connected: false, connectionType: "none" }); });
    return { remove: function () {
      window.removeEventListener("online", callback);
      window.removeEventListener("offline", callback);
    }};
  }

  /* ================================================================
   * BIOMETRICS
   * ================================================================ */

  function isBiometricsAvailable() {
    var bio = getPlugin("Biometrics");
    if (!bio) return Promise.resolve(false);
    return bio.isAvailable().then(function (r) {
      return r.isAvailable;
    }).catch(function () { return false; });
  }

  function authenticateWithBiometrics(reason) {
    var bio = getPlugin("Biometrics");
    if (!bio) {
      throw new Error("Biometrics not available. Add @capacitor/biometrics plugin.");
    }
    return bio.verify({
      reason: reason || "Authenticate to continue",
      cancelTitle: "Cancel",
      fallbackTitle: "Use PIN",
      iosTitle: "Authenticate",
    });
  }

  function setBiometricsCredentials(username, password, server) {
    var bio = getPlugin("Biometrics");
    if (!bio) throw new Error("Biometrics not available");
    return bio.setCredentials({ username: username, password: password, server: server });
  }

  function getBiometricsCredentials(server) {
    var bio = getPlugin("Biometrics");
    if (!bio) throw new Error("Biometrics not available");
    return bio.getCredentials({ server: server });
  }

  function deleteBiometricsCredentials(server) {
    var bio = getPlugin("Biometrics");
    if (!bio) throw new Error("Biometrics not available");
    return bio.deleteCredentials({ server: server });
  }

  /* ================================================================
   * DEVICE INFO
   * ================================================================ */

  function getDeviceInfo() {
    var device = getPlugin("Device");
    if (device) {
      return device.getInfo();
    }
    return Promise.resolve({
      platform: "web",
      model: navigator.userAgent,
      operatingSystem: "unknown",
      osVersion: "unknown",
      manufacturer: "unknown",
      isVirtual: false,
      webViewVersion: navigator.appVersion,
      name: "",
      memUsed: -1,
      realdiskFree: -1,
      realdiskTotal: -1,
      identifier: "",
    });
  }

  function getDeviceLanguage() {
    var device = getPlugin("Device");
    if (device) {
      return device.getLanguageCode();
    }
    return Promise.resolve({ value: navigator.language });
  }

  function getDeviceLanguageTag() {
    var device = getPlugin("Device");
    if (device) {
      return device.getLanguageTag();
    }
    return Promise.resolve({ value: navigator.language });
  }

  function getDeviceId() {
    var device = getPlugin("Device");
    if (device) {
      return device.getId();
    }
    return Promise.resolve({ identifier: "web-" + Math.random().toString(36).substr(2, 9) });
  }

  function getBatteryInfo() {
    var device = getPlugin("Device");
    if (device) {
      return device.getBatteryInfo();
    }
    if ("getBattery" in navigator) {
      return navigator.getBattery().then(function (b) {
        return { batteryLevel: b.level, isCharging: b.charging };
      });
    }
    return Promise.resolve({ batteryLevel: -1, isCharging: false });
  }

  function getUptime() {
    var device = getPlugin("Device");
    if (device) {
      return device.getUptime();
    }
    return Promise.resolve(-1);
  }

  /* ================================================================
   * KEYBOARD
   * ================================================================ */

  function showKeyboard() {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) return keyboard.show();
    return Promise.resolve();
  }

  function hideKeyboard() {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) return keyboard.hide();
    // Web fallback: blur active element
    if (document.activeElement && document.activeElement.blur) {
      document.activeElement.blur();
    }
    return Promise.resolve();
  }

  function onKeyboardShow(callback) {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) {
      return keyboard.addListener("keyboardDidShow", callback);
    }
    return { remove: function () {} };
  }

  function onKeyboardHide(callback) {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) {
      return keyboard.addListener("keyboardDidHide", callback);
    }
    return { remove: function () {} };
  }

  function isKeyboardVisible() {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) {
      return keyboard.isVisible();
    }
    return Promise.resolve(false);
  }

  function setKeyboardAccessoryBar(visible) {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) {
      return keyboard.setAccessoryBarVisible({ isVisible: visible });
    }
    return Promise.resolve();
  }

  function setScrollDisabled(disabled) {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) {
      return keyboard.setScroll({ isDisabled: disabled });
    }
    return Promise.resolve();
  }

  /* ================================================================
   * APP LIFECYCLE
   * ================================================================ */

  function onAppResume(callback) {
    if (!hasCapacitor()) return { remove: function () {} };
    return window.Capacitor.Plugins.App.addListener("resume", callback);
  }

  function onAppPause(callback) {
    if (!hasCapacitor()) return { remove: function () {} };
    return window.Capacitor.Plugins.App.addListener("pause", callback);
  }

  function onAppUrlOpen(callback) {
    if (!hasCapacitor()) return { remove: function () {} };
    return window.Capacitor.Plugins.App.addListener("appUrlOpen", callback);
  }

  function onBackButton(callback) {
    if (!hasCapacitor()) return { remove: function () {} };
    return window.Capacitor.Plugins.App.addListener("backButton", { priority: 0 }, callback);
  }

  function exitApp() {
    if (!hasCapacitor()) return Promise.resolve();
    return window.Capacitor.Plugins.App.exitApp();
  }

  function canOpenUrl(url) {
    if (!hasCapacitor()) return Promise.resolve(false);
    return window.Capacitor.Plugins.App.canOpenUrl({ url: url });
  }

  function openUrl(url) {
    if (!hasCapacitor()) return Promise.reject(new Error("Not available on web"));
    return window.Capacitor.Plugins.App.openUrl({ url: url });
  }

  function getLaunchUrl() {
    if (!hasCapacitor()) return Promise.resolve(null);
    return window.Capacitor.Plugins.App.getLaunchUrl();
  }

  function minimizeApp() {
    if (!hasCapacitor()) return Promise.resolve();
    return window.Capacitor.Plugins.App.minimize();
  }

  /* ================================================================
   * BROWSER
   * ================================================================ */

  function openInBrowser(url) {
    var browser = getPlugin("Browser");
    if (browser) {
      return browser.open({ url: url });
    }
    window.open(url, "_blank");
    return Promise.resolve();
  }

  function closeBrowser() {
    var browser = getPlugin("Browser");
    if (browser) return browser.close();
    return Promise.resolve();
  }

  /* ================================================================
   * SCREEN ORIENTATION
   * ================================================================ */

  function lockOrientation(orientation) {
    var screen = getPlugin("ScreenOrientation");
    if (screen) {
      return screen.lock({ orientation: orientation });
    }
    if (window.screen && window.screen.orientation && window.screen.orientation.lock) {
      return window.screen.orientation.lock(orientation).catch(function () {
        throw new Error("Screen orientation lock not supported");
      });
    }
    throw new Error("Screen orientation lock not available");
  }

  function unlockOrientation() {
    var screen = getPlugin("ScreenOrientation");
    if (screen) {
      return screen.unlock();
    }
    if (window.screen && window.screen.orientation && window.screen.orientation.unlock) {
      window.screen.orientation.unlock();
    }
    return Promise.resolve();
  }

  function getOrientation() {
    var screen = getPlugin("ScreenOrientation");
    if (screen) {
      return screen.orientation();
    }
    return Promise.resolve({ type: window.screen.orientation?.type || "unknown" });
  }

  /* ================================================================
   * SAFE AREA
   * ================================================================ */

  function getSafeArea() {
    var safeArea = getPlugin("SafeArea");
    if (safeArea) {
      return safeArea.getSafeAreaInsets();
    }
    // Web fallback using CSS environment variables
    var style = getComputedStyle(document.documentElement);
    return Promise.resolve({
      insets: {
        top: parseInt(style.getPropertyValue("--sat") || "0"),
        bottom: parseInt(style.getPropertyValue("--sab") || "0"),
        left: parseInt(style.getPropertyValue("--sal") || "0"),
        right: parseInt(style.getPropertyValue("--sar") || "0"),
      },
    });
  }

  function setSafeAreaMargins(enable) {
    var safeArea = getPlugin("SafeArea");
    if (safeArea) {
      if (enable) {
        safeArea.enableImmersiveMode();
      } else {
        safeArea.disableImmersiveMode();
      }
    }
    return Promise.resolve();
  }

  /* ================================================================
   * NFC
   * ================================================================ */

  function isNfcAvailable() {
    var nfc = getPlugin("NFC");
    if (!nfc) return Promise.resolve(false);
    return nfc.isEnabled().then(function (r) { return r.isEnabled; }).catch(function () { return false; });
  }

  function startNfcScan(callback) {
    var nfc = getPlugin("NFC");
    if (!nfc) throw new Error("NFC not available. Add @capacitor-community/nfc plugin.");
    return nfc.addListener("nfcTagScanned", callback);
  }

  function stopNfcScan() {
    var nfc = getPlugin("NFC");
    if (!nfc) return Promise.resolve();
    return nfc.removeAllListeners();
  }

  function writeNfcTag(data) {
    var nfc = getPlugin("NFC");
    if (!nfc) throw new Error("NFC not available. Add @capacitor-community/nfc plugin.");
    return nfc.write({ message: data });
  }

  function readNfcTag() {
    var nfc = getPlugin("NFC");
    if (!nfc) throw new Error("NFC not available. Add @capacitor-community/nfc plugin.");
    return new Promise(function (resolve, reject) {
      var sub = nfc.addListener("nfcTagScanned", function (tag) {
        sub.remove();
        resolve(tag);
      });
      nfc.scan().catch(function (err) { reject(err); });
    });
  }

  function formatNfcTag(data) {
    var nfc = getPlugin("NFC");
    if (!nfc) throw new Error("NFC not available");
    return nfc.format({ message: data });
  }

  /* ================================================================
   * MEDIA PLAYER (Native Audio)
   * ================================================================ */

  function loadAudioAsset(assetPath, options) {
    options = options || {};
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available. Add @capacitor-community/native-audio plugin.");
    return audio.load({
      assetId: options.id || assetPath,
      assetPath: assetPath,
      audioChannelNum: options.channels || 1,
      isUrl: options.isUrl || false,
    });
  }

  function playAudio(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available");
    return audio.play({ assetId: assetId, time: 0 });
  }

  function pauseAudio(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available");
    return audio.pause({ assetId: assetId });
  }

  function resumeAudio(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available");
    return audio.resume({ assetId: assetId });
  }

  function stopAudio(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available");
    return audio.stop({ assetId: assetId });
  }

  function setAudioVolume(assetId, volume) {
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available");
    return audio.setVolume({ assetId: assetId, volume: Math.max(0, Math.min(1, volume)) });
  }

  function getAudioDuration(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available");
    return audio.getDuration({ assetId: assetId });
  }

  function getCurrentAudioTime(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available");
    return audio.getCurrentTime({ assetId: assetId });
  }

  function seekAudio(assetId, time) {
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available");
    return audio.seek({ assetId: assetId, time: time });
  }

  function unloadAudio(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available");
    return audio.unload({ assetId: assetId });
  }

  function setAudioRate(assetId, rate) {
    var audio = getPlugin("NativeAudio");
    if (!audio) throw new Error("Native audio not available");
    return audio.setRate({ assetId: assetId, rate: rate });
  }

  function isAudioPlaying(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.resolve(false);
    return audio.isPlaying({ assetId: assetId }).then(function (r) { return r.isPlaying; });
  }

  /* ================================================================
   * SENSORS (Generic Sensor API)
   * ================================================================ */

  function getAccelerometerData() {
    if ("Accelerometer" in window) {
      var accel = new window.Accelerometer({ frequency: 60 });
      return new Promise(function (resolve, reject) {
        accel.addEventListener("reading", function () {
          resolve({ x: accel.x, y: accel.y, z: accel.z, timestamp: accel.timestamp });
          accel.stop();
        });
        accel.addEventListener("error", function (e) { reject(new Error(e.error.message)); });
        accel.start();
      }).catch(function () {
        throw new Error("Accelerometer not available");
      });
    }
    throw new Error("Accelerometer not available on this platform");
  }

  function getGyroscopeData() {
    if ("Gyroscope" in window) {
      var gyro = new window.Gyroscope({ frequency: 60 });
      return new Promise(function (resolve, reject) {
        gyro.addEventListener("reading", function () {
          resolve({ x: gyro.x, y: gyro.y, z: gyro.z, timestamp: gyro.timestamp });
          gyro.stop();
        });
        gyro.addEventListener("error", function (e) { reject(new Error(e.error.message)); });
        gyro.start();
      }).catch(function () {
        throw new Error("Gyroscope not available");
      });
    }
    throw new Error("Gyroscope not available on this platform");
  }

  function getMagnetometerData() {
    if ("Magnetometer" in window) {
      var mag = new window.Magnetometer({ frequency: 60 });
      return new Promise(function (resolve, reject) {
        mag.addEventListener("reading", function () {
          resolve({ x: mag.x, y: mag.y, z: mag.z, timestamp: mag.timestamp });
          mag.stop();
        });
        mag.addEventListener("error", function (e) { reject(new Error(e.error.message)); });
        mag.start();
      }).catch(function () {
        throw new Error("Magnetometer not available");
      });
    }
    throw new Error("Magnetometer not available on this platform");
  }

  function getOrientationData() {
    if ("AbsoluteOrientationSensor" in window) {
      var orient = new window.AbsoluteOrientationSensor({ frequency: 60 });
      return new Promise(function (resolve, reject) {
        orient.addEventListener("reading", function () {
          resolve({
            quaternion: orient.quaternion,
            timestamp: orient.timestamp,
          });
          orient.stop();
        });
        orient.addEventListener("error", function (e) { reject(new Error(e.error.message)); });
        orient.start();
      }).catch(function () {
        throw new Error("Orientation sensor not available");
      });
    }
    throw new Error("Orientation sensor not available on this platform");
  }

  /* ================================================================
   * CONTACTS
   * ================================================================ */

  function getContacts() {
    var contacts = getPlugin("Contacts");
    if (!contacts) throw new Error("Contacts not available. Add @capacitor-community/contacts plugin.");
    return contacts.getContacts();
  }

  function createContact(data) {
    var contacts = getPlugin("Contacts");
    if (!contacts) throw new Error("Contacts not available");
    return contacts.createContact({ contact: data });
  }

  function pickContact() {
    var contacts = getPlugin("Contacts");
    if (!contacts) throw new Error("Contacts not available");
    return contacts.pickContact();
  }

  function deleteContact(contactId) {
    var contacts = getPlugin("Contacts");
    if (!contacts) throw new Error("Contacts not available");
    return contacts.deleteContact({ contactId: contactId });
  }

  function requestContactsPermission() {
    var contacts = getPlugin("Contacts");
    if (!contacts) return Promise.reject(new Error("Contacts not available"));
    return contacts.requestPermissions().then(function (r) { return r.contacts === "granted"; });
  }

  /* ================================================================
   * CALENDAR
   * ================================================================ */

  function createCalendarEvent(data) {
    var calendar = getPlugin("Calendar");
    if (!calendar) throw new Error("Calendar not available. Add @capacitor-community/calendar plugin.");
    return calendar.createEvent({
      title: data.title,
      location: data.location,
      notes: data.notes,
      startDate: data.startDate,
      endDate: data.endDate,
      isAllDay: data.isAllDay || false,
      calendarId: data.calendarId || null,
      url: data.url || null,
    });
  }

  function getCalendarEvents(startDate, endDate) {
    var calendar = getPlugin("Calendar");
    if (!calendar) throw new Error("Calendar not available");
    return calendar.listEventsInRange({ from: startDate, to: endDate });
  }

  function deleteCalendarEvent(eventId) {
    var calendar = getPlugin("Calendar");
    if (!calendar) throw new Error("Calendar not available");
    return calendar.deleteEvent({ eventId: eventId });
  }

  function requestCalendarPermission() {
    var calendar = getPlugin("Calendar");
    if (!calendar) return Promise.reject(new Error("Calendar not available"));
    return calendar.requestPermissions().then(function (r) { return r.calendar === "granted"; });
  }

  function openCalendar(date) {
    var calendar = getPlugin("Calendar");
    if (!calendar) return Promise.reject(new Error("Calendar not available"));
    return calendar.openCalendar({ date: date || Date.now() });
  }

  /* ================================================================
   * IN-APP PURCHASES
   * ================================================================ */

  function configurePurchases(apiKey) {
    var purchases = getPlugin("Purchases");
    if (!purchases) throw new Error("In-app purchases not available. Add @capacitor-community/purchases plugin.");
    return purchases.configure({ apiKey: apiKey, appUserID: null });
  }

  function getProducts() {
    var purchases = getPlugin("Purchases");
    if (!purchases) throw new Error("In-app purchases not available");
    return purchases.getProducts();
  }

  function purchaseProduct(productId) {
    var purchases = getPlugin("Purchases");
    if (!purchases) throw new Error("In-app purchases not available");
    return purchases.purchaseProduct({ productIdentifier: productId });
  }

  function purchasePackage(packageId) {
    var purchases = getPlugin("Purchases");
    if (!purchases) throw new Error("In-app purchases not available");
    return purchases.purchasePackage({ packageIdentifier: packageId });
  }

  function restorePurchases() {
    var purchases = getPlugin("Purchases");
    if (!purchases) throw new Error("In-app purchases not available");
    return purchases.restorePurchases();
  }

  function getCustomerInfo() {
    var purchases = getPlugin("Purchases");
    if (!purchases) throw new Error("In-app purchases not available");
    return purchases.getCustomerInfo();
  }

  function syncPurchases() {
    var purchases = getPlugin("Purchases");
    if (!purchases) return Promise.resolve();
    return purchases.syncPurchases();
  }

  function showPaywall(productId) {
    var purchases = getPlugin("Purchases");
    if (!purchases) throw new Error("In-app purchases not available");
    return purchases.presentCodeRedemptionSheet();
  }

  /* ================================================================
   * FILE PICKER
   * ================================================================ */

  function pickFile(options) {
    options = options || {};
    var picker = getPlugin("FilePicker");
    if (!picker) throw new Error("File picker not available. Add @capacitor-community/file-picker plugin.");
    return picker.pickFiles({
      types: options.types || ["*/*"],
      multiple: options.multiple || false,
      readData: options.readData || false,
    });
  }

  function pickPhoto() {
    var picker = getPlugin("FilePicker");
    if (!picker) throw new Error("File picker not available");
    return picker.pickImages({ multiple: false, readData: false });
  }

  function pickPhotos(options) {
    options = options || {};
    var picker = getPlugin("FilePicker");
    if (!picker) throw new Error("File picker not available");
    return picker.pickImages({
      multiple: options.multiple || true,
      readData: options.readData || false,
    });
  }

  function pickVideo() {
    var picker = getPlugin("FilePicker");
    if (!picker) throw new Error("File picker not available");
    return picker.pickVideos({ multiple: false, readData: false });
  }

  function pickVideos(options) {
    options = options || {};
    var picker = getPlugin("FilePicker");
    if (!picker) throw new Error("File picker not available");
    return picker.pickVideos({
      multiple: options.multiple || true,
      readData: options.readData || false,
    });
  }

  /* ================================================================
   * PHOTO GALLERY
   * ================================================================ */

  function savePhotoToGallery(data) {
    var photos = getPlugin("Photos");
    if (!photos) throw new Error("Photos plugin not available");
    return photos.savePhoto({ data: data });
  }

  function getPhotoFromGallery() {
    var photos = getPlugin("Photos");
    if (!photos) throw new Error("Photos plugin not available");
    return photos.getPhoto();
  }

  function requestPhotosPermission() {
    var photos = getPlugin("Photos");
    if (!photos) return Promise.reject(new Error("Photos plugin not available"));
    return photos.requestPermissions().then(function (r) { return r.photos === "granted"; });
  }

  /* ================================================================
   * BLUETOOTH (Web Bluetooth API)
   * ================================================================ */

  function requestBluetoothDevice(options) {
    options = options || {};
    if (!navigator.bluetooth) {
      throw new Error("Web Bluetooth not available. Use Chrome on Android or desktop.");
    }
    return navigator.bluetooth.requestDevice({
      filters: options.filters || [],
      optionalServices: options.optionalServices || [],
      acceptAllDevices: options.acceptAllDevices || false,
    });
  }

  function connectBluetoothDevice(device) {
    return device.gatt.connect();
  }

  function disconnectBluetoothDevice(device) {
    if (device.gatt && device.gatt.connected) {
      device.gatt.disconnect();
    }
    return Promise.resolve();
  }

  function isBluetoothDeviceConnected(device) {
    return Promise.resolve(device.gatt ? device.gatt.connected : false);
  }

  function readBluetoothCharacteristic(service, characteristicUUID) {
    return service.getCharacteristic(characteristicUUID).then(function (char) {
      return char.readValue();
    });
  }

  function writeBluetoothCharacteristic(service, characteristicUUID, value) {
    return service.getCharacteristic(characteristicUUID).then(function (char) {
      return char.writeValue(value);
    });
  }

  /* ================================================================
   * SMS / CALL (URL Schemes)
   * ================================================================ */

  function sendSms(phoneNumber, message) {
    var url = "sms:" + phoneNumber + (message ? "?body=" + encodeURIComponent(message) : "");
    window.location.href = url;
    return Promise.resolve();
  }

  function callPhoneNumber(phoneNumber) {
    window.location.href = "tel:" + phoneNumber;
    return Promise.resolve();
  }

  function sendEmail(to, subject, body) {
    var url = "mailto:" + to;
    var params = [];
    if (subject) params.push("subject=" + encodeURIComponent(subject));
    if (body) params.push("body=" + encodeURIComponent(body));
    if (params.length > 0) url += "?" + params.join("&");
    window.location.href = url;
    return Promise.resolve();
  }

  function openMaps(address, lat, lng) {
    var url;
    if (lat !== undefined && lng !== undefined) {
      url = "https://maps.google.com/?q=" + lat + "," + lng;
    } else {
      url = "https://maps.google.com/?q=" + encodeURIComponent(address);
    }
    window.open(url, "_blank");
    return Promise.resolve();
  }

  /* ================================================================
   * DARK MODE
   * ================================================================ */

  function isDarkMode() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function onDarkModeChange(callback) {
    if (!window.matchMedia) return { remove: function () {} };
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    var handler = function (e) { callback(e.matches); };
    mq.addEventListener("change", handler);
    return { remove: function () { mq.removeEventListener("change", handler); } };
  }

  function setBackgroundColor(color) {
    document.documentElement.style.backgroundColor = color;
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", color);
  }

  /* ================================================================
   * PUBLIC API
   * ================================================================ */

  var MikiFeatures = {
    // Permissions
    requestPermission: requestPermission,
    checkPermission: checkPermission,
    PermissionStatus: PermissionStatus,

    // Camera
    takePhoto: takePhoto,
    pickImages: pickImages,
    pickMedia: pickMedia,

    // Geolocation
    getCurrentPosition: getCurrentPosition,
    watchPosition: watchPosition,
    clearWatch: clearWatch,

    // Notifications
    scheduleNotification: scheduleNotification,
    cancelNotification: cancelNotification,
    getPendingNotifications: getPendingNotifications,
    registerNotifications: registerNotifications,

    // Push Notifications
    registerForPush: registerForPush,
    getPushToken: getPushToken,
    onPushReceived: onPushReceived,
    onPushAction: onPushAction,
    getDeliveredNotifications: getDeliveredNotifications,
    removeDeliveredNotifications: removeDeliveredNotifications,
    removeAllDeliveredNotifications: removeAllDeliveredNotifications,

    // Haptics
    hapticImpact: hapticImpact,
    hapticVibrate: hapticVibrate,
    hapticSelection: hapticSelection,

    // Clipboard
    copyToClipboard: copyToClipboard,
    readClipboard: readClipboard,

    // Share
    shareContent: shareContent,
    canShare: canShare,

    // Status Bar
    setStatusBarStyle: setStatusBarStyle,
    setStatusBarColor: setStatusBarColor,
    showStatusBar: showStatusBar,
    hideStatusBar: hideStatusBar,
    setStatusBarVisible: setStatusBarVisible,

    // Network
    getNetworkStatus: getNetworkStatus,
    onNetworkChange: onNetworkChange,

    // Biometrics
    isBiometricsAvailable: isBiometricsAvailable,
    authenticateWithBiometrics: authenticateWithBiometrics,
    setBiometricsCredentials: setBiometricsCredentials,
    getBiometricsCredentials: getBiometricsCredentials,
    deleteBiometricsCredentials: deleteBiometricsCredentials,

    // Device
    getDeviceInfo: getDeviceInfo,
    getDeviceLanguage: getDeviceLanguage,
    getDeviceLanguageTag: getDeviceLanguageTag,
    getDeviceId: getDeviceId,
    getBatteryInfo: getBatteryInfo,
    getUptime: getUptime,

    // Keyboard
    showKeyboard: showKeyboard,
    hideKeyboard: hideKeyboard,
    onKeyboardShow: onKeyboardShow,
    onKeyboardHide: onKeyboardHide,
    isKeyboardVisible: isKeyboardVisible,
    setKeyboardAccessoryBar: setKeyboardAccessoryBar,
    setScrollDisabled: setScrollDisabled,

    // App Lifecycle
    onAppResume: onAppResume,
    onAppPause: onAppPause,
    onAppUrlOpen: onAppUrlOpen,
    onBackButton: onBackButton,
    exitApp: exitApp,
    canOpenUrl: canOpenUrl,
    openUrl: openUrl,
    getLaunchUrl: getLaunchUrl,
    minimizeApp: minimizeApp,

    // Browser
    openInBrowser: openInBrowser,
    closeBrowser: closeBrowser,

    // Screen Orientation
    lockOrientation: lockOrientation,
    unlockOrientation: unlockOrientation,
    getOrientation: getOrientation,

    // Safe Area
    getSafeArea: getSafeArea,
    setSafeAreaMargins: setSafeAreaMargins,

    // NFC
    isNfcAvailable: isNfcAvailable,
    startNfcScan: startNfcScan,
    stopNfcScan: stopNfcScan,
    writeNfcTag: writeNfcTag,
    readNfcTag: readNfcTag,
    formatNfcTag: formatNfcTag,

    // Media Player
    loadAudioAsset: loadAudioAsset,
    playAudio: playAudio,
    pauseAudio: pauseAudio,
    resumeAudio: resumeAudio,
    stopAudio: stopAudio,
    setAudioVolume: setAudioVolume,
    getAudioDuration: getAudioDuration,
    getCurrentAudioTime: getCurrentAudioTime,
    seekAudio: seekAudio,
    unloadAudio: unloadAudio,
    setAudioRate: setAudioRate,
    isAudioPlaying: isAudioPlaying,

    // Sensors
    getAccelerometerData: getAccelerometerData,
    getGyroscopeData: getGyroscopeData,
    getMagnetometerData: getMagnetometerData,
    getOrientationData: getOrientationData,

    // Contacts
    getContacts: getContacts,
    createContact: createContact,
    pickContact: pickContact,
    deleteContact: deleteContact,
    requestContactsPermission: requestContactsPermission,

    // Calendar
    createCalendarEvent: createCalendarEvent,
    getCalendarEvents: getCalendarEvents,
    deleteCalendarEvent: deleteCalendarEvent,
    requestCalendarPermission: requestCalendarPermission,
    openCalendar: openCalendar,

    // In-App Purchases
    configurePurchases: configurePurchases,
    getProducts: getProducts,
    purchaseProduct: purchaseProduct,
    purchasePackage: purchasePackage,
    restorePurchases: restorePurchases,
    getCustomerInfo: getCustomerInfo,
    syncPurchases: syncPurchases,
    showPaywall: showPaywall,

    // File Picker
    pickFile: pickFile,
    pickPhoto: pickPhoto,
    pickPhotos: pickPhotos,
    pickVideo: pickVideo,
    pickVideos: pickVideos,

    // Photo Gallery
    savePhotoToGallery: savePhotoToGallery,
    getPhotoFromGallery: getPhotoFromGallery,
    requestPhotosPermission: requestPhotosPermission,

    // Bluetooth
    requestBluetoothDevice: requestBluetoothDevice,
    connectBluetoothDevice: connectBluetoothDevice,
    disconnectBluetoothDevice: disconnectBluetoothDevice,
    isBluetoothDeviceConnected: isBluetoothDeviceConnected,
    readBluetoothCharacteristic: readBluetoothCharacteristic,
    writeBluetoothCharacteristic: writeBluetoothCharacteristic,

    // SMS / Call / Email
    sendSms: sendSms,
    callPhoneNumber: callPhoneNumber,
    sendEmail: sendEmail,
    openMaps: openMaps,

    // Dark Mode
    isDarkMode: isDarkMode,
    onDarkModeChange: onDarkModeChange,
    setBackgroundColor: setBackgroundColor,
  };

  window.MikiFeatures = MikiFeatures;
})();
