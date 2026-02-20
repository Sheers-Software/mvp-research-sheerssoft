(function () {
    'use strict';

    // ─── Configuration ────────────────────────────────────────
    const scriptEl = document.currentScript;
    const API_URL = scriptEl.getAttribute('data-api-url') || 'http://localhost:8000';
    const PROPERTY_ID = scriptEl.getAttribute('data-property-id');
    const THEME_COLOR = scriptEl.getAttribute('data-color') || '#0F172A';
    const GREETING = scriptEl.getAttribute('data-greeting') || 'Hi! 👋 Welcome to our hotel. How can I help you today?';
    const HEADER_TITLE = scriptEl.getAttribute('data-title') || 'Concierge';
    const PRIVACY_URL = scriptEl.getAttribute('data-privacy-url') || '#';

    if (!PROPERTY_ID) {
        console.error('Nocturn Widget: data-property-id is required');
        return;
    }

    // ─── Styles ───────────────────────────────────────────────
    const style = document.createElement('style');
    style.textContent = `
        #nocturn-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 99999;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: #1e293b;
        }

        /* ─── Launcher ─── */
        #nocturn-launcher {
            width: 56px;
            height: 56px;
            background: ${THEME_COLOR};
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        #nocturn-launcher:hover {
            transform: scale(1.08);
            box-shadow: 0 6px 24px rgba(0,0,0,0.3);
        }
        #nocturn-launcher svg { width: 28px; height: 28px; fill: #fff; }

        /* ─── Chat Window ─── */
        #nocturn-chat {
            position: absolute;
            bottom: 72px;
            right: 0;
            width: 380px;
            max-width: calc(100vw - 32px);
            height: 520px;
            max-height: calc(100vh - 100px);
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 8px 40px rgba(0,0,0,0.18);
            display: none;
            flex-direction: column;
            overflow: hidden;
            opacity: 0;
            transform: translateY(16px) scale(0.97);
            transition: opacity 0.25s ease, transform 0.25s ease;
        }
        #nocturn-chat.open {
            display: flex;
            opacity: 1;
            transform: translateY(0) scale(1);
        }

        /* ─── Header ─── */
        .nocturn-header {
            background: ${THEME_COLOR};
            color: #fff;
            padding: 14px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }
        .nocturn-header h3 { margin: 0; font-size: 15px; font-weight: 600; }
        .nocturn-header-status {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 2px;
        }
        .nocturn-close {
            cursor: pointer;
            font-size: 22px;
            line-height: 1;
            background: none;
            border: none;
            color: #fff;
            opacity: 0.7;
            transition: opacity 0.15s;
            padding: 0 4px;
        }
        .nocturn-close:hover { opacity: 1; }

        /* ─── Consent Banner ─── */
        .nocturn-consent {
            padding: 16px;
            background: #fefce8;
            border-bottom: 1px solid #fde68a;
            font-size: 12px;
            color: #713f12;
            display: flex;
            flex-direction: column;
            gap: 10px;
            flex-shrink: 0;
        }
        .nocturn-consent p { margin: 0; }
        .nocturn-consent a { color: #92400e; text-decoration: underline; }
        .nocturn-consent-btn {
            background: ${THEME_COLOR};
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            align-self: flex-start;
            transition: opacity 0.15s;
        }
        .nocturn-consent-btn:hover { opacity: 0.9; }

        /* ─── Messages ─── */
        .nocturn-messages {
            flex: 1;
            padding: 14px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
            background: #f8fafc;
        }
        .nocturn-msg {
            max-width: 82%;
            padding: 10px 14px;
            border-radius: 14px;
            font-size: 13.5px;
            line-height: 1.5;
            word-wrap: break-word;
            animation: nocturn-fadein 0.2s ease;
        }
        @keyframes nocturn-fadein {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .nocturn-msg.guest {
            align-self: flex-end;
            background: ${THEME_COLOR};
            color: #fff;
            border-bottom-right-radius: 4px;
        }
        .nocturn-msg.ai {
            align-self: flex-start;
            background: #fff;
            color: #1e293b;
            border-bottom-left-radius: 4px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }

        /* ─── Typing Indicator ─── */
        .nocturn-typing {
            font-size: 12px;
            color: #94a3b8;
            padding: 0 14px 6px;
            display: none;
            flex-shrink: 0;
        }
        .nocturn-typing.visible { display: block; }

        /* ─── Input ─── */
        .nocturn-input-area {
            padding: 12px 14px;
            background: #fff;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 8px;
            flex-shrink: 0;
        }
        .nocturn-input-area input {
            flex: 1;
            padding: 9px 14px;
            border: 1px solid #e2e8f0;
            border-radius: 24px;
            font-size: 13.5px;
            outline: none;
            transition: border-color 0.15s;
            font-family: inherit;
        }
        .nocturn-input-area input:focus { border-color: ${THEME_COLOR}; }
        .nocturn-input-area input:disabled {
            background: #f1f5f9;
            cursor: not-allowed;
        }
        .nocturn-send {
            background: none;
            border: none;
            cursor: pointer;
            color: ${THEME_COLOR};
            font-size: 18px;
            padding: 2px 6px;
            transition: transform 0.15s;
        }
        .nocturn-send:hover { transform: scale(1.15); }
        .nocturn-send:disabled { opacity: 0.3; cursor: not-allowed; }

        /* ─── Mobile ─── */
        @media (max-width: 480px) {
            #nocturn-widget { bottom: 12px; right: 12px; }
            #nocturn-launcher { width: 50px; height: 50px; }
            #nocturn-launcher svg { width: 24px; height: 24px; }
            #nocturn-chat {
                bottom: 0;
                right: 0;
                left: 0;
                width: 100vw;
                max-width: 100vw;
                height: 100vh;
                max-height: 100vh;
                border-radius: 0;
                position: fixed;
            }
        }
    `;
    document.head.appendChild(style);

    // ─── DOM ──────────────────────────────────────────────────
    const widget = document.createElement('div');
    widget.id = 'nocturn-widget';

    const launcher = document.createElement('div');
    launcher.id = 'nocturn-launcher';
    launcher.setAttribute('aria-label', 'Open chat');
    launcher.innerHTML = '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>';

    const chat = document.createElement('div');
    chat.id = 'nocturn-chat';
    chat.innerHTML = `
        <div class="nocturn-header">
            <div>
                <h3>${HEADER_TITLE}</h3>
                <div class="nocturn-header-status" id="nocturn-status">Online</div>
            </div>
            <button class="nocturn-close" aria-label="Close chat">&times;</button>
        </div>
        <div class="nocturn-consent" id="nocturn-consent" style="display:none;">
            <p>🔒 By continuing, you agree to our <a href="${PRIVACY_URL}" target="_blank">Privacy Policy</a>. Your conversation data is processed in accordance with Malaysia's PDPA 2010.</p>
            <button class="nocturn-consent-btn" id="nocturn-accept">I Agree &amp; Continue</button>
        </div>
        <div class="nocturn-messages" id="nocturn-messages"></div>
        <div class="nocturn-typing" id="nocturn-typing">${HEADER_TITLE} is typing…</div>
        <div class="nocturn-input-area">
            <input type="text" id="nocturn-input" placeholder="Ask about rooms, rates, facilities…" disabled />
            <button class="nocturn-send" id="nocturn-send" disabled>➤</button>
        </div>
    `;

    widget.appendChild(chat);
    widget.appendChild(launcher);
    document.body.appendChild(widget);

    // ─── State ────────────────────────────────────────────────
    let isOpen = false;
    let consentGiven = localStorage.getItem('nocturn_consent') === 'true';
    let sessionId = localStorage.getItem('nocturn_session') || crypto.randomUUID();
    let ws = null;
    let wsConnected = false;

    localStorage.setItem('nocturn_session', sessionId);

    const messagesEl = document.getElementById('nocturn-messages');
    const inputEl = document.getElementById('nocturn-input');
    const sendBtn = document.getElementById('nocturn-send');
    const typingEl = document.getElementById('nocturn-typing');
    const consentEl = document.getElementById('nocturn-consent');
    const statusEl = document.getElementById('nocturn-status');

    // ─── Consent ──────────────────────────────────────────────
    function showConsent() {
        if (consentGiven) {
            enableChat();
            return;
        }
        consentEl.style.display = 'flex';
        inputEl.disabled = true;
        sendBtn.disabled = true;
    }

    function enableChat() {
        consentEl.style.display = 'none';
        inputEl.disabled = false;
        sendBtn.disabled = false;
        inputEl.focus();
        connectWebSocket();
    }

    document.getElementById('nocturn-accept').addEventListener('click', function () {
        consentGiven = true;
        localStorage.setItem('nocturn_consent', 'true');
        enableChat();
    });

    // ─── Toggle ───────────────────────────────────────────────
    function toggleChat() {
        isOpen = !isOpen;
        chat.classList.toggle('open', isOpen);
        if (isOpen) {
            showConsent();
            if (messagesEl.children.length === 0) {
                appendMsg('ai', GREETING);
            }
        }
    }

    launcher.addEventListener('click', toggleChat);
    chat.querySelector('.nocturn-close').addEventListener('click', toggleChat);

    // ─── Messages ─────────────────────────────────────────────
    function appendMsg(role, text) {
        const div = document.createElement('div');
        div.className = 'nocturn-msg ' + role;
        div.textContent = text;
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function showTyping(v) {
        typingEl.classList.toggle('visible', v);
    }

    // ─── WebSocket ────────────────────────────────────────────
    function connectWebSocket() {
        if (ws && ws.readyState <= 1) return; // Already connected or connecting

        const wsUrl = API_URL.replace(/^http/, 'ws') + '/api/v1/ws/chat?property_id=' + PROPERTY_ID + '&session_id=' + sessionId;

        try {
            ws = new WebSocket(wsUrl);
        } catch (e) {
            console.warn('Nocturn: WebSocket creation failed, using HTTP fallback');
            wsConnected = false;
            statusEl.textContent = 'Online';
            return;
        }

        ws.onopen = function () {
            wsConnected = true;
            statusEl.textContent = 'Connected';
        };

        ws.onmessage = function (event) {
            showTyping(false);
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'ai_response') {
                    appendMsg('ai', data.response);
                } else if (data.type === 'typing') {
                    showTyping(true);
                } else if (data.type === 'error') {
                    appendMsg('ai', 'Sorry, something went wrong. Please try again.');
                }
            } catch (e) {
                // Plain text response
                appendMsg('ai', event.data);
            }
        };

        ws.onerror = function () {
            console.warn('Nocturn: WebSocket error, falling back to HTTP');
            wsConnected = false;
            statusEl.textContent = 'Online';
        };

        ws.onclose = function () {
            wsConnected = false;
            statusEl.textContent = 'Online';
            // Reconnect after 5 seconds if chat is still open
            if (isOpen && consentGiven) {
                setTimeout(connectWebSocket, 5000);
            }
        };
    }

    // ─── Send ─────────────────────────────────────────────────
    async function sendMessage() {
        const text = inputEl.value.trim();
        if (!text) return;

        appendMsg('guest', text);
        inputEl.value = '';
        showTyping(true);

        // Try WebSocket first, fall back to HTTP
        if (wsConnected && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                message: text,
                session_id: sessionId,
                property_id: PROPERTY_ID,
            }));
        } else {
            // HTTP fallback
            try {
                const res = await fetch(API_URL + '/api/v1/conversations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        property_id: PROPERTY_ID,
                        message: text,
                        session_id: sessionId,
                    }),
                });
                const data = await res.json();
                showTyping(false);
                appendMsg('ai', data.response || 'Sorry, I could not process your request.');
            } catch (err) {
                console.error('Nocturn: HTTP send failed', err);
                showTyping(false);
                appendMsg('ai', 'Sorry, I\'m having trouble connecting. Please try again shortly.');
            }
        }
    }

    inputEl.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') sendMessage();
    });
    sendBtn.addEventListener('click', sendMessage);

})();
