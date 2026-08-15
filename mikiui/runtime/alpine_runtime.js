/* MikiUI Alpine.js runtime wrapper.
 * Registers a small global store and helpers used by components (Tabs,
 * Modal, ListView) and wires Alpine to re-evaluate after HTMX swaps.
 */
document.addEventListener("alpine:init", function () {
  Alpine.store("miki", {
    modals: {},
    open(name) {
      this.modals[name] = true;
    },
    close(name) {
      this.modals[name] = false;
    },
    isOpen(name) {
      return !!this.modals[name];
    },
  });
});

// Re-initialize Alpine on dynamically swapped content.
document.addEventListener("miki:swapped", function () {
  if (window.Alpine) {
    Alpine.initTree(document.body);
  }
});

// Initialize Alpine when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", function () {
    if (window.Alpine) {
      Alpine.initTree(document.body);
    }
  });
} else {
  if (window.Alpine) {
    Alpine.initTree(document.body);
  }
}