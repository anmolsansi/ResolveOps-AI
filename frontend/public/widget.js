/**
 * ResolveOps AI — Embeddable Chat Widget (V6)
 *
 * Usage:
 *   <script src="https://your-host.com/widget.js" data-api-key="YOUR_KEY"></script>
 *
 * Creates a floating chat bubble that opens a support chat panel.
 * Uses Shadow DOM for style isolation.
 */
(function () {
  "use strict";

  var API_BASE = document.currentScript?.getAttribute("data-api-base") || window.location.origin;
  var API_KEY = document.currentScript?.getAttribute("data-api-key") || "dev-widget-key";
  var PRIMARY_COLOR = "#6366f1";
  var STORAGE_KEY = "resolveops_widget_session";

  function getSession() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY));
    } catch {
      return null;
    }
  }

  function saveSession(session) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }

  function apiPost(path, body) {
    return fetch(API_BASE + path, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Widget-Key": API_KEY,
      },
      body: JSON.stringify(body),
    }).then(function (r) {
      if (!r.ok) throw new Error("API error " + r.status);
      return r.json();
    });
  }

  function createWidget() {
    var host = document.createElement("div");
    host.id = "resolveops-widget-host";
    host.style.cssText = "position:fixed;bottom:24px;right:24px;z-index:999999;font-family:Inter,system-ui,sans-serif;";
    document.body.appendChild(host);

    var shadow = host.attachShadow({ mode: "open" });

    var styles = document.createElement("style");
    styles.textContent = "\n"
      + "* { box-sizing: border-box; margin: 0; padding: 0; }\n"
      + ".bubble { width: 60px; height: 60px; border-radius: 50%; background: " + PRIMARY_COLOR + "; "
      + "display: flex; align-items: center; justify-content: center; cursor: pointer; "
      + "box-shadow: 0 4px 16px rgba(0,0,0,0.2); transition: transform 0.2s; }\n"
      + ".bubble:hover { transform: scale(1.1); }\n"
      + ".bubble svg { width: 28px; height: 28px; fill: white; }\n"
      + ".panel { display: none; position: fixed; bottom: 96px; right: 24px; width: 380px; height: 520px; "
      + "background: white; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); "
      + "flex-direction: column; overflow: hidden; }\n"
      + ".panel.open { display: flex; }\n"
      + ".header { background: " + PRIMARY_COLOR + "; color: white; padding: 16px; "
      + "font-weight: 600; font-size: 15px; display: flex; justify-content: space-between; align-items: center; }\n"
      + ".header button { background: none; border: none; color: white; cursor: pointer; font-size: 18px; }\n"
      + ".messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }\n"
      + ".msg { max-width: 85%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.5; }\n"
      + ".msg.customer { align-self: flex-end; background: " + PRIMARY_COLOR + "; color: white; border-bottom-right-radius: 4px; }\n"
      + ".msg.ai { align-self: flex-start; background: #f3f4f6; color: #111; border-bottom-left-radius: 4px; }\n"
      + ".msg.system { align-self: center; background: #fef3c7; color: #92400e; font-size: 12px; padding: 6px 12px; }\n"
      + ".citations { margin-top: 6px; font-size: 11px; color: #6b7280; }\n"
      + ".confidence { font-size: 11px; color: #9ca3af; margin-top: 4px; }\n"
      + ".input-area { padding: 12px; border-top: 1px solid #e5e7eb; display: flex; gap: 8px; }\n"
      + ".input-area input { flex: 1; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; outline: none; }\n"
      + ".input-area input:focus { border-color: " + PRIMARY_COLOR + "; }\n"
      + ".input-area button { padding: 10px 16px; background: " + PRIMARY_COLOR + "; color: white; border: none; "
      + "border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px; }\n"
      + ".input-area button:disabled { opacity: 0.5; cursor: not-allowed; }\n"
      + ".escalation { background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 8px 12px; "
      + "font-size: 12px; color: #991b1b; margin-top: 8px; }\n"
      + ".typing { display: flex; gap: 4px; padding: 8px 14px; }\n"
      + ".typing span { width: 6px; height: 6px; background: #9ca3af; border-radius: 50%; animation: blink 1.4s infinite; }\n"
      + ".typing span:nth-child(2) { animation-delay: 0.2s; }\n"
      + ".typing span:nth-child(3) { animation-delay: 0.4s; }\n"
      + "@keyframes blink { 0%, 80%, 100% { opacity: 0.3; } 40% { opacity: 1; } }\n";

    var bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>';

    var panel = document.createElement("div");
    panel.className = "panel";
    panel.innerHTML = '\n'
      + '<div class="header"><span>Support Chat</span><button class="close-btn">&times;</button></div>\n'
      + '<div class="messages"></div>\n'
      + '<div class="input-area"><input type="text" placeholder="Ask a question..." /><button class="send-btn">Send</button></div>\n';

    shadow.appendChild(styles);
    shadow.appendChild(bubble);
    shadow.appendChild(panel);

    var messagesEl = panel.querySelector(".messages");
    var inputEl = panel.querySelector("input");
    var sendBtn = panel.querySelector(".send-btn");
    var closeBtn = panel.querySelector(".close-btn");

    var session = getSession();
    var isOpen = false;

    function addMessage(role, content, meta) {
      var div = document.createElement("div");
      div.className = "msg " + role;
      div.textContent = content;
      if (meta && meta.citations && meta.citations.length > 0) {
        var cit = document.createElement("div");
        cit.className = "citations";
        cit.textContent = "Sources: " + meta.citations.join(", ");
        div.appendChild(cit);
      }
      if (meta && meta.confidence !== undefined) {
        var conf = document.createElement("div");
        conf.className = "confidence";
        conf.textContent = "Confidence: " + Math.round(meta.confidence * 100) + "%";
        div.appendChild(conf);
      }
      messagesEl.appendChild(div);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function addSystemMessage(content) {
      addMessage("system", content);
    }

    function showTyping() {
      var div = document.createElement("div");
      div.className = "msg ai typing";
      div.innerHTML = "<span></span><span></span><span></span>";
      messagesEl.appendChild(div);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return div;
    }

    function sendMessage() {
      var text = inputEl.value.trim();
      if (!text) return;
      inputEl.value = "";
      sendBtn.disabled = true;

      addMessage("customer", text);

      var typing = showTyping();

      var payload = {
        message: text,
        conversation_id: session ? session.conversation_id : null,
        customer_email: session ? session.customer_email : null,
        customer_name: session ? session.customer_name : null,
      };

      apiPost("/widget/chat", payload)
        .then(function (data) {
          messagesEl.removeChild(typing);
          addMessage("ai", data.answer, {
            citations: data.citations,
            confidence: data.confidence,
          });
          if (data.should_escalate) {
            addSystemMessage("Escalating to a human support agent...");
          }
          saveSession({
            conversation_id: data.conversation_id,
            customer_email: payload.customer_email,
            customer_name: payload.customer_name,
          });
        })
        .catch(function () {
          messagesEl.removeChild(typing);
          addMessage("ai", "Sorry, something went wrong. Please try again.");
        })
        .finally(function () {
          sendBtn.disabled = false;
          inputEl.focus();
        });
    }

    bubble.addEventListener("click", function () {
      isOpen = !isOpen;
      panel.classList.toggle("open", isOpen);
      if (isOpen && !session) {
        addSystemMessage("Welcome! How can we help you today?");
        inputEl.focus();
      }
    });

    closeBtn.addEventListener("click", function () {
      isOpen = false;
      panel.classList.remove("open");
    });

    sendBtn.addEventListener("click", sendMessage);
    inputEl.addEventListener("keydown", function (e) {
      if (e.key === "Enter") sendMessage();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createWidget);
  } else {
    createWidget();
  }
})();
