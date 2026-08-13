/* Ari Thai Catering - chat widget.
 *
 * Loaded only when site.config.json has a chat_endpoint (see tools/build.py),
 * so a page never carries a dead launcher. No dependencies, no build step, and
 * the whole widget is built here rather than in the page markup - that keeps
 * it out of all eight templates and off the critical render path.
 *
 * The model's reply is inserted as text, never as HTML. Links are added
 * afterwards, and only for a fixed list of our own contact details - the
 * assistant cannot put a link on the page, whatever it writes.
 */
(function () {
  "use strict";

  var CFG = window.ARI_CHAT;
  if (!CFG || !CFG.endpoint) return;

  var STORE_KEY = "ari-chat-v1";
  var GREETING =
    "Hi - I can help with packages, pricing, the menu and how catering works. " +
    "What are you planning?";
  var SUGGESTIONS = [
    "What is included in a package?",
    "How much for 25 people?",
    "Do you cater for vegans?",
    "How much notice do you need?"
  ];
  var FALLBACK =
    "Sorry - I could not reach the kitchen just then. Email " +
    CFG.email + " or use the enquiry form and we will come straight back to you.";

  // Only these strings ever become links in a reply.
  var LINKABLE = [
    { re: CFG.site + "/enquiry/", href: "/enquiry/" },
    { re: CFG.email, href: "mailto:" + CFG.email },
    { re: CFG.phone, href: "tel:" + CFG.phone.replace(/\s/g, "") }
  ];

  var history = load();
  var busy = false;
  var controller = null;
  var el = {};

  // ------------------------------------------------------------------ utils

  function load() {
    try {
      var raw = sessionStorage.getItem(STORE_KEY);
      var parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      return [];
    }
  }

  function save() {
    try {
      sessionStorage.setItem(STORE_KEY, JSON.stringify(history));
    } catch (e) {
      /* private mode, quota - the conversation just will not survive a reload */
    }
  }

  /* An error whose message came from our own endpoint, so it is safe to show
     to a customer (rate limits, message-too-long, the worker's own apology). */
  function serverError(message) {
    var err = new Error(message || FALLBACK);
    err.fromServer = Boolean(message);
    return err;
  }

  function make(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text) node.textContent = text;
    return node;
  }

  /* Escapes a string for use inside a RegExp. */
  function esc(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  var LINK_RE = new RegExp("(" + LINKABLE.map(function (l) { return esc(l.re); }).join("|") + ")", "g");

  /* Writes text into a node, turning only our own contact details into links. */
  function writeText(node, text) {
    node.textContent = "";
    var parts = text.split(LINK_RE);
    for (var i = 0; i < parts.length; i++) {
      var part = parts[i];
      if (!part) continue;
      var match = null;
      for (var j = 0; j < LINKABLE.length; j++) {
        if (LINKABLE[j].re === part) { match = LINKABLE[j]; break; }
      }
      if (match) {
        var a = make("a", null, part);
        a.href = match.href;
        node.appendChild(a);
      } else {
        node.appendChild(document.createTextNode(part));
      }
    }
  }

  // -------------------------------------------------------------------- DOM

  function build() {
    el.launcher = make("button", "chat-launcher");
    el.launcher.type = "button";
    el.launcher.setAttribute("aria-expanded", "false");
    el.launcher.innerHTML =
      '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">' +
      '<path d="M4 5.5h16v11H9.5L5 20.5v-4H4v-11Z" stroke="currentColor" stroke-width="1.8" ' +
      'stroke-linejoin="round"/><path d="M8.5 10h7M8.5 13h4.5" stroke="currentColor" ' +
      'stroke-width="1.8" stroke-linecap="round"/></svg><span>Ask a question</span>';

    el.panel = make("div", "chat-panel");
    el.panel.hidden = true;
    el.panel.setAttribute("role", "dialog");
    el.panel.setAttribute("aria-modal", "false");
    el.panel.setAttribute("aria-labelledby", "chat-title");

    var head = make("div", "chat-panel__head");
    var title = make("div", "chat-panel__title");
    title.id = "chat-title";
    title.appendChild(make("strong", null, "Ask Ari"));
    title.appendChild(make("span", null, "Catering questions, answered on the spot"));
    var close = make("button", "chat-close");
    close.type = "button";
    close.setAttribute("aria-label", "Close chat");
    close.innerHTML =
      '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">' +
      '<path d="M5 5l10 10M15 5L5 15" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round"/></svg>';
    head.appendChild(title);
    head.appendChild(close);

    el.log = make("div", "chat-log");
    el.log.setAttribute("role", "log");
    el.log.setAttribute("aria-live", "polite");
    el.log.setAttribute("aria-label", "Conversation");

    el.chips = make("div", "chat-chips");
    SUGGESTIONS.forEach(function (q) {
      var chip = make("button", "chat-chip", q);
      chip.type = "button";
      chip.addEventListener("click", function () { send(q); });
      el.chips.appendChild(chip);
    });

    el.form = make("form", "chat-form");
    el.input = make("textarea", "chat-input");
    el.input.rows = 1;
    el.input.placeholder = "Ask about packages, the menu, delivery...";
    el.input.setAttribute("aria-label", "Your question");
    el.input.maxLength = 1000;
    el.send = make("button", "chat-send");
    el.send.type = "submit";
    el.send.setAttribute("aria-label", "Send");
    el.send.innerHTML =
      '<svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">' +
      '<path d="M3 10h13M11 5l5 5-5 5" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" stroke-linejoin="round"/></svg>';
    el.form.appendChild(el.input);
    el.form.appendChild(el.send);

    var foot = make("div", "chat-foot");
    foot.appendChild(document.createTextNode("AI assistant - it can get things wrong. For allergies and firm quotes, "));
    var link = make("a", null, "use the enquiry form");
    link.href = "/enquiry/";
    foot.appendChild(link);
    foot.appendChild(document.createTextNode("."));

    el.panel.appendChild(head);
    el.panel.appendChild(el.log);
    el.panel.appendChild(el.chips);
    el.panel.appendChild(el.form);
    el.panel.appendChild(foot);

    document.body.appendChild(el.launcher);
    document.body.appendChild(el.panel);

    el.launcher.addEventListener("click", toggle);
    close.addEventListener("click", function () { setOpen(false); el.launcher.focus(); });
    el.form.addEventListener("submit", function (e) {
      e.preventDefault();
      send(el.input.value);
    });
    el.input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send(el.input.value);
      }
    });
    el.input.addEventListener("input", grow);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !el.panel.hidden) {
        setOpen(false);
        el.launcher.focus();
      }
    });
  }

  function grow() {
    el.input.style.height = "auto";
    el.input.style.height = Math.min(el.input.scrollHeight, 120) + "px";
  }

  function toggle() {
    setOpen(el.panel.hidden);
  }

  function setOpen(open) {
    el.panel.hidden = !open;
    el.launcher.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("chat-open", open);
    if (open) {
      el.input.focus();
      scroll();
    } else if (controller) {
      controller.abort();
    }
  }

  function scroll() {
    el.log.scrollTop = el.log.scrollHeight;
  }

  /* Appends a bubble and returns the node its text lives in. */
  function bubble(role, text) {
    var wrap = make("div", "chat-msg chat-msg--" + role);
    var body = make("div", "chat-msg__body");
    writeText(body, text || "");
    wrap.appendChild(body);
    el.log.appendChild(wrap);
    scroll();
    return body;
  }

  function render() {
    el.log.textContent = "";
    bubble("bot", GREETING);
    history.forEach(function (m) {
      bubble(m.role === "user" ? "user" : "bot", m.content);
    });
    el.chips.hidden = history.length > 0;
    scroll();
  }

  // ------------------------------------------------------------- networking

  function send(text) {
    text = (text || "").trim();
    if (!text || busy) return;

    el.input.value = "";
    grow();
    el.chips.hidden = true;
    history.push({ role: "user", content: text });
    bubble("user", text);
    save();

    var node = bubble("bot", "");
    var dots = make("span", "chat-dots");
    dots.setAttribute("aria-label", "Typing");
    node.appendChild(dots);
    setBusy(true);

    controller = new AbortController();
    var answer = "";

    fetch(CFG.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history }),
      signal: controller.signal
    })
      .then(function (res) {
        if (!res.ok || !res.body) {
          return res.json().catch(function () { return {}; }).then(function (data) {
            throw serverError(data.error);
          });
        }
        return readStream(res.body, function (chunk) {
          answer += chunk;
          writeText(node, answer);
          scroll();
        });
      })
      .then(function () {
        if (!answer) throw new Error("Empty reply");
        history.push({ role: "assistant", content: answer });
        save();
      })
      .catch(function (err) {
        if (err && err.name === "AbortError") {
          node.parentNode.remove();
          return;
        }
        // Drop the failed turn so a retry does not resend a broken exchange.
        history.pop();
        save();
        // Only ever show a message we wrote ourselves - a network failure's
        // own text ("Failed to fetch") means nothing to a customer.
        var shown = err && err.fromServer ? err.message : FALLBACK;
        writeText(node, answer ? answer + "\n\n" + shown : shown);
        node.parentNode.classList.add("chat-msg--error");
      })
      .then(function () {
        setBusy(false);
        controller = null;
      });
  }

  /* Reads our SSE format: one JSON object per "data:" line. */
  function readStream(body, onText) {
    var reader = body.getReader();
    var decoder = new TextDecoder();
    var buffer = "";

    function pump() {
      return reader.read().then(function (result) {
        if (result.done) return;
        buffer += decoder.decode(result.value, { stream: true });
        var lines = buffer.split("\n");
        buffer = lines.pop();
        for (var i = 0; i < lines.length; i++) {
          var line = lines[i].trim();
          if (line.indexOf("data:") !== 0) continue;
          var evt;
          try {
            evt = JSON.parse(line.slice(5));
          } catch (e) {
            continue;
          }
          if (evt.type === "text") onText(evt.text);
          else if (evt.type === "error") throw serverError(evt.message);
        }
        return pump();
      });
    }
    return pump();
  }

  function setBusy(state) {
    busy = state;
    el.send.disabled = state;
    el.input.disabled = state;
    el.panel.classList.toggle("is-busy", state);
    if (!state) {
      var dots = el.log.querySelector(".chat-dots");
      if (dots) dots.remove();
      el.input.focus();
    }
  }

  // -------------------------------------------------------------------- go

  build();
  render();
})();
