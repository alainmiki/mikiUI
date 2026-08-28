(function () {
  "use strict";

  if (typeof window === "undefined") return;
  if (typeof window.mikiChat !== "undefined") return;

  /* ---------------------------------------------------------------
   * ChatUI — accessible chat log + input form.
   *
   * Features:
   *  - Auto-scroll to bottom on new messages.
   *  - Typing indicator with show()/hide().
   *  - Enter to send (Shift+Enter for newline in multiline mode).
   *  - Empty-input guard (no blank messages sent).
   *  - XSS-safe message insertion (textContent, not innerHTML).
   *  - Avatar + timestamp support via appendMessage().
   *  - CustomEvents: miki:chat:send { text }, miki:chat:messageadded.
   *  - Public API: mikiChat.appendMessage(el, {role,text,avatar,time}),
   *    mikiChat.clear(el), mikiChat.scrollToBottom(el),
   *    mikiChat.toggleTyping(el, bool).
   * --------------------------------------------------------------- */

  function mikiChat() {}

  function esc(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  mikiChat.init = function (el) {
    if (!el || el.dataset.mikiChatInit === "true") return;
    el.dataset.mikiChatInit = "true";

    var log = el.querySelector(".miki-chat-log");
    var form = el.querySelector('[data-miki-chat-form="true"]');
    var input = form ? form.querySelector('input[name="message"], textarea[name="message"]') : null;
    var typingIndicator = el.querySelector(".miki-chat-typing");

    if (log) mikiChat.scrollToBottom(el);

    if (input && form) {
      var typingTimer = null;
      var isTyping = false;

      on(input, "input", function () {
        if (!typingIndicator) return;
        if (!isTyping) {
          isTyping = true;
          typingIndicator.style.display = "flex";
        }
        clearTimeout(typingTimer);
        typingTimer = setTimeout(function () {
          isTyping = false;
          typingIndicator.style.display = "none";
          mikiChat.scrollToBottom(el);
        }, 500);
      });

      /* Enter to send, Shift+Enter for newline (textarea only) */
      on(input, "keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          mikiChat._submit(el, form, input);
        }
      });

      /* Submit handler */
      on(form, "submit", function (e) {
        e.preventDefault();
        mikiChat._submit(el, form, input);
      });
    }

    /* Auto-scroll on content changes */
    if (log && typeof MutationObserver !== "undefined") {
      var observer = new MutationObserver(function () {
        mikiChat.scrollToBottom(el);
      });
      observer.observe(log, { childList: true, subtree: true });
    }
  };

  mikiChat._submit = function (el, form, input) {
    if (!input) return;
    var text = input.value;
    if (text == null) return;
    text = text.trim();
    if (!text) return;

    dispatch(el, "miki:chat:send", { text: text });

    /* If the form has no hx-* / action, echo locally so the demo works */
    if (!form.getAttribute("hx-post") && !form.getAttribute("action")) {
      mikiChat.appendMessage(el, { role: "user", text: text });
      input.value = "";
      mikiChat.scrollToBottom(el);
    }
  };

  mikiChat.scrollToBottom = function (el) {
    var log = el && el.querySelector ? el.querySelector(".miki-chat-log") : null;
    if (log) log.scrollTop = log.scrollHeight;
  };

  mikiChat.toggleTyping = function (el, show) {
    if (!el || !el.querySelector) return;
    var indicator = el.querySelector(".miki-chat-typing");
    if (indicator) indicator.style.display = show ? "flex" : "none";
    mikiChat.scrollToBottom(el);
  };

  mikiChat.clear = function (el) {
    var log = el && el.querySelector ? el.querySelector(".miki-chat-log") : null;
    if (log) log.innerHTML = "";
  };

  mikiChat.appendMessage = function (el, opts) {
    opts = opts || {};
    var log = el && el.querySelector ? el.querySelector(".miki-chat-log") : null;
    if (!log) return;

    var role = opts.role === "user" ? "user" : "bot";
    var text = opts.text != null ? String(opts.text) : "";
    var avatar = opts.avatar;
    var time = opts.time;

    var bubble = document.createElement("div");
    bubble.className = "miki-chat-msg miki-chat-" + role;
    bubble.setAttribute("role", "listitem");

    if (avatar) {
      var av = document.createElement("div");
      av.className = "miki-chat-avatar";
      if (avatar.indexOf("<") === -1 && avatar.indexOf("http") !== 0 && avatar.indexOf("/") !== 0) {
        av.textContent = avatar;
      } else if (avatar.indexOf("http") === 0 || avatar.indexOf("/") === 0 || avatar.indexOf("data:") === 0) {
        var img = document.createElement("img");
        img.src = avatar;
        img.alt = role + " avatar";
        img.className = "miki-chat-avatar-img";
        av.appendChild(img);
      } else {
        av.innerHTML = avatar;
      }
      bubble.appendChild(av);
    }

    var body = document.createElement("div");
    body.className = "miki-chat-bubble-body";

    var txt = document.createElement("div");
    txt.className = "miki-chat-text";
    txt.textContent = text;
    body.appendChild(txt);

    if (time) {
      var ts = document.createElement("div");
      ts.className = "miki-chat-time";
      ts.textContent = time;
      body.appendChild(ts);
    }

    bubble.appendChild(body);
    log.appendChild(bubble);
    mikiChat.scrollToBottom(el);
    dispatch(el, "miki:chat:messageadded", { role: role, text: text });
  };

  window.mikiChat = mikiChat;
})();
