/* =====================================================
   CAMPUSMIND AI — JARVIS 3D ANIMATED VOICE ASSISTANT
   Three.js + Ready Player Me (.glb) + TalkingHead.js + ElevenLabs TTS
===================================================== */

import { TalkingHead } from "talkinghead";

class VoiceAvatarController {
    constructor() {
        this.head = null;
        this.isInitialized = false;
        this.isLoading = false;
        this.currentState = "idle"; // 'idle' | 'listening' | 'thinking' | 'speaking'
        this.isMuted = false;
        this.wakeWordEnabled = false;
        this.recognition = null;
        this.continuousRecognition = null;
        this.currentAudioSource = null;
        this.wakeWordTimeout = null;

        // UI Element References
        this.container = null;
        this.viewport = null;
        this.statusBadge = null;
        this.statusText = null;
        this.loadingOverlay = null;
        this.progressBar = null;
        this.micButton = null;
        this.wakeWordToggle = null;
        this.subtitlesElem = null;

        // Default Ready Player Me female avatar fallback (jsDelivr CDN)
        this.defaultAvatarUrl = "https://cdn.jsdelivr.net/gh/met4citizen/TalkingHead@main/avatars/brunette.glb";
        this.localAvatarUrl = "/avatars/avatar.glb";

    }


    /**
     * Initialize DOM elements and 3D Avatar viewport
     */
    async init(containerId = "jarvis-avatar-stage") {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.warn("[VoiceAvatar] Container element not found:", containerId);
            return;
        }

        this.viewport = document.getElementById("jarvis-3d-viewport");
        this.statusBadge = document.getElementById("jarvis-status-badge");
        this.statusText = document.getElementById("jarvis-status-text");
        this.loadingOverlay = document.getElementById("jarvis-loading-overlay");
        this.progressBar = document.getElementById("jarvis-loading-progress");
        this.micButton = document.getElementById("jarvis-mic-btn");
        this.wakeWordToggle = document.getElementById("jarvis-wakeword-toggle");
        this.subtitlesElem = document.getElementById("jarvis-subtitles");

