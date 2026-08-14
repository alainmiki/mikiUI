/* MikiUI HTMX runtime wrapper.
 * Configures hx-boost for SPA-like navigation and ensures CSRF-friendly
 * partial requests. HTMX core is loaded from CDN; this file adds MikiUI
 * conventions on top.
 */
(function () {
  if (typeof htmx === "undefined") return;

  // Swap only on a 200 and scroll the target into view on swap.
  htmx.config.scrollIntoViewOnBoost = true;
  htmx.config.defaultSwapStyle = "innerHTML";

  // Emit a custom event after every swap so Alpine components can re-init.
  htmx.on("htmx:afterSwap", function (evt) {
    document.dispatchEvent(
      new CustomEvent("miki:swapped", { detail: evt.detail })
    );
  });

  document.addEventListener("DOMContentLoaded", function () {
    htmx.process(document.body);
  });
})();
