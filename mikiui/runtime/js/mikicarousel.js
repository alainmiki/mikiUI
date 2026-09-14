(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiCarousel = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      el.setAttribute("data-miki-current-index", "0");

      var slides = el.querySelectorAll(".miki-carousel-slide");
      var dots = el.querySelectorAll(".miki-carousel-dot");

      var prevBtn = el.querySelector(".miki-carousel-prev");
      var nextBtn = el.querySelector(".miki-carousel-next");

      var nextCleanup = null;
      var prevCleanup = null;
      if (nextBtn) {
        nextCleanup = onPointer(nextBtn, "activate", function () { mikiCarousel.next(el); });
      }
      if (prevBtn) {
        prevCleanup = onPointer(prevBtn, "activate", function () { mikiCarousel.prev(el); });
      }

      var dotCleanups = [];
      for (var i = 0; i < dots.length; i++) {
        (function (dot, idx) {
          dot.setAttribute("data-index", idx);
          var cleanup = onPointer(dot, "activate", function () { mikiCarousel.goTo(el, idx); });
          dotCleanups.push(cleanup);
        })(dots[i], i);
      }

      var autoplay = el.getAttribute("data-autoplay") === "true";
      if (autoplay) {
        var interval = parseInt(el.getAttribute("data-interval") || "4000", 10);
        mikiCarousel.startAutoplay(el, interval);
      }

      var enterHandler = function () { mikiCarousel.stopAutoplay(el); };
      var leaveHandler = function () {
        if (el.getAttribute("data-autoplay") === "true") {
          var interval = parseInt(el.getAttribute("data-interval") || "4000", 10);
          mikiCarousel.startAutoplay(el, interval);
        }
      };
      on(el, "mouseenter", enterHandler);
      on(el, "mouseleave", leaveHandler);

      on(el, "keydown", function (e) {
        if (e.key === "ArrowLeft") {
          e.preventDefault();
          mikiCarousel.prev(el);
        } else if (e.key === "ArrowRight") {
          e.preventDefault();
          mikiCarousel.next(el);
        }
      });

      var startX = 0;
      var startY = 0;
      var threshold = 50;
      var restraint = 100;
      var allowswipe = true;
      var endX = 0;
      var endY = 0;

      on(el, "touchstart", function (e) {
        if (e.touches.length !== 1) return;
        var touch = e.touches[0];
        startX = touch.clientX;
        startY = touch.clientY;
        allowswipe = true;
        mikiCarousel.stopAutoplay(el);
      }, { passive: true });

      on(el, "touchmove", function (e) {
        if (e.touches.length !== 1 || !allowswipe) return;
      }, { passive: true });

      on(el, "touchmove", function (e) {
        if (e.touches.length !== 1) return;
        endX = e.touches[0].clientX;
        endY = e.touches[0].clientY;
      }, { passive: true });

      on(el, "touchend", function (e) {
        var distX = endX - startX;
        var distY = endY - startY;
        if (Math.abs(distX) >= threshold && Math.abs(distY) <= restraint) {
          if (distX > 0) {
            mikiCarousel.prev(el);
          } else {
            mikiCarousel.next(el);
          }
        }
        if (el.getAttribute("data-autoplay") === "true") {
          var interval = parseInt(el.getAttribute("data-interval") || "4000", 10);
          mikiCarousel.startAutoplay(el, interval);
        }
      });

      registerDestroyHandler(el, function () {
        if (nextCleanup) nextCleanup();
        if (prevCleanup) prevCleanup();
        for (var j = 0; j < dotCleanups.length; j++) {
          dotCleanups[j]();
        }
        off(el, "mouseenter", enterHandler);
        off(el, "mouseleave", leaveHandler);
        mikiCarousel.stopAutoplay(el);
      });
    },

    destroy: function (el) {
      mikiDestroy(el);
    },

    next: function (el) {
      var slides = el.querySelectorAll(".miki-carousel-slide");
      if (!slides.length) return;
      var current = parseInt(el.getAttribute("data-miki-current-index") || "0", 10);
      var next = (current + 1) % slides.length;
      mikiCarousel.goTo(el, next);
    },

    prev: function (el) {
      var slides = el.querySelectorAll(".miki-carousel-slide");
      if (!slides.length) return;
      var current = parseInt(el.getAttribute("data-miki-current-index") || "0", 10);
      var prev = (current - 1 + slides.length) % slides.length;
      mikiCarousel.goTo(el, prev);
    },

    goTo: function (el, index) {
      var slides = el.querySelectorAll(".miki-carousel-slide");
      var dots = el.querySelectorAll(".miki-carousel-dot");
      if (index < 0) index = slides.length - 1;
      if (index >= slides.length) index = 0;

      for (var i = 0; i < slides.length; i++) {
        if (i === index) {
          slides[i].classList.remove("miki-carousel-slide-hidden");
        } else {
          slides[i].classList.add("miki-carousel-slide-hidden");
        }
      }

      for (var j = 0; j < dots.length; j++) {
        if (j === index) {
          dots[j].classList.add("miki-carousel-dot-active");
        } else {
          dots[j].classList.remove("miki-carousel-dot-active");
        }
      }

      el.setAttribute("data-miki-current-index", index);
      dispatch(el, "miki:carousel:changed", { index: index });
    },

    startAutoplay: function (el, interval) {
      if (el.dataset.mikiAutoplayId) {
        clearInterval(parseInt(el.dataset.mikiAutoplayId, 10));
      }
      el.classList.remove("paused");
      var id = setInterval(function () {
        mikiCarousel.next(el);
      }, interval);
      el.dataset.mikiAutoplayId = String(id);
    },

    stopAutoplay: function (el) {
      if (el.dataset.mikiAutoplayId) {
        clearInterval(parseInt(el.dataset.mikiAutoplayId, 10));
        delete el.dataset.mikiAutoplayId;
      }
      el.classList.add("paused");
    }
  };

  window.mikiCarousel = mikiCarousel;
})();
