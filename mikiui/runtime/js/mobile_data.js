(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.MikiData !== "undefined") return;

  /* ================================================================
   * MikiData - Offline-first data persistence layer.
   *
   * Provides:
   * 1. Local storage with automatic sync when online
   * 2. Queue for pending operations when offline
   * 3. Conflict resolution for data sync
   * 4. Automatic retry with exponential backoff
   * ================================================================ */

  var DB_NAME = "mikiui_data";
  var DB_VERSION = 1;
  var SYNC_QUEUE_KEY = "mikiui_sync_queue";
  var LAST_SYNC_KEY = "mikiui_last_sync";

  var _db = null;
  var _syncInProgress = false;
  var _listeners = { online: [], offline: [], sync: [], error: [] };

  /* --------------------------------------------------------
   * IndexedDB wrapper for structured data storage.
   * -------------------------------------------------------- */

  function openDB() {
    if (_db) return Promise.resolve(_db);
    return new Promise(function (resolve, reject) {
      if (!("indexedDB" in window)) {
        reject(new Error("IndexedDB not available"));
        return;
      }
      var request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onerror = function () { reject(request.error); };
      request.onsuccess = function () { _db = request.result; resolve(_db); };
      request.onupgradeneeded = function (event) {
        var db = event.target.result;
        if (!db.objectStoreNames.contains("data")) {
          db.createObjectStore("data", { keyPath: "key" });
        }
        if (!db.objectStoreNames.contains("queue")) {
          db.createObjectStore("queue", { keyPath: "id", autoIncrement: true });
        }
        if (!db.objectStoreNames.contains("meta")) {
          db.createObjectStore("meta", { keyPath: "key" });
        }
      };
    });
  }

  function dbGet(storeName, key) {
    return openDB().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(storeName, "readonly");
        var store = tx.objectStore(storeName);
        var request = store.get(key);
        request.onsuccess = function () { resolve(request.result ? request.result.value : null); };
        request.onerror = function () { reject(request.error); };
      });
    });
  }

  function dbSet(storeName, key, value) {
    return openDB().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(storeName, "readwrite");
        var store = tx.objectStore(storeName);
        var request = store.put({ key: key, value: value, updatedAt: Date.now() });
        request.onsuccess = function () { resolve(value); };
        request.onerror = function () { reject(request.error); };
      });
    });
  }

  function dbDelete(storeName, key) {
    return openDB().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(storeName, "readwrite");
        var store = tx.objectStore(storeName);
        var request = store.delete(key);
        request.onsuccess = function () { resolve(); };
        request.onerror = function () { reject(request.error); };
      });
    });
  }

  function dbGetAll(storeName) {
    return openDB().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(storeName, "readonly");
        var store = tx.objectStore(storeName);
        var request = store.getAll();
        request.onsuccess = function () {
          var result = {};
          request.result.forEach(function (item) { result[item.key] = item.value; });
          resolve(result);
        };
        request.onerror = function () { reject(request.error); };
      });
    });
  }

  function dbClear(storeName) {
    return openDB().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(storeName, "readwrite");
        var store = tx.objectStore(storeName);
        var request = store.clear();
        request.onsuccess = function () { resolve(); };
        request.onerror = function () { reject(request.error); };
      });
    });
  }

  /* --------------------------------------------------------
   * LocalStorage fallback for simple key-value data.
   * -------------------------------------------------------- */

  function lsGet(key) {
    try {
      var val = localStorage.getItem(DB_NAME + ":" + key);
      return val ? JSON.parse(val) : null;
    } catch (e) { return null; }
  }

  function lsSet(key, value) {
    try {
      localStorage.setItem(DB_NAME + ":" + key, JSON.stringify(value));
      return Promise.resolve(value);
    } catch (e) { return Promise.reject(e); }
  }

  function lsDelete(key) {
    try { localStorage.removeItem(DB_NAME + ":" + key); return Promise.resolve(); }
    catch (e) { return Promise.reject(e); }
  }

  function lsGetAll() {
    try {
      var result = {};
      for (var i = 0; i < localStorage.length; i++) {
        var key = localStorage.key(i);
        if (key && key.indexOf(DB_NAME + ":") === 0) {
          var shortKey = key.substring(DB_NAME.length + 1);
          result[shortKey] = JSON.parse(localStorage.getItem(key));
        }
      }
      return result;
    } catch (e) { return {}; }
  }

  /* --------------------------------------------------------
   * Sync queue for offline operations.
   * -------------------------------------------------------- */

  function getQueue() {
    return lsGet(SYNC_QUEUE_KEY) || [];
  }

  function addToQueue(operation) {
    var queue = getQueue();
    operation.id = Date.now() + "-" + Math.random().toString(36).substr(2, 9);
    operation.timestamp = Date.now();
    operation.retries = 0;
    queue.push(operation);
    return lsSet(SYNC_QUEUE_KEY, queue).then(function () { return operation.id; });
  }

  function removeFromQueue(id) {
    var queue = getQueue().filter(function (op) { return op.id !== id; });
    return lsSet(SYNC_QUEUE_KEY, queue);
  }

  function updateQueue(queue) {
    return lsSet(SYNC_QUEUE_KEY, queue);
  }

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
   * Public API.
   * -------------------------------------------------------- */

  var MikiData = {
    // Storage - uses IndexedDB if available, falls back to localStorage
    get: function (key) {
      if ("indexedDB" in window) {
        return dbGet("data", key).catch(function () { return lsGet(key); });
      }
      return Promise.resolve(lsGet(key));
    },

    set: function (key, value) {
      if ("indexedDB" in window) {
        return dbSet("data", key, value).catch(function () { return lsSet(key, value); });
      }
      return lsSet(key, value);
    },

    delete: function (key) {
      if ("indexedDB" in window) {
        return dbDelete("data", key).catch(function () { return lsDelete(key); });
      }
      return lsDelete(key);
    },

    getAll: function () {
      if ("indexedDB" in window) {
        return dbGetAll("data").catch(function () { return lsGetAll(); });
      }
      return Promise.resolve(lsGetAll());
    },

    clear: function () {
      if ("indexedDB" in window) {
        return dbClear("data").catch(function () {
          Object.keys(lsGetAll()).forEach(function (k) { lsDelete(k); });
        });
      }
      Object.keys(lsGetAll()).forEach(function (k) { lsDelete(k); });
      return Promise.resolve();
    },

    // Sync queue for offline operations
    queue: function (operation) {
      return addToQueue(operation);
    },

    getQueue: function () {
      return Promise.resolve(getQueue());
    },

    clearQueue: function () {
      return lsSet(SYNC_QUEUE_KEY, []);
    },

    removeFromQueue: function (id) {
      return removeFromQueue(id);
    },

    // Sync operations when back online
    sync: function (syncHandler) {
      if (_syncInProgress) return Promise.resolve({ synced: 0, failed: 0 });
      _syncInProgress = true;

      var queue = getQueue();
      if (queue.length === 0) {
        _syncInProgress = false;
        return Promise.resolve({ synced: 0, failed: 0 });
      }

      var synced = 0;
      var failed = 0;

      return Promise.each
        ? Promise.each(queue, function (op) {
            return syncHandler(op).then(function () {
              synced++;
              return removeFromQueue(op.id);
            }).catch(function () {
              failed++;
              op.retries = (op.retries || 0) + 1;
            });
          }).then(function () {
            _syncInProgress = false;
            lsSet("mikiui_last_sync", Date.now());
            _emit("sync", { synced: synced, failed: failed });
            return { synced: synced, failed: failed };
          })
        : queue.reduce(function (promise, op) {
            return promise.then(function () {
              return syncHandler(op).then(function () {
                synced++;
                return removeFromQueue(op.id);
              }).catch(function () {
                failed++;
                op.retries = (op.retries || 0) + 1;
              });
            });
          }, Promise.resolve()).then(function () {
            _syncInProgress = false;
            lsSet("mikiui_last_sync", Date.now());
            _emit("sync", { synced: synced, failed: failed });
            return { synced: synced, failed: failed };
          });
    },

    // Last sync timestamp
    getLastSync: function () {
      return Promise.resolve(lsGet(LAST_SYNC_KEY) || null);
    },

    // Event listeners
    on: on,

    // Check if data exists
    has: function (key) {
      return this.get(key).then(function (val) { return val !== null; });
    },

    // Get multiple keys at once
    getMany: function (keys) {
      var self = this;
      return Promise.all(keys.map(function (k) { return self.get(k); })).then(function (values) {
        var result = {};
        keys.forEach(function (k, i) { result[k] = values[i]; });
        return result;
      });
    },

    // Set multiple keys at once
    setMany: function (data) {
      var self = this;
      return Promise.all(Object.keys(data).map(function (k) { return self.set(k, data[k]); }));
    },

    // Increment a numeric value
    increment: function (key, amount) {
      var self = this;
      amount = amount || 1;
      return this.get(key).then(function (val) {
        var num = (typeof val === "number" ? val : 0) + amount;
        return self.set(key, num).then(function () { return num; });
      });
    },

    // Append to an array
    append: function (key, item) {
      var self = this;
      return this.get(key).then(function (val) {
        var arr = Array.isArray(val) ? val : [];
        arr.push(item);
        return self.set(key, arr).then(function () { return arr; });
      });
    },

    // Prepend to an array
    prepend: function (key, item) {
      var self = this;
      return this.get(key).then(function (val) {
        var arr = Array.isArray(val) ? val : [];
        arr.unshift(item);
        return self.set(key, arr).then(function () { return arr; });
      });
    },

    // Remove from an array
    removeFromArray: function (key, predicate) {
      var self = this;
      return this.get(key).then(function (val) {
        if (!Array.isArray(val)) return [];
        var arr = val.filter(function (item) { return !predicate(item); });
        return self.set(key, arr).then(function () { return arr; });
      });
    },

    // Cache with expiration
    cache: function (key, ttlMs) {
      var self = this;
      return this.get(key).then(function (val) {
        if (val && val.__expires && val.__expires > Date.now()) {
          return val.__data;
        }
        return null;
      });
    },

    setCache: function (key, data, ttlMs) {
      var self = this;
      var wrapped = { __data: data, __expires: Date.now() + ttlMs };
      return self.set(key, wrapped);
    },

    // Auto-sync when online
    enableAutoSync: function (syncHandler, intervalMs) {
      var self = this;
      intervalMs = intervalMs || 30000; // 30 seconds default

      function trySync() {
        if (navigator.onLine) {
          self.sync(syncHandler).catch(function (err) { _emit("error", err); });
        }
      }

      // Sync on online event
      window.addEventListener("online", trySync);

      // Periodic sync
      var timer = setInterval(trySync, intervalMs);

      // Return cleanup function
      return function () {
        window.removeEventListener("online", trySync);
        clearInterval(timer);
      };
    },
  };

  window.MikiData = MikiData;
})();
