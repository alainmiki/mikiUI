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

      if (nextBtn) {
        on(nextBtn, "click", function () { mikiCarousel.next(el); });
      }
      if (prevBtn) {
        on(prevBtn, "click", function () { mikiCarousel.prev(el); });
      }

      for (var i = 0; i < dots.length; i++) {
        (function (dot, idx) {
          dot.setAttribute("data-index", idx);
          on(dot, "click", function () { mikiCarousel.goTo(el, idx); });
        })(dots[i], i);
      }

      var autoplay = el.getAttribute("data-autoplay") === "true";
      if (autoplay) {
        var interval = parseInt(el.getAttribute("data-interval") || "4000", 10);
        mikiCarousel.startAutoplay(el, interval);
      }

      on(el, "mouseenter", function () {
        mikiCarousel.stopAutoplay(el);
      });
      on(el, "mouseleave", function () {
        if (el.getAttribute("data-autoplay") === "true") {
          var interval = parseInt(el.getAttribute("data-interval") || "4000", 10);
          mikiCarousel.startAutoplay(el, interval);
        }
      });

      // Keyboard navigation
      on(el, "keydown", function (e) {
        if (e.key === "ArrowLeft") {
          e.preventDefault();
          mikiCarousel.prev(el);
        } else if (e.key === "ArrowRight") {
          e.preventDefault();
          mikiCarousel.next(el);
        }
      });
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