        this.bindEvents();
        await this.loadAvatar();
        this.initSpeechRecognition();
    }

    /**
     * Set avatar UI state: idle | listening | thinking | speaking
     */
    setState(state, subtitle = "") {
        this.currentState = state;
        if (!this.container) return;

        // Reset state classes
        this.container.classList.remove("state-idle", "state-listening", "state-thinking", "state-speaking");
        this.container.classList.add(`state-${state}`);

        if (this.statusText) {
            switch (state) {
                case "listening":
                    this.statusText.textContent = "LISTENING...";
                    break;
                case "thinking":
                    this.statusText.textContent = "THINKING...";
                    break;
                case "speaking":
                    this.statusText.textContent = "SPEAKING...";
                    break;
                case "idle":
                default:
                    this.statusText.textContent = this.wakeWordEnabled ? "WAKE-WORD ACTIVE ('Hey Campus')" : "ONLINE / IDLE";
                    break;
            }
        }

        if (this.subtitlesElem) {
            if (subtitle) {
                this.subtitlesElem.textContent = subtitle;
                this.subtitlesElem.style.display = "block";
            } else if (state === "idle") {
                this.subtitlesElem.style.display = "none";
            }
        }

        // TalkingHead subtle posture reactions
        if (this.head) {
            try {
                if (state === "listening") {
                    this.head.lookAtCamera(1000);
                    this.head.setMood("neutral");
                } else if (state === "thinking") {
                    this.head.setMood("neutral");
                } else if (state === "speaking") {
                    this.head.lookAtCamera(500);
                } else if (state === "idle") {
                    this.head.setMood("neutral");
                }
            } catch (e) {
                console.debug("[VoiceAvatar] Mood/Posture update:", e);
            }
        }
    }

    /**
     * Load Ready Player Me Avatar using TalkingHead
     */
    async loadAvatar() {
        if (this.isInitialized || this.isLoading) return;
        this.isLoading = true;

        if (this.loadingOverlay) this.loadingOverlay.style.display = "flex";

        try {
            // Instantiate TalkingHead in the viewport
            this.head = new TalkingHead(this.viewport, {
                ttsEndpoint: null, // Managed via ElevenLabs Flask backend
                lipsyncModules: ["en"],
                cameraView: "upper", // Pura posture dikhe
                avatarMood: "neutral",
                modelPixelRatio: Math.min(window.devicePixelRatio || 1, 2),
                modelFPS: 30,
                cameraRotateEnable: true,
                cameraPanEnable: false,
                cameraZoomEnable: false,
                avatarIdleEyeContact: 0.8,
                avatarIdleHeadMove: 0.6,
                avatarSpeakingEyeContact: 0.9,
                avatarSpeakingHeadMove: 0.7
            });

            // Target local avatar model downloaded into frontend/avatars/avatar.glb
            let targetUrl = this.localAvatarUrl;
            console.log("[VoiceAvatar] Loading avatar model from:", targetUrl);

            try {
                await this.head.showAvatar({
                    url: targetUrl,
                    body: "F",
                    avatarMood: "neutral",
                    lipsyncLang: "en",
                    avatarIdleEyeContact: 0.7,
                    avatarSpeakingEyeContact: 0.8
                }, (ev) => {
                    if (ev.lengthComputable && this.progressBar) {
                        const pct = Math.min(100, Math.round((ev.loaded / ev.total) * 100));
                        this.progressBar.style.width = pct + "%";
                    }
                });
            } catch (loadErr) {
                console.warn("[VoiceAvatar] Local avatar load error, falling back to CDN:", loadErr);
                // Fallback to jsDelivr CDN avatar
                await this.head.showAvatar({
                    url: this.defaultAvatarUrl,
                    body: "F",
                    avatarMood: "neutral",
                    lipsyncLang: "en"
                });
            }

            this.isInitialized = true;
            this.setState("idle");
            if (this.loadingOverlay) this.loadingOverlay.style.display = "none";
            console.log("[VoiceAvatar] 3D Avatar materialized successfully.");


        } catch (error) {
            console.error("[VoiceAvatar] Failed to load 3D Avatar:", error);
            if (this.loadingOverlay) {
                this.loadingOverlay.innerHTML = `
                    <div style="color: #ff5555; text-align: center; padding: 20px;">
                        <i class="fa-solid fa-triangle-exclamation" style="font-size: 28px; margin-bottom: 8px;"></i>
                        <p style="font-size: 13px;">Failed to initialize 3D Avatar.</p>
                        <p style="font-size: 11px; opacity: 0.8;">WebGL or model loading issue.</p>
                    </div>
                `;
            }
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Synthesize speech via Flask ElevenLabs endpoint & Lip-sync avatar
     */
    async speak(text) {
        if (!text || !text.trim()) return;
        if (this.isMuted) return;

        // Ensure 3D avatar is visible and initialized
        if (!this.isInitialized && !this.isLoading) {
            await this.loadAvatar();
        }

        this.setState("thinking", "Preparing voice response...");

        const apiBase = window.CAMPUSMIND_API_BASE || (
            window.location.port && window.location.port !== "5000" && window.location.hostname
                ? window.location.protocol + "//" + window.location.hostname + ":5000"
                : ""
        );

        try {
            const response = await fetch(`${apiBase}/api/voice-assistant/speak`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                console.warn("[VoiceAvatar] TTS synthesis error:", errData);
                this.setState("idle");
                return;
            }

            const data = await response.json();
            if (!data.success || !data.audio_base64) {
                console.warn("[VoiceAvatar] TTS failed:", data.error);
                this.setState("idle");
                return;
            }

            // Convert Base64 string to ArrayBuffer
            const binary = atob(data.audio_base64);
            const bytes = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) {
                bytes[i] = binary.charCodeAt(i);
            }

            // Decode AudioBuffer using TalkingHead's internal AudioContext
            if (!this.head || !this.head.audioCtx) {
                console.error("[VoiceAvatar] AudioContext not available in TalkingHead");
                this.setState("idle");
                return;
            }

            const audioBuffer = await this.head.audioCtx.decodeAudioData(bytes.buffer);

            // Group character alignments into words & timestamps for TalkingHead
            const alignment = data.alignment;
            const words = [];
            const wtimes = [];
            const wdurations = [];

            if (alignment && alignment.characters && alignment.characters.length > 0) {
                let currentWord = "";
                let wordStart = null;
                let lastEnd = 0;

                for (let i = 0; i < alignment.characters.length; i++) {
                    const ch = alignment.characters[i];
                    const startSec = alignment.character_start_times_seconds[i];
                    const endSec = alignment.character_end_times_seconds[i];

                    if (ch === " " || ch === "\n" || ch === "\t" || ch === "." || ch === "," || ch === "!" || ch === "?") {
                        if (currentWord.trim().length > 0 && wordStart !== null) {
                            words.push(currentWord.trim());
                            // Offset by -60ms for natural mouth-lead synchronization
                            wtimes.push(Math.max(0, Math.round(wordStart * 1000 - 60)));
                            wdurations.push(Math.max(80, Math.round((lastEnd - wordStart) * 1000)));
                            currentWord = "";
                            wordStart = null;
                        }
                    } else {
                        if (wordStart === null) wordStart = startSec;
                        currentWord += ch;
                        lastEnd = endSec;
                    }
                }

                if (currentWord.trim().length > 0 && wordStart !== null) {
                    words.push(currentWord.trim());
                    wtimes.push(Math.max(0, Math.round(wordStart * 1000 - 60)));
                    wdurations.push(Math.max(80, Math.round((lastEnd - wordStart) * 1000)));
                }
            }

            const audioObject = {
                audio: audioBuffer,
                words: words,
                wtimes: wtimes,
                wdurations: wdurations
            };

            this.setState("speaking", data.spoken_text || text);

            // Trigger lip-synced speech playback
            await this.head.speakAudio(audioObject);

            this.setState("idle");

        } catch (error) {
            console.error("[VoiceAvatar] Speech pipeline exception:", error);
            this.setState("idle");
        }
    }

    /**
     * Stop current speech & lip animation
     */
    stopSpeaking() {
        if (this.head) {
            try {
                this.head.stopSpeaking();
            } catch (e) {}
        }
        this.setState("idle");
    }

    /**
     * Initialize Speech Recognition & "Hey Campus" Wake-Word Engine
     */
    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn("[VoiceAvatar] Web Speech API not supported in this browser.");
            if (this.wakeWordToggle) {
                this.wakeWordToggle.disabled = true;
                this.wakeWordToggle.title = "Wake-word requires Chrome or Edge browser";
            }
            return;
        }

        // 1. Direct Voice Input Recognition
        this.recognition = new SpeechRecognition();
        this.recognition.lang = "en-IN";
        this.recognition.interimResults = true;
        this.recognition.continuous = false;

        this.recognition.onstart = () => {
            this.setState("listening", "Listening... Ask your question!");
            if (this.micButton) this.micButton.classList.add("active");
        };

        this.recognition.onresult = (event) => {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            if (this.subtitlesElem) {
                this.subtitlesElem.textContent = transcript;
                this.subtitlesElem.style.display = "block";
            }
            const chatInput = document.getElementById("chat-input");
            if (chatInput) {
                chatInput.value = transcript;
            }
        };

        this.recognition.onerror = (e) => {
            console.warn("[VoiceAvatar] Direct mic recognition error:", e.error);
            if (this.micButton) this.micButton.classList.remove("active");
            this.setState("idle");
        };

        this.recognition.onend = () => {
            if (this.micButton) this.micButton.classList.remove("active");
            const chatInput = document.getElementById("chat-input");
            const sendBtn = document.getElementById("chat-send");
            if (chatInput && chatInput.value.trim() && sendBtn) {
                this.setState("thinking", "Processing your question...");
                sendBtn.click();
            } else {
                this.setState("idle");
            }
        };

        // 2. Continuous Wake-word Recognition ("Hey Campus")
        this.continuousRecognition = new SpeechRecognition();
        this.continuousRecognition.lang = "en-IN";
        this.continuousRecognition.continuous = true;
        this.continuousRecognition.interimResults = true;

        this.continuousRecognition.onresult = (event) => {
            if (this.currentState === "speaking" || this.currentState === "thinking") {
                return; // Do not interrupt during speech
            }

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript.toLowerCase();
                if (transcript.includes("hey campus") || transcript.includes("a campus") || transcript.includes("campus mind")) {
                    console.log("[VoiceAvatar] Wake-word detected!");
                    this.stopWakeWordListener();
                    this.triggerDirectMic();
                    break;
                }
            }
        };

        this.continuousRecognition.onend = () => {
            if (this.wakeWordEnabled && this.currentState === "idle") {
                try {
                    this.continuousRecognition.start();
                } catch (e) {}
            }
        };

        this.continuousRecognition.onerror = (e) => {
            if (e.error !== "no-speech") {
                console.debug("[VoiceAvatar] Wake-word listener note:", e.error);
            }
        };
    }

    startWakeWordListener() {
        if (!this.continuousRecognition) return;
        this.wakeWordEnabled = true;
        try {
            this.continuousRecognition.start();
            this.setState("idle");
            console.log("[VoiceAvatar] Wake-word continuous listening started.");
        } catch (e) {}
    }

    stopWakeWordListener() {
        this.wakeWordEnabled = false;
        if (!this.continuousRecognition) return;
        try {
            this.continuousRecognition.stop();
            console.log("[VoiceAvatar] Wake-word continuous listening stopped.");
        } catch (e) {}
    }

    triggerDirectMic() {
        if (!this.recognition) return;
        try {
            this.recognition.start();
        } catch (e) {
            console.debug("[VoiceAvatar] Mic start note:", e);
        }
    }

    /**
     * Enter ChatGPT-Style Fullscreen Voice Assistant Mode
     */
    enterFullscreen() {
        if (!this.container) return;
        this.container.classList.remove("jarvis-hidden");
        this.container.classList.add("jarvis-fullscreen-mode");

        const toggleBtn = document.getElementById("header-jarvis-toggle");
        if (toggleBtn) toggleBtn.classList.add("active");

        if (!this.isInitialized && !this.isLoading) {
            this.loadAvatar();
        }

        // Trigger Three.js resize event after DOM reflow
        setTimeout(() => {
            window.dispatchEvent(new Event("resize"));
        }, 80);
        setTimeout(() => {
            window.dispatchEvent(new Event("resize"));
        }, 300);
    }

    /**
     * Exit Fullscreen Mode back to standard chat
     */
    exitFullscreen() {
        if (!this.container) return;
        this.container.classList.remove("jarvis-fullscreen-mode");

        // Trigger Three.js resize event
        setTimeout(() => {
            window.dispatchEvent(new Event("resize"));
        }, 80);
    }

    /**
     * Toggle Fullscreen Voice Mode
     */
    toggleFullscreen() {
        if (!this.container) return;
        if (this.container.classList.contains("jarvis-fullscreen-mode")) {
            this.exitFullscreen();
        } else {
            this.enterFullscreen();
        }
    }

    /**
     * UI Event bindings
     */
    bindEvents() {

        // Direct Microphone Button on Avatar HUD
        if (this.micButton) {
            this.micButton.addEventListener("click", () => {
                if (this.currentState === "listening") {
                    try { this.recognition.stop(); } catch (e) {}
                } else {
                    this.triggerDirectMic();
                }
            });
        }

        // Wake Word Toggle
        if (this.wakeWordToggle) {
            this.wakeWordToggle.addEventListener("change", (e) => {
                if (e.target.checked) {
                    this.startWakeWordListener();
                } else {
                    this.stopWakeWordListener();
                    this.setState("idle");
                }
            });
        }

        // Fullscreen Mode Controls (ChatGPT Voice Assistant Style)
        const expandBtn = document.getElementById("jarvis-expand-btn");
        if (expandBtn) {
            expandBtn.addEventListener("click", () => this.toggleFullscreen());
        }

        const exitFullscreenBtn = document.getElementById("jarvis-exit-fullscreen-btn");
        if (exitFullscreenBtn) {
            exitFullscreenBtn.addEventListener("click", () => this.exitFullscreen());
        }

        // Bottom Input Bar ChatGPT-Style Voice Avatar Launcher Button
        const chatAvatarModeBtn = document.getElementById("chat-avatar-mode-btn");
        if (chatAvatarModeBtn) {
            chatAvatarModeBtn.addEventListener("click", () => this.enterFullscreen());
        }

        // Close / Minimize Avatar Stage
        const closeBtn = document.getElementById("jarvis-close-btn");
        if (closeBtn && this.container) {
            closeBtn.addEventListener("click", () => {
                this.container.classList.add("jarvis-hidden");
                this.exitFullscreen();
                const toggleBtn = document.getElementById("header-jarvis-toggle");
                if (toggleBtn) toggleBtn.classList.remove("active");
                this.stopSpeaking();
                this.stopWakeWordListener();
            });
        }


        // Camera View Switcher (Head / Upper body)
        const cameraBtn = document.getElementById("jarvis-camera-btn");
        if (cameraBtn) {
            let isHeadView = true;
            cameraBtn.addEventListener("click", () => {
                if (!this.head) return;
                isHeadView = !isHeadView;
                this.head.setView(isHeadView ? "head" : "upper");
                cameraBtn.title = isHeadView ? "Switch to Upper View" : "Switch to Head View";
            });
        }

        // Mute / Unmute Button
        const muteBtn = document.getElementById("jarvis-mute-btn");
        if (muteBtn) {
            muteBtn.addEventListener("click", () => {
                this.isMuted = !this.isMuted;
                muteBtn.innerHTML = this.isMuted
                    ? '<i class="fa-solid fa-volume-xmark"></i>'
                    : '<i class="fa-solid fa-volume-high"></i>';
                muteBtn.classList.toggle("muted", this.isMuted);
                if (this.isMuted) this.stopSpeaking();
            });
        }

        // Pause 3D animation when tab is inactive to conserve battery & GPU
        document.addEventListener("visibilitychange", () => {
            if (!this.head) return;
            if (document.visibilityState === "visible") {
                this.head.start();
            } else {
                this.head.stop();
            }
        });
    }
}

// Global Singleton Instance
window.CampusMindVoiceAvatar = new VoiceAvatarController();

// Auto-initialize when DOM is ready if container exists
document.addEventListener("DOMContentLoaded", () => {
    window.CampusMindVoiceAvatar.init();
});

export { VoiceAvatarController };