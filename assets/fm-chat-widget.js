/*!
 * FM Chat Widget v1 — chat automatizado estilo WhatsApp, embutível em qualquer site estático.
 * Mesmo arquivo nos 4 sites (FM Tecnologia, NFCore, Iron Fit, Kordena); o que muda é a
 * configuração passada em window.FM_CHAT_CONFIG antes de carregar este script.
 *
 * Configuração esperada (definir ANTES de incluir este <script>):
 *   window.FM_CHAT_CONFIG = {
 *     site: "nfcore",                         // identificador do produto (bate com o backend)
 *     productName: "NFCore",                  // nome exibido no cabeçalho do chat
 *     accentColor: "#0b8457",                 // cor do botão/cabeçalho (padrão: verde WhatsApp)
 *     avatarInitial: "N",                     // letra/ícone do avatar
 *     greeting: "Olá! Posso te ajudar a conhecer o NFCore. Pergunte sobre planos, cobertura ou teste grátis.",
 *     apiBase: "https://chat.fmtecnologiaia.com.br", // endpoint do backend (vazio = modo WhatsApp direto)
 *     whatsappNumber: "5511978350851",        // número para fallback/handoff humano
 *     whatsappPrefill: "Olá! Vim pelo site do NFCore e quero falar com um atendente."
 *   };
 *
 * Sem apiBase configurado (ou se o backend estiver fora do ar), o widget funciona em modo
 * degradado: mostra uma mensagem explicando e já oferece o botão de WhatsApp real — nunca
 * fica quebrado nem passa impressão de que a automação existe quando não existe.
 */
