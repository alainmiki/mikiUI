(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiChat = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var log = el.querySelector(".miki-chat-log");
      var form = el.querySelector('[data-miki-chat-form="true"]');
      var input = form ? form.querySelector('input[name="message"]') : null;
      var typingIndicator = el.querySelector(".miki-chat-typing");

      if (log) {
        mikiChat.scrollToBottom(el);
      }

      if (input && form) {
        var typingTimer = null;
        var isTyping = false;

        on(input, "input", function () {
          if (typingIndicator) {
            if (!isTyping) {
              isTyping = true;
              typingIndicator.style.display = "block";
            }
            clearTimeout(typingTimer);
            typingTimer = setTimeout(function () {
              isTyping = false;
              typingIndicator.style.display = "none";
              mikiChat.scrollToBottom(el);
            }, 300);
          }
        });

        on(form, "keydown", function (e) {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            var btn = form.querySelector('button[type="submit"]') || form.querySelector("button");
            if (btn) btn.click();
          }
        });

        /* Send button: use onPointer for both mouse click and touch tap */
        var sendBtn = form.querySelector('button[type="submit"]') || form.querySelector("button");
        if (sendBtn) {
          onPointer(sendBtn, "activate", function (e) {
            /* Native form submission will handle on both mouse and touch */
          });
        }

        /* Prevent page scroll when touching the chat input area */
        on(input, "touchstart", function () {
          input.dataset.mikiChatInputTouched = "true";
        });
      }

      // Auto-scroll observer
      if (log) {
        var observer = new MutationObserver(function () {
          mikiChat.scrollToBottom(el);
        });
        observer.observe(log, { childList: true, subtree: true });
        el.dataset.mikiObserver = "active";
      }
    },

    scrollToBottom: function (el) {
      var log = el.querySelector(".miki-chat-log");
      if (log) {
        log.scrollTop = log.scrollHeight;
      }
    },

    toggleTyping: function (el, show) {
      var indicator = el.querySelector(".miki-chat-typing");
      if (indicator) {
        indicator.style.display = show ? "block" : "none";
        mikiChat.scrollToBottom(el);
      }
    }
  };

  window.mikiChat = mikiChat;
})();
