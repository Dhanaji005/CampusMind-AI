/* =====================================================
   CAMPUSMIND AI — PRODUCTION CHATBOT CLIENT
   Personalized Student-Aware AI, Grounded RAG & File Vision
===================================================== */

(function () {
    "use strict";

    // -----------------------------------------------------
    // CONFIG & API BASE
    // -----------------------------------------------------
    const API_BASE = (function () {
        if (window.CAMPUSMIND_API_BASE) return window.CAMPUSMIND_API_BASE;
        try {
            if (window.location && window.location.protocol && window.location.protocol.startsWith("http")) {
                const port = window.location.port;
                if (!port || port === "80" || port === "443" || port === "5000") {
                    return window.location.origin;
                }
                if (window.location.hostname) {
                    return window.location.protocol + "//" + window.location.hostname + ":5000";
                }
            }
        } catch (e) {}
        return "http://127.0.0.1:5000";
    })();

    const CHAT_ENDPOINT = API_BASE + "/api/chatbot/chat";
    const UPLOAD_ENDPOINT = API_BASE + "/api/chatbot/upload";

    const conversation = [];
    let activeSessionId = null;

    // -----------------------------------------------------
    // UTILITY HELPERS
    // -----------------------------------------------------
    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatTime(date) {
        const d = date || new Date();
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function renderMarkdownLite(text) {
        let html = escapeHtml(text || "");

        // Code blocks ```lang ... ```
        html = html.replace(/```([a-zA-Z0-9_-]*)\n?([\s\S]*?)```/g, function (_m, lang, code) {
            return "<pre><code class='language-" + escapeHtml(lang) + "'>" + code + "</code></pre>";
        });

        // Inline code `...`
        html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

        // Bold **...**
        html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

        // Headers
        html = html.replace(/^### (.*$)/gim, "<h3 style='margin:10px 0 4px;font-size:15px;color:#00d4ff;'>$1</h3>");
        html = html.replace(/^## (.*$)/gim, "<h2 style='margin:12px 0 6px;font-size:16px;color:#7dd3fc;'>$1</h2>");
        html = html.replace(/^# (.*$)/gim, "<h1 style='margin:14px 0 8px;font-size:18px;color:#ffffff;'>$1</h1>");

        // Bullet points
        html = html.replace(/^\s*[-*]\s+(.*)$/gim, "<li style='margin-left:18px;'>$1</li>");

        // Paragraphs & Line breaks
        html = html.replace(/\n\n+/g, "</p><p>");
        html = html.replace(/\n/g, "<br>");

        return "<p>" + html + "</p>";
    }

    // -----------------------------------------------------
    // AUTH & ROLE CONTEXT
    // -----------------------------------------------------
    function getUserProfile() {
        const rawUser = localStorage.getItem("campusmind_user");
        if (rawUser) {
            try {
                return JSON.parse(rawUser);
            } catch (e) {
                return null;
            }
        }
        return null;
    }

    function getAuthToken() {
        return localStorage.getItem("campusmind_jwt") || null;
    }

    // -----------------------------------------------------
    // BACKEND API COMMUNICATION
    // -----------------------------------------------------
    async function sendToBackend(message, attachments) {
        const token = getAuthToken();
        const user = getUserProfile();
        const persona = (user && user.role) ? user.role : "student";

        const headers = { "Content-Type": "application/json" };
        if (token) headers["Authorization"] = "Bearer " + token;

        const payload = {
            message: message,
            history: conversation.slice(0, -1), // Prior conversation turns excluding the current active prompt
            attachments: attachments || [],
            persona: persona,
            use_rag: true, // Always automatically enabled
            session_id: activeSessionId
        };

        let response;
        try {
            response = await fetch(CHAT_ENDPOINT, {
                method: "POST",
                headers: headers,
                body: JSON.stringify(payload)
            });
        } catch (fetchErr) {
            throw new Error("Cannot connect to CampusMind AI backend at " + API_BASE + ". Please ensure the backend is running via 'run.bat' or 'python app.py' in the bakend folder.");
        }

        let data = null;
        try {
            data = await response.json();
        } catch (e) {
            throw new Error("Server returned an invalid response (HTTP " + response.status + ").");
        }

        if (!response.ok || !data.success) {
            throw new Error((data && data.error) || "Request failed with status " + response.status);
        }

        if (data.session_id) {
            activeSessionId = data.session_id;
        }

        return data;
    }

    // -----------------------------------------------------
    // 1) QUICK CHAT WIDGET (on Home Page)
    // -----------------------------------------------------
    function initQuickInput() {
        const input = document.getElementById("ai-quick-input");
        const btn   = document.getElementById("ai-quick-send");
        const out   = document.getElementById("ai-quick-reply");

        if (!input || !btn || !out) return;

        async function send() {
            const text = (input.value || "").trim();
            if (!text) {
                input.focus();
                return;
            }

            conversation.push({ role: "user", content: text });

            const original = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

            out.hidden = false;
            out.classList.add("loading");
            out.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Consulting campus knowledge…';

            try {
                const data = await sendToBackend(text, []);
                const reply = data.reply || "(no reply)";

                conversation.push({ role: "assistant", content: reply });

                out.classList.remove("loading");
                out.classList.add("reply");

                let citationsHtml = "";
                if (data.sources && data.sources.length > 0) {
                    citationsHtml = '<div style="margin-top:8px;font-size:11.5px;color:#00d4ff;"><i class="fa-solid fa-file-shield"></i> Verified from: '
                        + data.sources.map(s => escapeHtml(s.title)).join(", ") + '</div>';
                }

                out.innerHTML =
                    '<div class="ai-quick-reply-label"><i class="fa-solid fa-brain"></i> CampusMind AI</div>'
                    + '<div class="ai-quick-reply-body">'
                    + renderMarkdownLite(reply)
                    + citationsHtml
                    + '</div>';

                input.value = "";
            } catch (err) {
                if (conversation.length > 0 && conversation[conversation.length - 1].role === "user") {
                    conversation.pop();
                }
                out.classList.remove("loading");
                out.classList.add("error");
                out.innerHTML =
                    '<i class="fa-solid fa-triangle-exclamation"></i> '
                    + escapeHtml(err.message || "Something went wrong.");
            } finally {
                btn.disabled = false;
                btn.innerHTML = original;
            }
        }

        btn.addEventListener("click", send);
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
            }
        });
    }

    // -----------------------------------------------------
    // 2) FULL-SCREEN PRODUCTION CHATBOT
    // -----------------------------------------------------
    function initFullChat() {
        const dropZone = document.getElementById("chat-drop-zone");
        const log = document.getElementById("chat-log");
        const input = document.getElementById("chat-input");
        const sendBtn = document.getElementById("chat-send");
        const voiceBtn = document.getElementById("chat-voice-btn");
        const newChatBtn = document.getElementById("chat-new-btn");
        const attachBtn = document.getElementById("chat-attach-btn");
        const fileInput = document.getElementById("chat-file-input");
        const previewTray = document.getElementById("chat-attachments-preview");
        const userStatusBadge = document.getElementById("header-user-status");

        // Citation Modal Elements
        const modal = document.getElementById("source-modal");
        const modalTitle = document.getElementById("modal-source-title");
        const modalCat = document.getElementById("modal-source-category");
        const modalContent = document.getElementById("modal-source-content");
        const modalClose = document.getElementById("modal-close-btn");

        if (modalClose && modal) {
            modalClose.addEventListener("click", () => modal.style.display = "none");
            modal.addEventListener("click", (e) => {
                if (e.target === modal) modal.style.display = "none";
            });
        }

        function openSourceModal(source) {
            if (!modal) return;
            if (modalTitle) modalTitle.innerHTML = '<i class="fa-solid fa-file-shield" style="color:#00d4ff;"></i> ' + escapeHtml(source.title);
            if (modalCat) modalCat.textContent = source.category || "Official Campus Document";
            if (modalContent) modalContent.textContent = source.snippet || "Official verified campus record.";
            modal.style.display = "flex";
        }

        // Header user status rendering
        const currentUser = getUserProfile();
        if (userStatusBadge) {
            if (currentUser) {
                const firstName = (currentUser.name || "User").split(" ")[0];
                const yearOrRole = currentUser.role === "student" && currentUser.year_of_study
                    ? currentUser.year_of_study
                    : (currentUser.role ? currentUser.role.toUpperCase() : "STUDENT");

                let avatarHtml = '<i class="fa-solid fa-circle-user"></i>';
                if (currentUser.avatar_url) {
                    const av = currentUser.avatar_url.trim();
                    if (av.startsWith("data:image") || av.startsWith("http")) {
                        avatarHtml = `<img src="${av}" alt="${escapeHtml(currentUser.name || 'User')}" class="header-user-avatar-img" />`;
                    } else {
                        avatarHtml = `<span class="header-user-avatar-emoji">${av}</span>`;
                    }
                } else if (currentUser.name) {
                    avatarHtml = `<span class="header-user-avatar-emoji" style="font-weight:700;font-size:12px;width:20px;height:20px;display:inline-flex;align-items:center;justify-content:center;background:rgba(0,212,255,0.2);border-radius:50%;">${escapeHtml(currentUser.name.charAt(0).toUpperCase())}</span>`;
                }

                userStatusBadge.innerHTML = `
                    ${avatarHtml}
                    <span>${escapeHtml(firstName)} (${escapeHtml(yearOrRole)})</span>
                `;
            } else {
                userStatusBadge.innerHTML = `
                    <a href="../auth/signin.html" style="color:inherit;text-decoration:none;display:inline-flex;align-items:center;gap:6px;">
                        <i class="fa-regular fa-user"></i> Sign In
                    </a>
                `;
            }
        }

        if (!log || !input || !sendBtn) return;

        const pendingAttachments = [];

        // Auto-expand textarea
        function autoResizeTextarea() {
            input.style.height = "auto";
            input.style.height = Math.min(input.scrollHeight, 160) + "px";
        }

        input.addEventListener("input", autoResizeTextarea);

        // Attachment Tray Rendering
        function renderPreviewTray() {
            if (!previewTray) return;
            if (pendingAttachments.length === 0) {
                previewTray.hidden = true;
                previewTray.innerHTML = "";
                return;
            }

            previewTray.hidden = false;
            previewTray.innerHTML = "";

            pendingAttachments.forEach((att, idx) => {
                const chip = document.createElement("div");
                chip.className = "att-preview-chip";

                if (att.type === "image") {
                    chip.innerHTML = `
                        <i class="fa-regular fa-image" style="color:#00d4ff;"></i>
                        <span>${escapeHtml(att.name)}</span>
                        <button type="button" class="att-remove" data-idx="${idx}">&times;</button>
                    `;
                } else {
                    chip.innerHTML = `
                        <i class="fa-solid fa-file-pdf" style="color:#f87171;"></i>
                        <span>${escapeHtml(att.name)}</span>
                        <button type="button" class="att-remove" data-idx="${idx}">&times;</button>
                    `;
                }
                previewTray.appendChild(chip);
            });

            previewTray.querySelectorAll(".att-remove").forEach(b => {
                b.addEventListener("click", function (e) {
                    e.stopPropagation();
                    const index = parseInt(this.getAttribute("data-idx"), 10);
                    if (!isNaN(index)) {
                        pendingAttachments.splice(index, 1);
                        renderPreviewTray();
                    }
                });
            });
        }

        async function processFile(file) {
            if (!file) return;
            if (file.size > 20 * 1024 * 1024) {
                alert(`File "${file.name}" is too large. Maximum size is 20MB.`);
                return;
            }

            const isPdf = file.name.toLowerCase().endsWith(".pdf") || file.type.includes("pdf");
            const isImage = file.type.startsWith("image/");

            if (isImage) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    pendingAttachments.push({
                        type: "image",
                        name: file.name,
                        content: e.target.result
                    });
                    renderPreviewTray();
                };
                reader.readAsDataURL(file);
            } else if (isPdf) {
                const formData = new FormData();
                formData.append("file", file);
                try {
                    const res = await fetch(UPLOAD_ENDPOINT, { method: "POST", body: formData });
                    const data = await res.json();
                    if (res.ok && data.success) {
                        pendingAttachments.push({
                            type: "pdf",
                            name: data.file.name,
                            content: data.file.content,
                            pages: data.file.total_pages
                        });
                        renderPreviewTray();
                    } else {
                        alert(data.error || "Failed to process PDF.");
                    }
                } catch (err) {
                    alert("Error uploading PDF: " + err.message);
                }
            }
        }

        if (attachBtn && fileInput) {
            attachBtn.addEventListener("click", () => fileInput.click());
            fileInput.addEventListener("change", async function () {
                if (this.files && this.files.length > 0) {
                    for (let i = 0; i < this.files.length; i++) {
                        await processFile(this.files[i]);
                    }
                    this.value = "";
                }
            });
        }

        // Drag and drop onto chat
        if (dropZone) {
            dropZone.addEventListener("dragover", (e) => {
                e.preventDefault();
                dropZone.classList.add("drag-over");
            });
            dropZone.addEventListener("dragleave", () => {
                dropZone.classList.remove("drag-over");
            });
            dropZone.addEventListener("drop", async (e) => {
                e.preventDefault();
                dropZone.classList.remove("drag-over");
                if (e.dataTransfer && e.dataTransfer.files) {
                    for (let i = 0; i < e.dataTransfer.files.length; i++) {
                        await processFile(e.dataTransfer.files[i]);
                    }
                }
            });
        }

        // Voice Input (Speech-to-Text) Controller
        let recognition = null;
        let isRecordingVoice = false;
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        function stopVoiceRecording() {
            isRecordingVoice = false;
            if (voiceBtn) {
                voiceBtn.classList.remove("recording");
                voiceBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
                voiceBtn.title = "Voice Input: Speak to ask questions";
            }
            if (input) input.placeholder = "Ask CampusMind anything about your college...";
        }

        if (SpeechRecognition && voiceBtn) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = "en-IN"; // Supports English, Hindi/English mix seamlessly

            recognition.onstart = function () {
                isRecordingVoice = true;
                voiceBtn.classList.add("recording");
                voiceBtn.innerHTML = '<i class="fa-solid fa-microphone-lines"></i>';
                voiceBtn.title = "Listening... Speak your question (Click to stop)";
                input.placeholder = "🎙️ Listening... Speak your question now...";
            };

            recognition.onresult = function (event) {
                let transcript = "";
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                if (transcript) {
                    input.value = transcript;
                    autoResizeTextarea();
                }
            };

            recognition.onerror = function (event) {
                console.warn("Speech recognition event:", event.error);
                stopVoiceRecording();
                if (event.error === "not-allowed") {
                    alert("Microphone access was denied. Please allow microphone permission in your browser to use voice input.");
                }
            };

            recognition.onend = function () {
                stopVoiceRecording();
            };

            voiceBtn.addEventListener("click", () => {
                if (isRecordingVoice) {
                    try { recognition.stop(); } catch (e) {}
                    stopVoiceRecording();
                } else {
                    try {
                        recognition.start();
                    } catch (e) {
                        console.error("Speech start error:", e);
                        try { recognition.stop(); } catch (err) {}
                        stopVoiceRecording();
                    }
                }
            });
        } else if (voiceBtn) {
            voiceBtn.addEventListener("click", () => {
                alert("Voice recognition is not supported in this browser. Please use Chrome, Edge, or a browser with Web Speech API.");
            });
        }

        // Bind Suggestion Prompt Cards
        function bindSuggestionCards() {
            document.querySelectorAll(".suggestion-card").forEach(card => {
                card.addEventListener("click", function () {
                    const prompt = this.getAttribute("data-prompt") || "";
                    if (prompt) {
                        input.value = prompt;
                        send();
                    }
                });
            });
        }
        bindSuggestionCards();

        // Append message to conversation view
        function appendMessage(role, content, attachments, sources) {
            const wrap = document.createElement("div");
            wrap.className = "chat-msg chat-msg-" + (role === "user" ? "user" : "bot");

            const avatar = document.createElement("div");
            avatar.className = "chat-avatar";

            if (role === "user") {
                const user = getUserProfile();
                if (user && user.avatar_url) {
                    const av = user.avatar_url.trim();
                    if (av.startsWith("data:image") || av.startsWith("http")) {
                        avatar.innerHTML = `<img src="${av}" alt="${escapeHtml(user.name || 'User')}" />`;
                    } else {
                        avatar.innerHTML = av;
                    }
                } else if (user && user.name) {
                    avatar.innerHTML = escapeHtml(user.name.charAt(0).toUpperCase());
                } else {
                    avatar.innerHTML = '<i class="fa-solid fa-user"></i>';
                }
            } else {
                avatar.innerHTML = '<i class="fa-solid fa-brain"></i>';
            }

            const bubbleWrapper = document.createElement("div");
            bubbleWrapper.className = "chat-bubble-wrapper";

            const bubble = document.createElement("div");
            bubble.className = "chat-bubble";

            // User Attachments inside message
            if (role === "user" && attachments && attachments.length > 0) {
                const attContainer = document.createElement("div");
                attContainer.className = "chat-msg-attachments";
                attachments.forEach(att => {
                    if (att.type === "image") {
                        const img = document.createElement("img");
                        img.src = att.content;
                        img.className = "bubble-att-img";
                        img.alt = "Attachment";
                        attContainer.appendChild(img);
                    } else {
                        const card = document.createElement("div");
                        card.className = "bubble-att-card";
                        card.innerHTML = `<i class="fa-solid fa-file-pdf"></i> <span>${escapeHtml(att.name)}</span>`;
                        attContainer.appendChild(card);
                    }
                });
                bubble.appendChild(attContainer);
            }

            const textNode = document.createElement("div");
            textNode.innerHTML = renderMarkdownLite(content || "");
            bubble.appendChild(textNode);

            bubbleWrapper.appendChild(bubble);

            // Copy text helper with visual feedback
            function copyMessageToClipboard(textToCopy, btnEl) {
                if (!textToCopy) return;
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(textToCopy).catch(() => fallbackClipboardCopy(textToCopy));
                } else {
                    fallbackClipboardCopy(textToCopy);
                }
                if (btnEl) {
                    const originalHtml = btnEl.innerHTML;
                    btnEl.innerHTML = '<i class="fa-solid fa-check" style="color:#34d399;"></i> <span>Copied!</span>';
                    btnEl.classList.add("active-success");
                    setTimeout(() => {
                        btnEl.innerHTML = originalHtml;
                        btnEl.classList.remove("active-success");
                    }, 1400);
                }
            }

            function fallbackClipboardCopy(text) {
                const ta = document.createElement("textarea");
                ta.value = text;
                ta.style.position = "fixed";
                ta.style.left = "-9999px";
                document.body.appendChild(ta);
                ta.select();
                try { document.execCommand("copy"); } catch (e) {}
                document.body.removeChild(ta);
            }

            // Message Toolbar: Copy, Edit, Resend, Listen, Regenerate
            const toolbar = document.createElement("div");
            toolbar.className = "msg-toolbar";
            toolbar.style.marginTop = "6px";

            if (role === "user") {
                toolbar.style.justifyContent = "flex-end";

                // 1. Copy Button
                const copyBtn = document.createElement("button");
                copyBtn.type = "button";
                copyBtn.className = "msg-action-btn";
                copyBtn.title = "Copy question";
                copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> <span>Copy</span>';
                copyBtn.addEventListener("click", () => copyMessageToClipboard(content, copyBtn));

                // 2. Edit Button (Inline Edit Box)
                const editBtn = document.createElement("button");
                editBtn.type = "button";
                editBtn.className = "msg-action-btn";
                editBtn.title = "Edit and resend question";
                editBtn.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> <span>Edit</span>';
                editBtn.addEventListener("click", () => {
                    if (bubble.querySelector(".msg-inline-edit-box")) return; // already editing
                    const originalHtml = bubble.innerHTML;

                    bubble.innerHTML = `
                        <textarea class="msg-inline-edit-box">${escapeHtml(content || '')}</textarea>
                        <div class="msg-inline-actions">
                            <button type="button" class="msg-cancel-edit-btn">Cancel</button>
                            <button type="button" class="msg-save-resend-btn">
                                <i class="fa-solid fa-paper-plane"></i> Save & Resend
                            </button>
                        </div>
                    `;

                    const textarea = bubble.querySelector(".msg-inline-edit-box");
                    textarea.focus();
                    textarea.setSelectionRange(textarea.value.length, textarea.value.length);

                    // Cancel
                    bubble.querySelector(".msg-cancel-edit-btn")?.addEventListener("click", () => {
                        bubble.innerHTML = originalHtml;
                    });

                    // Save & Resend
                    const doSaveAndResend = () => {
                        const newText = textarea.value.trim();
                        if (newText) {
                            bubble.innerHTML = originalHtml;
                            sendMessageWithText(newText, attachments);
                        }
                    };

                    bubble.querySelector(".msg-save-resend-btn")?.addEventListener("click", doSaveAndResend);
                    textarea.addEventListener("keydown", (e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            doSaveAndResend();
                        }
                    });
                });

                // 3. Resend Button
                const resendBtn = document.createElement("button");
                resendBtn.type = "button";
                resendBtn.className = "msg-action-btn";
                resendBtn.title = "Resend this question";
                resendBtn.innerHTML = '<i class="fa-solid fa-rotate-right"></i> <span>Resend</span>';
                resendBtn.addEventListener("click", () => {
                    sendMessageWithText(content, attachments);
                });

                toolbar.appendChild(copyBtn);
                toolbar.appendChild(editBtn);
                toolbar.appendChild(resendBtn);

                const timeSpan = document.createElement("div");
                timeSpan.className = "chat-msg-time";
                timeSpan.textContent = formatTime();
                timeSpan.style.marginLeft = "4px";
                toolbar.appendChild(timeSpan);

            } else if (role === "bot") {
                toolbar.style.justifyContent = "space-between";

                const leftActions = document.createElement("div");
                leftActions.style.display = "flex";
                leftActions.style.gap = "6px";
                leftActions.style.alignItems = "center";
                leftActions.style.flexWrap = "wrap";

                // 1. Copy Button
                const copyBtn = document.createElement("button");
                copyBtn.type = "button";
                copyBtn.className = "msg-action-btn";
                copyBtn.title = "Copy answer text";
                copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> <span>Copy</span>';
                copyBtn.addEventListener("click", () => copyMessageToClipboard(content, copyBtn));
                leftActions.appendChild(copyBtn);

                // 2. Listen (TTS)
                const speakBtn = document.createElement("button");
                speakBtn.type = "button";
                speakBtn.className = "msg-action-btn msg-speak-btn";
                speakBtn.title = "Read message aloud";
                speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i> <span>Listen</span>';

                speakBtn.addEventListener("click", () => {
                    if (!("speechSynthesis" in window)) {
                        alert("Speech synthesis is not supported in this browser.");
                        return;
                    }

                    if (window.speechSynthesis.speaking) {
                        window.speechSynthesis.cancel();
                        document.querySelectorAll(".msg-speak-btn").forEach(b => {
                            b.classList.remove("speaking");
                            b.innerHTML = '<i class="fa-solid fa-volume-high"></i> <span>Listen</span>';
                        });
                        return;
                    }

                    const plainText = (content || "")
                        .replace(/[*_~`#\[\]\(\)>]/g, " ")
                        .replace(/\s+/g, " ")
                        .trim();

                    const utterance = new SpeechSynthesisUtterance(plainText);
                    utterance.rate = 1.0;
                    utterance.lang = "en-IN";

                    speakBtn.classList.add("speaking");
                    speakBtn.innerHTML = '<i class="fa-solid fa-volume-xmark"></i> <span>Stop</span>';

                    utterance.onend = utterance.onerror = () => {
                        speakBtn.classList.remove("speaking");
                        speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i> <span>Listen</span>';
                    };

                    window.speechSynthesis.speak(utterance);
                });
                leftActions.appendChild(speakBtn);

                // 3. Regenerate Button
                const regenBtn = document.createElement("button");
                regenBtn.type = "button";
                regenBtn.className = "msg-action-btn";
                regenBtn.title = "Regenerate answer";
                regenBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> <span>Regenerate</span>';
                regenBtn.addEventListener("click", () => {
                    for (let i = conversation.length - 1; i >= 0; i--) {
                        if (conversation[i].role === "user") {
                            sendMessageWithText(conversation[i].content);
                            break;
                        }
                    }
                });
                leftActions.appendChild(regenBtn);

                toolbar.appendChild(leftActions);

                const timeSpan = document.createElement("div");
                timeSpan.className = "chat-msg-time";
                timeSpan.textContent = formatTime();
                toolbar.appendChild(timeSpan);
            }

            bubbleWrapper.appendChild(toolbar);

            if (role === "bot") {
                wrap.appendChild(avatar);
                wrap.appendChild(bubbleWrapper);
            } else {
                wrap.appendChild(bubbleWrapper);
                wrap.appendChild(avatar);
            }

            log.appendChild(wrap);
            scrollToBottom();
        }

        function scrollToBottom() {
            const mainArea = document.querySelector(".chat-main-area");
            if (mainArea) {
                mainArea.scrollTop = mainArea.scrollHeight;
            }
        }

        function setSending(sending) {
            sendBtn.disabled = sending;
            input.disabled = sending;
            if (attachBtn) attachBtn.disabled = sending;
            sendBtn.innerHTML = sending
                ? '<i class="fa-solid fa-spinner fa-spin"></i>'
                : '<i class="fa-solid fa-arrow-up"></i>';
        }

        // Send logic with customText & customAtts support
        async function sendMessageWithText(customText, customAtts) {
            const text = (customText !== undefined ? customText : (input.value || "")).trim();
            const currentAtts = customAtts !== undefined ? [...customAtts] : [...pendingAttachments];

            if (!text && currentAtts.length === 0) {
                input.focus();
                return;
            }

            // Remove welcome screen on first message
            const welcome = document.getElementById("chat-welcome-screen");
            if (welcome) welcome.remove();

            appendMessage("user", text || "(Attached files)", currentAtts);

            let userPromptForHistory = text;
            if (currentAtts.length > 0) {
                const fileNames = currentAtts.map(a => a.name).join(", ");
                userPromptForHistory = text ? `[Files: ${fileNames}] ${text}` : `[Attached Files: ${fileNames}]`;
            }
            conversation.push({ role: "user", content: userPromptForHistory });

            if (customText === undefined) {
                input.value = "";
                input.style.height = "auto";
                pendingAttachments.length = 0;
                renderPreviewTray();
            }

            // Typing Indicator
            const typingWrap = document.createElement("div");
            typingWrap.className = "chat-msg chat-msg-bot chat-typing";
            typingWrap.innerHTML = `
                <div class="chat-avatar"><i class="fa-solid fa-brain"></i></div>
                <div class="chat-bubble-wrapper">
                    <div class="chat-bubble chat-typing-bubble">
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                    </div>
                </div>
            `;
            log.appendChild(typingWrap);
            scrollToBottom();

            setSending(true);

            try {
                const data = await sendToBackend(text, currentAtts);
                typingWrap.remove();

                const reply = data.reply || "(no reply)";
                appendMessage("bot", reply, null, data.sources || []);
                conversation.push({ role: "assistant", content: reply });
            } catch (err) {
                typingWrap.remove();
                if (conversation.length > 0 && conversation[conversation.length - 1].role === "user") {
                    conversation.pop();
                }
                appendMessage("bot", "⚠️ " + (err.message || "Something went wrong. Please check if the backend is running."));
            } finally {
                setSending(false);
                input.focus();
            }
        }

        function send() {
            return sendMessageWithText();
        }

        sendBtn.addEventListener("click", send);
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
            }
        });

        // New Chat Button Handler
        if (newChatBtn) {
            newChatBtn.addEventListener("click", function () {
                conversation.length = 0;
                activeSessionId = null;
                pendingAttachments.length = 0;
                renderPreviewTray();
                input.value = "";
                input.style.height = "auto";

                log.innerHTML = `
                    <div class="chat-welcome" id="chat-welcome-screen">
                        <div class="chat-welcome-avatar">
                            <i class="fa-solid fa-brain"></i>
                        </div>
                        <h2>How can I help you today?</h2>
                        <p class="welcome-desc">Ask anything about your syllabus, college rules, exams, or VPCSC Indapur campus resources.</p>
                        
                        <div class="chat-suggestion-grid">
                            <button type="button" class="suggestion-card" data-prompt="What are my enrolled academic subjects and syllabus?">
                                <i class="fa-solid fa-book-open"></i>
                                <div class="suggestion-text">
                                    <strong>My Academic Subjects</strong>
                                    <span>View subjects & syllabus for your current year</span>
                                </div>
                            </button>

                            <button type="button" class="suggestion-card" data-prompt="What is the latest college notice and announcement?">
                                <i class="fa-solid fa-bullhorn"></i>
                                <div class="suggestion-text">
                                    <strong>Latest College Notices</strong>
                                    <span>Check recent circulars & urgent deadlines</span>
                                </div>
                            </button>

                            <button type="button" class="suggestion-card" data-prompt="Tell me about upcoming exam dates, schedules, and rules.">
                                <i class="fa-solid fa-calendar-check"></i>
                                <div class="suggestion-text">
                                    <strong>Upcoming Exams & Rules</strong>
                                    <span>Timetable, room venues & attendance rules</span>
                                </div>
                            </button>

                            <button type="button" class="suggestion-card" data-prompt="Tell me about VPCSC Indapur college, courses, and campus facilities.">
                                <i class="fa-solid fa-building-columns"></i>
                                <div class="suggestion-text">
                                    <strong>VPCSC Indapur Knowledge</strong>
                                    <span>SPPU affiliation, degrees, labs & facilities</span>
                                </div>
                            </button>
                        </div>
                    </div>
                `;
                bindSuggestionCards();
                input.focus();
            });
        }

        // URL Parameter handling (e.g. from Dashboard shortcuts)
        const urlParams = new URLSearchParams(window.location.search);
        const initialPrompt = urlParams.get("prompt");
        if (initialPrompt) {
            input.value = initialPrompt;
            setTimeout(() => send(), 300);
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        initQuickInput();
        initFullChat();
    });
})();