(function () {
  "use strict";

  var CFG = window.FM_CHAT_CONFIG || {};
  var SITE = CFG.site || "fm";
  var PRODUCT = CFG.productName || "FM Tecnologia";
  var ACCENT = CFG.accentColor || "#128C7E";
  var AVATAR = (CFG.avatarInitial || PRODUCT.charAt(0) || "F").toUpperCase();
  var GREETING = CFG.greeting || "Olá! Como posso ajudar?";
  var API_BASE = (CFG.apiBase || "").replace(/\/$/, "");
  var WA_NUMBER = CFG.whatsappNumber || "";
  var WA_PREFILL = CFG.whatsappPrefill || ("Olá! Vim pelo site do " + PRODUCT + ".");
  var SESSION_KEY = "fm_chat_session_" + SITE;

  function waLink(text) {
    return "https://wa.me/" + WA_NUMBER + "?text=" + encodeURIComponent(text || WA_PREFILL);
  }

  function getSessionId() {
    try {
      var id = window.localStorage.getItem(SESSION_KEY);
      if (!id) {
        id = SITE + "-" + Date.now() + "-" + Math.random().toString(36).slice(2, 10);
        window.localStorage.setItem(SESSION_KEY, id);
      }
      return id;
    } catch (e) {
      return SITE + "-" + Date.now();
    }
  }

  var css = "" +
    "#fmchat-btn{position:fixed;bottom:20px;right:20px;width:60px;height:60px;border-radius:50%;" +
    "background:" + ACCENT + ";box-shadow:0 4px 14px rgba(0,0,0,.25);display:flex;align-items:center;" +
    "justify-content:center;cursor:pointer;z-index:999998;transition:transform .15s ease;border:none;}" +
    "#fmchat-btn:hover{transform:scale(1.06);}" +
    "#fmchat-btn svg{width:30px;height:30px;fill:#fff;}" +
    "#fmchat-panel{position:fixed;bottom:92px;right:20px;width:340px;max-width:92vw;height:480px;" +
    "max-height:72vh;background:#fff;color:#111;border-radius:14px;box-shadow:0 10px 34px rgba(0,0,0,.28);" +
    "display:none;flex-direction:column;overflow:hidden;z-index:999999;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;" +
    "text-align:left;line-height:normal;}" +
    "#fmchat-panel *{box-sizing:border-box;}" +
    "#fmchat-panel.open{display:flex;}" +
    "#fmchat-head{background:" + ACCENT + ";color:#fff;padding:12px 14px;display:flex;align-items:center;gap:10px;}" +
    "#fmchat-avatar{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.25);" +
    "display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px;}" +
    "#fmchat-head .fmchat-title{font-weight:600;font-size:14px;}" +
    "#fmchat-head .fmchat-sub{font-size:11px;opacity:.85;}" +
    "#fmchat-close{margin-left:auto;cursor:pointer;background:none;border:none;color:#fff;font-size:18px;opacity:.85;}" +
    "#fmchat-body{flex:1;overflow-y:auto;padding:12px;background:#e9edf0;display:flex;flex-direction:column;gap:8px;}" +
    ".fmchat-msg{max-width:80%;padding:8px 11px;border-radius:9px;font-size:13.5px;line-height:1.35;white-space:pre-wrap;word-wrap:break-word;color:#111;}" +
    ".fmchat-msg.bot{background:#fff;align-self:flex-start;border-top-left-radius:2px;color:#111;}" +
    ".fmchat-msg.user{background:#d9fdd3;align-self:flex-end;border-top-right-radius:2px;color:#111;}" +
    ".fmchat-msg.sys{background:transparent;align-self:center;color:#667;font-size:12px;text-align:center;}" +
    ".fmchat-typing{align-self:flex-start;background:#fff;border-radius:9px;padding:8px 12px;font-size:12px;color:#888;}" +
    "#fmchat-foot{display:flex;border-top:1px solid #ddd;padding:8px;gap:6px;background:#fff;}" +
    "#fmchat-input{flex:1;border:1px solid #ccc;border-radius:18px;padding:8px 13px;font-size:13.5px;outline:none;color:#111;background:#fff;}" +
    "#fmchat-send{background:" + ACCENT + ";border:none;color:#fff;border-radius:50%;width:36px;height:36px;" +
    "display:flex;align-items:center;justify-content:center;cursor:pointer;flex:none;}" +
    ".fmchat-wabtn{display:inline-block;margin-top:6px;background:#128C7E;color:#fff !important;text-decoration:none;" +
    "padding:7px 12px;border-radius:16px;font-size:12.5px;}";

    "#fmchat-invite{position:fixed;bottom:25px;right:92px;z-index:999997;max-width:min(300px,calc(100vw - 112px));display:flex;align-items:center;gap:6px;background:#fff;color:#172033;border:1px solid #e2e8f0;border-radius:14px;box-shadow:0 6px 22px rgba(0,0,0,.17);font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;}" +
    "#fmchat-invite[hidden]{display:none;}" +
    "#fmchat-invite-open{border:0;background:transparent;color:inherit;cursor:pointer;text-align:left;padding:10px 4px 10px 12px;min-width:0;}" +
    "#fmchat-invite-open strong{display:block;font-size:12px;line-height:1.35;color:#1e293b;}" +
    "#fmchat-invite-open span{display:block;font-size:12px;line-height:1.4;color:#475569;}" +
    "#fmchat-invite-dismiss{align-self:flex-start;flex:none;background:transparent;border:0;color:#64748b;cursor:pointer;padding:7px 9px;font-size:17px;line-height:1;}" +
    "#fmchat-invite :focus-visible{outline:2px solid #2563eb;outline-offset:2px;}" +
    "@media(max-width:480px){#fmchat-invite{bottom:23px;right:88px;max-width:calc(100vw - 108px);}#fmchat-invite-open{padding:8px 2px 8px 10px;}#fmchat-invite-open span{font-size:11px;}}" +

  var styleEl = document.createElement("style");
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  var btn = document.createElement("button");
  btn.id = "fmchat-btn";
  btn.setAttribute("aria-label", "Abrir chat");
  btn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12c0 1.85.5 3.58 1.38 5.07L2 22l5.07-1.33A9.94 9.94 0 0 0 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2z"/></svg>';
  document.body.appendChild(btn);

  var INVITATIONS = {
    fm: "Conheça nossas soluções ou fale com nossa equipe.",
    nfcore: "Precisa de ajuda com emissão fiscal ou quer conhecer o NFCore?",
    kordena: "Conheça a gestão inteligente para seu restaurante.",
    ironfit: "Tire dúvidas e descubra como transformar sua academia."
  };
  var INVITATION = CFG.invitation || INVITATIONS[SITE] || "Como podemos ajudar?";
  var INVITE_KEY = "fm_chat_invite_dismissed_" + SITE;
  var invite = document.createElement("div");
  invite.id = "fmchat-invite";
  var inviteOpen = document.createElement("button");
  inviteOpen.id = "fmchat-invite-open";
  inviteOpen.type = "button";
  inviteOpen.setAttribute("aria-label", "Abrir atendimento: " + INVITATION);
  var inviteTitle = document.createElement("strong");
  inviteTitle.textContent = "Atendimento Inteligente";
  var inviteMessage = document.createElement("span");
  inviteMessage.textContent = INVITATION;
  inviteOpen.appendChild(inviteTitle);
  inviteOpen.appendChild(inviteMessage);
  var inviteDismiss = document.createElement("button");
  inviteDismiss.id = "fmchat-invite-dismiss";
  inviteDismiss.type = "button";
  inviteDismiss.setAttribute("aria-label", "Dispensar convite de atendimento");
  inviteDismiss.textContent = "×";
  invite.appendChild(inviteOpen);
  invite.appendChild(inviteDismiss);
  document.body.appendChild(invite);
  try { invite.hidden = window.sessionStorage.getItem(INVITE_KEY) === "1"; } catch (e) {}
  inviteOpen.addEventListener("click", function () { btn.click(); });
  inviteDismiss.addEventListener("click", function () {
    invite.hidden = true;
    try { window.sessionStorage.setItem(INVITE_KEY, "1"); } catch (e) {}
  });

  var panel = document.createElement("div");
  panel.id = "fmchat-panel";
  panel.innerHTML =
    '<div id="fmchat-head">' +
      '<div id="fmchat-avatar">' + AVATAR + '</div>' +
      '<div><div class="fmchat-title">' + PRODUCT + '</div><div class="fmchat-sub">normalmente responde em poucos segundos</div></div>' +
      '<button id="fmchat-close" aria-label="Fechar">✕</button>' +
    '</div>' +
    '<div id="fmchat-body"></div>' +
    '<div id="fmchat-foot">' +
      '<input id="fmchat-input" type="text" placeholder="Digite sua mensagem..." autocomplete="off" />' +
      '<button id="fmchat-send" aria-label="Enviar"><svg viewBox="0 0 24 24" width="18" height="18"><path fill="#fff" d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg></button>' +
    '</div>';
  document.body.appendChild(panel);

  var body = panel.querySelector("#fmchat-body");
  var input = panel.querySelector("#fmchat-input");

  function addMsg(text, who) {
    var el = document.createElement("div");
    el.className = "fmchat-msg " + who;
    el.innerHTML = text;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
    return el;
  }

  function addWaButton(text, label) {
    var el = document.createElement("div");
    el.className = "fmchat-msg sys";
    el.innerHTML = '<a class="fmchat-wabtn" target="_blank" rel="noopener" href="' + waLink(text) + '">' +
      (label || "Falar no WhatsApp") + "</a>";
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
  }

  var opened = false;
  btn.addEventListener("click", function () {
    panel.classList.toggle("open");
    invite.hidden = panel.classList.contains("open") || invite.hidden;
    if (!opened && panel.classList.contains("open")) {
      opened = true;
      addMsg(GREETING, "bot");
      if (!API_BASE && WA_NUMBER) {
        addWaButton(WA_PREFILL, "Prefiro falar no WhatsApp");
      }
      input.focus();
    }
  });
  panel.querySelector("#fmchat-close").addEventListener("click", function () {
    panel.classList.remove("open");
  });

  function showTyping() {
    var t = document.createElement("div");
    t.className = "fmchat-typing";
    t.id = "fmchat-typing-now";
    t.textContent = PRODUCT + " está digitando...";
    body.appendChild(t);
    body.scrollTop = body.scrollHeight;
  }
  function hideTyping() {
    var t = document.getElementById("fmchat-typing-now");
    if (t) t.remove();
  }

  function sendMessage() {
    var text = input.value.trim();
    if (!text) return;
    addMsg(text, "user");
    input.value = "";

    if (!API_BASE) {
      // Modo degradado: sem backend configurado ainda — oferece WhatsApp real, nunca finge automação.
      addMsg("Ainda não tenho respostas automáticas configuradas aqui, mas posso te colocar direto com a nossa equipe:", "bot");
      addWaButton(text);
      return;
    }

    showTyping();
    fetch(API_BASE + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ site: SITE, message: text, session_id: getSessionId() })
    })
      .then(function (r) {
        if (!r.ok) throw new Error("status " + r.status);
        return r.json();
      })
      .then(function (data) {
        hideTyping();
        addMsg(data.reply || "Desculpe, não consegui responder agora.", "bot");
        if (data.handoff) {
          addWaButton(data.handoff_message || text, "Continuar no WhatsApp com um atendente");
        }
      })
      .catch(function () {
        hideTyping();
        addMsg("Tive um problema para responder agora. Pode falar direto com a gente:", "bot");
        addWaButton(text);
      });
  }

  panel.querySelector("#fmchat-send").addEventListener("click", sendMessage);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") sendMessage();
  });
})();
