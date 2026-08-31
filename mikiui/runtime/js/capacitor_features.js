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

  function getPlugin(name) {
    if (!hasCapacitor()) return null;
    if (!window.Capacitor.isPluginAvailable(name)) return null;
    return window.Capacitor.Plugins[name] || null;
  }

  /* --------------------------------------------------------
   * Camera — Capacitor Camera plugin or getUserMedia fallback.
   * -------------------------------------------------------- */

  function takePhoto(options) {
    options = options || {};
    var camera = getPlugin("Camera");
    if (camera) {
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
        resolve({ photos: files.map(function (f) { return { webPath: URL.createObjectURL(f) }; }) });
      };
      input.click();
    });
  }

  /* --------------------------------------------------------
   * Geolocation — Capacitor Geolocation or navigator.geolocation.
   * -------------------------------------------------------- */

  function getCurrentPosition(options) {
    options = options || {};
    var geo = getPlugin("Geolocation");
    if (geo) {
      return geo.getCurrentPosition(options);
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

  function watchPosition(options, callback) {
    var geo = getPlugin("Geolocation");
    if (geo) {
      return geo.watchPosition(options || {}, callback);
    }
    if (navigator.geolocation) {
      return navigator.geolocation.watchPosition(
        function (pos) { callback(pos, null); },
        function (err) { callback(null, err); },
        Object.assign({ enableHighAccuracy: true, timeout: 10000 }, options || {})
      );
    }
    return Promise.reject(new Error("Geolocation not available on this platform"));
  }

  /* --------------------------------------------------------
   * Notifications — Capacitor LocalNotifications or Web Notifications.
   * -------------------------------------------------------- */

  function scheduleNotification(options) {
    options = options || {};
    var notify = getPlugin("LocalNotifications");
    if (notify) {
      return notify.schedule({
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

  /* --------------------------------------------------------
   * Push Notifications — Capacitor PushNotifications.
   * -------------------------------------------------------- */

  function registerForPush() {
    var push = getPlugin("PushNotifications");
    if (!push) {
      return Promise.reject(new Error("Push notifications not available"));
    }
    return push.register().then(function () {
      return push.getDeliveredNotifications();
    });
  }

  function getPushToken() {
    var push = getPlugin("PushNotifications");
    if (!push) {
      return Promise.reject(new Error("Push notifications not available"));
    }
    return new Promise(function (resolve) {
      push.addListener("registration", function (token) { resolve(token.value); });
      push.addListener("registrationError", function (err) { reject(err); });
      push.register();
    });
  }

  function onPushReceived(callback) {
    var push = getPlugin("PushNotifications");
    if (push) {
      push.addListener("pushNotificationReceived", callback);
    }
  }

  /* --------------------------------------------------------
   * Haptics — Capacitor Haptics or Vibration API.
   * -------------------------------------------------------- */

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

  /* --------------------------------------------------------
   * Clipboard — Capacitor Clipboard or navigator.clipboard.
   * -------------------------------------------------------- */

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
    return Promise.reject(new Error("Clipboard read not available"));
  }

  /* --------------------------------------------------------
   * Share — Capacitor Share or Web Share API.
   * -------------------------------------------------------- */

  function shareContent(options) {
    options = options || {};
    var share = getPlugin("Share");
    if (share) {
      return share.share(options);
    }
    if (navigator.share) {
      return navigator.share(options);
    }
    return Promise.reject(new Error("Share not available on this platform"));
  }

  function canShare() {
    if (hasCapacitor() && getPlugin("Share")) return true;
    return typeof navigator.share === "function";
  }

  /* --------------------------------------------------------
   * Status Bar — Capacitor StatusBar (mobile only).
   * -------------------------------------------------------- */

  function setStatusBarStyle(style) {
    var statusBar = getPlugin("StatusBar");
    if (statusBar) {
      statusBar.setStyle({ style: style });
    }
  }

  function setStatusBarColor(color) {
    var statusBar = getPlugin("StatusBar");
    if (statusBar) {
      statusBar.setBackgroundColor({ color: color });
    }
  }

  function showStatusBar() {
    var statusBar = getPlugin("StatusBar");
    if (statusBar) statusBar.show();
  }

  function hideStatusBar() {
    var statusBar = getPlugin("StatusBar");
    if (statusBar) statusBar.hide();
  }

  /* --------------------------------------------------------
   * Network — Capacitor Network or navigator.onLine.
   * -------------------------------------------------------- */

  function getNetworkStatus() {
    var network = getPlugin("Network");
    if (network) {
      return network.getStatus();
    }
    return Promise.resolve({ connected: navigator.onLine, connectionType: "unknown" });
  }

  function onNetworkChange(callback) {
    var network = getPlugin("Network");
    if (network) {
      network.addListener("networkStatusChange", callback);
    } else {
      window.addEventListener("online", function () { callback({ connected: true }); });
      window.addEventListener("offline", function () { callback({ connected: false }); });
    }
  }

  /* --------------------------------------------------------
   * Biometrics — Capacitor Biometrics.
   * -------------------------------------------------------- */

  function isBiometricsAvailable() {
    var bio = getPlugin("Biometrics");
    if (!bio) return Promise.resolve(false);
    return bio.isAvailable().then(function (r) { return r.isAvailable; });
  }

  function authenticateWithBiometrics(reason) {
    var bio = getPlugin("Biometrics");
    if (!bio) {
      return Promise.reject(new Error("Biometrics not available"));
    }
    return bio.authenticate({
      reason: reason || "Authenticate to continue",
      cancelTitle: "Cancel",
      fallbackTitle: "Use PIN",
    });
  }

  function setBiometricsCredentials(username, password, server) {
    var bio = getPlugin("Biometrics");
    if (!bio) return Promise.reject(new Error("Biometrics not available"));
    return bio.setCredentials({ username: username, password: password, server: server });
  }

  function getBiometricsCredentials(server) {
    var bio = getPlugin("Biometrics");
    if (!bio) return Promise.reject(new Error("Biometrics not available"));
    return bio.getCredentials({ server: server });
  }

  function deleteBiometricsCredentials(server) {
    var bio = getPlugin("Biometrics");
    if (!bio) return Promise.reject(new Error("Biometrics not available"));
    return bio.deleteCredentials({ server: server });
  }

  /* --------------------------------------------------------
   * Device Info — Capacitor Device.
   * -------------------------------------------------------- */

  function getDeviceInfo() {
    var device = getPlugin("Device");
    if (device) {
      return device.getInfo();
    }
    // Web fallback
    return Promise.resolve({
      platform: "web",
      model: navigator.userAgent,
      operatingSystem: "unknown",
      osVersion: "unknown",
      manufacturer: "unknown",
      isVirtual: false,
      webViewVersion: navigator.appVersion,
      batteryLevel: -1,
      isCharging: false,
      languageCode: navigator.language,
      languageTag: navigator.language,
    });
  }

  function getDeviceLanguage() {
    var device = getPlugin("Device");
    if (device) {
      return device.getLanguageCode();
    }
    return Promise.resolve({ value: navigator.language });
  }

  function getDeviceId() {
    var device = getPlugin("Device");
    if (device) {
      return device.getId();
    }
    // Web fallback: generate a random ID
    return Promise.resolve({
      identifier: "web-" + Math.random().toString(36).substr(2, 9),
    });
  }

  function getBatteryInfo() {
    var device = getPlugin("Device");
    if (device) {
      return device.getBatteryInfo();
    }
    // Web fallback: Battery Status API
    if ("getBattery" in navigator) {
      return navigator.getBattery().then(function (b) {
        return { batteryLevel: b.level, isCharging: b.charging };
      });
    }
    return Promise.resolve({ batteryLevel: -1, isCharging: false });
  }

  /* --------------------------------------------------------
   * Keyboard — Capacitor Keyboard.
   * -------------------------------------------------------- */

  function showKeyboard() {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) keyboard.show();
  }

  function hideKeyboard() {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) keyboard.hide();
  }

  function onKeyboardShow(callback) {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) {
      keyboard.addListener("keyboardWillShow", callback);
      keyboard.addListener("keyboardDidShow", callback);
    }
  }

  function onKeyboardHide(callback) {
    var keyboard = getPlugin("Keyboard");
    if (keyboard) {
      keyboard.addListener("keyboardWillHide", callback);
      keyboard.addListener("keyboardDidHide", callback);
    }
  }

  function isKeyboardVisible() {
    var keyboard = getPlugin("Keyboard");
    if (!keyboard) return Promise.resolve(false);
    return keyboard.isVisible();
  }

  /* --------------------------------------------------------
   * App Lifecycle — Capacitor App.
   * -------------------------------------------------------- */

  function onAppResume(callback) {
    if (!hasCapacitor()) return;
    window.Capacitor.Plugins.App.addListener("resume", callback);
  }

  function onAppPause(callback) {
    if (!hasCapacitor()) return;
    window.Capacitor.Plugins.App.addListener("pause", callback);
  }

  function onAppUrlOpen(callback) {
    if (!hasCapacitor()) return;
    window.Capacitor.Plugins.App.addListener("appUrlOpen", callback);
  }

  function onBackButton(callback) {
    if (!hasCapacitor()) return;
    window.Capacitor.Plugins.App.addListener("backButton", callback);
  }

  function exitApp() {
    if (!hasCapacitor()) return;
    window.Capacitor.Plugins.App.exitApp();
  }

  function canOpenUrl(url) {
    if (!hasCapacitor()) return Promise.resolve(false);
    return window.Capacitor.Plugins.App.canOpenUrl({ url: url });
  }

  function openUrl(url) {
    if (!hasCapacitor()) return Promise.reject(new Error("Not available"));
    return window.Capacitor.Plugins.App.openUrl({ url: url });
  }

  function getLaunchUrl() {
    if (!hasCapacitor()) return Promise.resolve(null);
    return window.Capacitor.Plugins.App.getLaunchUrl();
  }

  /* --------------------------------------------------------
   * Browser — Capacitor Browser.
   * -------------------------------------------------------- */

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

  /* --------------------------------------------------------
   * Screen Orientation — Capacitor ScreenOrientation.
   * -------------------------------------------------------- */

  function lockOrientation(orientation) {
    var screen = getPlugin("ScreenOrientation");
    if (screen) {
      return screen.lock({ orientation: orientation });
    }
    // Web fallback
    if (screen && screen.orientation && screen.orientation.lock) {
      return screen.orientation.lock(orientation).catch(function () {});
    }
    return Promise.reject(new Error("Screen orientation lock not available"));
  }

  function unlockOrientation() {
    var screen = getPlugin("ScreenOrientation");
    if (screen) {
      return screen.unlock();
    }
    if (screen && screen.orientation && screen.orientation.unlock) {
      screen.orientation.unlock();
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

  /* --------------------------------------------------------
   * Safe Area — Capacitor SafeArea.
   * -------------------------------------------------------- */

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
      safeArea.enableImmersiveMode();
    }
  }

  /* --------------------------------------------------------
   * NFC — Capacitor Community NFC.
   * -------------------------------------------------------- */

  function isNfcAvailable() {
    var nfc = getPlugin("NFC");
    if (!nfc) return Promise.resolve(false);
    return nfc.isEnabled().then(function (r) { return r.isEnabled; });
  }

  function startNfcScan(callback) {
    var nfc = getPlugin("NFC");
    if (!nfc) return Promise.reject(new Error("NFC not available"));
    return nfc.addListener("nfcTagScanned", callback);
  }

  function writeNfcTag(data) {
    var nfc = getPlugin("NFC");
    if (!nfc) return Promise.reject(new Error("NFC not available"));
    return nfc.write({ message: data });
  }

  /* --------------------------------------------------------
   * Media Player — Capacitor Community Native Audio.
   * -------------------------------------------------------- */

  function loadAudioAsset(assetPath, options) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.reject(new Error("Native audio not available"));
    return audio.load({
      assetId: options?.id || assetPath,
      assetPath: assetPath,
      audioChannelNum: options?.channels || 1,
      isUrl: options?.isUrl || false,
    });
  }

  function playAudio(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.reject(new Error("Native audio not available"));
    return audio.play({ assetId: assetId });
  }

  function pauseAudio(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.reject(new Error("Native audio not available"));
    return audio.pause({ assetId: assetId });
  }

  function resumeAudio(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.reject(new Error("Native audio not available"));
    return audio.resume({ assetId: assetId });
  }

  function stopAudio(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.reject(new Error("Native audio not available"));
    return audio.stop({ assetId: assetId });
  }

  function setAudioVolume(assetId, volume) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.reject(new Error("Native audio not available"));
    return audio.setVolume({ assetId: assetId, volume: volume });
  }

  function getAudioDuration(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.reject(new Error("Native audio not available"));
    return audio.getDuration({ assetId: assetId });
  }

  function getCurrentAudioTime(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.reject(new Error("Native audio not available"));
    return audio.getCurrentTime({ assetId: assetId });
  }

  function seekAudio(assetId, time) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.reject(new Error("Native audio not available"));
    return audio.seek({ assetId: assetId, time: time });
  }

  function unloadAudio(assetId) {
    var audio = getPlugin("NativeAudio");
    if (!audio) return Promise.reject(new Error("Native audio not available"));
    return audio.unload({ assetId: assetId });
  }

  /* --------------------------------------------------------
   * Sensors — Generic Sensor API (Web) or native plugins.
   * -------------------------------------------------------- */

  function getAccelerometerData() {
    if ("Accelerometer" in window) {
      var accel = new window.Accelerometer({ frequency: 60 });
      return new Promise(function (resolve) {
        accel.addEventListener("reading", function () {
          resolve({ x: accel.x, y: accel.y, z: accel.z });
          accel.stop();
        });
        accel.start();
      });
    }
    return Promise.reject(new Error("Accelerometer not available"));
  }

  function getGyroscopeData() {
    if ("Gyroscope" in window) {
      var gyro = new window.Gyroscope({ frequency: 60 });
      return new Promise(function (resolve) {
        gyro.addEventListener("reading", function () {
          resolve({ x: gyro.x, y: gyro.y, z: gyro.z });
          gyro.stop();
        });
        gyro.start();
      });
    }
    return Promise.reject(new Error("Gyroscope not available"));
  }

  function getMagnetometerData() {
    if ("Magnetometer" in window) {
      var mag = new window.Magnetometer({ frequency: 60 });
      return new Promise(function (resolve) {
        mag.addEventListener("reading", function () {
          resolve({ x: mag.x, y: mag.y, z: mag.z });
          mag.stop();
        });
        mag.start();
      });
    }
    return Promise.reject(new Error("Magnetometer not available"));
  }

  /* --------------------------------------------------------
   * Contacts — Capacitor Community Contacts.
   * -------------------------------------------------------- */

  function getContacts() {
    var contacts = getPlugin("Contacts");
    if (!contacts) return Promise.reject(new Error("Contacts not available"));
    return contacts.getContacts();
  }

  function createContact(data) {
    var contacts = getPlugin("Contacts");
    if (!contacts) return Promise.reject(new Error("Contacts not available"));
    return contacts.createContact({ contact: data });
  }

  function pickContact() {
    var contacts = getPlugin("Contacts");
    if (!contacts) return Promise.reject(new Error("Contacts not available"));
    return contacts.pickContact();
  }

  /* --------------------------------------------------------
   * Calendar — Capacitor Community Calendar.
   * -------------------------------------------------------- */

  function createCalendarEvent(data) {
    var calendar = getPlugin("Calendar");
    if (!calendar) return Promise.reject(new Error("Calendar not available"));
    return calendar.createEvent({
      title: data.title,
      location: data.location,
      notes: data.notes,
      startDate: data.startDate,
      endDate: data.endDate,
      isAllDay: data.isAllDay || false,
    });
  }

  function getCalendarEvents(startDate, endDate) {
    var calendar = getPlugin("Calendar");
    if (!calendar) return Promise.reject(new Error("Calendar not available"));
    return calendar.listEventsInRange({ from: startDate, to: endDate });
  }

  /* --------------------------------------------------------
   * In-App Purchases — Capacitor Community Purchases.
   * -------------------------------------------------------- */

  function getProducts() {
    var purchases = getPlugin("Purchases");
    if (!purchases) return Promise.reject(new Error("In-app purchases not available"));
    return purchases.getProducts();
  }

  function purchaseProduct(productId) {
    var purchases = getPlugin("Purchases");
    if (!purchases) return Promise.reject(new Error("In-app purchases not available"));
    return purchases.purchaseProduct({ productIdentifier: productId });
  }

  function restorePurchases() {
    var purchases = getPlugin("Purchases");
    if (!purchases) return Promise.reject(new Error("In-app purchases not available"));
    return purchases.restorePurchases();
  }

  function getCustomerInfo() {
    var purchases = getPlugin("Purchases");
    if (!purchases) return Promise.reject(new Error("In-app purchases not available"));
    return purchases.getCustomerInfo();
  }

  /* --------------------------------------------------------
   * File Picker — Capacitor Community File Picker.
   * -------------------------------------------------------- */

  function pickFile(options) {
    var picker = getPlugin("FilePicker");
    if (!picker) return Promise.reject(new Error("File picker not available"));
    return picker.pickFiles({
      types: options?.types || ["*/*"],
      multiple: options?.multiple || false,
      readData: options?.readData || false,
    });
  }

  function pickPhoto() {
    var picker = getPlugin("FilePicker");
    if (!picker) return Promise.reject(new Error("File picker not available"));
    return picker.pickImages({ multiple: false, readData: false });
  }

  function pickPhotos(options) {
    var picker = getPlugin("FilePicker");
    if (!picker) return Promise.reject(new Error("File picker not available"));
    return picker.pickImages({
      multiple: options?.multiple || true,
      readData: options?.readData || false,
    });
  }

  /* --------------------------------------------------------
   * Public API
   * -------------------------------------------------------- */

  var MikiFeatures = {
    // Camera
    takePhoto: takePhoto,
    pickImages: pickImages,

    // Geolocation
    getCurrentPosition: getCurrentPosition,
    watchPosition: watchPosition,

    // Notifications
    scheduleNotification: scheduleNotification,
    cancelNotification: cancelNotification,
    getPendingNotifications: getPendingNotifications,
    registerForPush: registerForPush,
    getPushToken: getPushToken,
    onPushReceived: onPushReceived,

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
    getDeviceId: getDeviceId,
    getBatteryInfo: getBatteryInfo,

    // Keyboard
    showKeyboard: showKeyboard,
    hideKeyboard: hideKeyboard,
    onKeyboardShow: onKeyboardShow,
    onKeyboardHide: onKeyboardHide,
    isKeyboardVisible: isKeyboardVisible,

    // App Lifecycle
    onAppResume: onAppResume,
    onAppPause: onAppPause,
    onAppUrlOpen: onAppUrlOpen,
    onBackButton: onBackButton,
    exitApp: exitApp,
    canOpenUrl: canOpenUrl,
    openUrl: openUrl,
    getLaunchUrl: getLaunchUrl,

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
    writeNfcTag: writeNfcTag,

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

    // Sensors
    getAccelerometerData: getAccelerometerData,
    getGyroscopeData: getGyroscopeData,
    getMagnetometerData: getMagnetometerData,

    // Contacts
    getContacts: getContacts,
    createContact: createContact,
    pickContact: pickContact,

    // Calendar
    createCalendarEvent: createCalendarEvent,
    getCalendarEvents: getCalendarEvents,

    // In-App Purchases
    getProducts: getProducts,
    purchaseProduct: purchaseProduct,
    restorePurchases: restorePurchases,
    getCustomerInfo: getCustomerInfo,

    // File Picker
    pickFile: pickFile,
    pickPhoto: pickPhoto,
    pickPhotos: pickPhotos,
  };

  window.MikiFeatures = MikiFeatures;
})();
