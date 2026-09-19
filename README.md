# 🎓 CampusMind AI — Intelligent Academic Companion & Campus Portal

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask%20%7C%20Gunicorn-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Protected%20Env%20%26%20JWT-red.svg)](#security--privacy)

**CampusMind AI** is an end-to-end intelligent academic cockpit and mentor designed for higher education institutions, with deep curriculum grounding for **Vidya Pratishthan's Commerce and Science College, Indapur (VPCSC Indapur)** affiliated with **Savitribai Phule Pune University (SPPU)**.

---

## 🌟 Key Features

### 1. 🤖 Context-Aware Campus AI Chatbot
- Multi-persona intelligence tailored for **Students**, **Faculty**, **Alumni**, **Administrators**, and **Guests**.
- Grounded in official VPCSC Indapur syllabus, faculty directories, credit systems, and administrative counter guides.
- Multimodal support: Upload notes, PDF syllabus, or diagrams directly into the chat for contextual reasoning.
- High-availability cascade: OpenRouter models (NVIDIA Nemotron, Gemma 4, DeepSeek) + deterministic offline RAG fallback.

### 2. 📊 Automated Attendance Management (HOD & Student Portal)
- **HOD Bulk Sheet Upload**: Department HODs can drag-and-drop attendance CSV sheets to automatically ingest, calculate percentages, and assign SPPU compliance statuses.
- **SPPU 75% Rule Compliance**:
  - `≥ 75%`: **Good** (Eligible for university examination hall tickets)
  - `60% - 74.9%`: **Average** (Warning: Below 75% mandate)
  - `< 60%`: **Critical** (Defaulter alert)
- **Zero-Flicker Student Cockpit**: Students see live attendance statistics and lecture breakdowns only after official HOD verification; otherwise, a clean status banner indicates sheet verification is in progress.
- **Chatbot Attendance Inquiry**: Students can ask *"What is my attendance?"* or *"Meri attendance kitni hai?"* to receive certified lecture counts and eligibility breakdowns.

### 3. 🏫 Academic Management & Cockpit
- Dynamic subject and syllabus breakdown by Year & Department (BCS, BBA-CA, Plain B.Sc, B.Com, BBA, M.Sc).
- Upcoming university exam schedules, seat numbers, and venue tracking.
- Real-time departmental notice board and upcoming campus event registrations.

### 4. 🔒 Enterprise Security & RBAC
- Cryptographically signed JWT tokens with role-based access control.
- Passwords hashed using industry-standard `pbkdf2:sha256`.
- Zero credentials or API keys exposed in version control (`.env` strictly excluded).

### 5. ✨ JARVIS-Style 3D Animated Female Voice Assistant
- **Ready Player Me 3D Avatar**: Fully rigged female 3D avatar (.glb) rendered via Three.js.
- **Real-Time Lip-Sync**: Powered by `TalkingHead.js` with viseme blendshape morphing.
- **Natural Expressive TTS**: Integrates ElevenLabs neural voice synthesis with millisecond-accurate word/character alignment timestamps.
- **"Hey Campus" Wake-Word Engine**: Continuous hands-free listening using Web Speech API.
- **Interactive UI States**: Dynamic visual states for `Idle`, `Listening`, `Thinking`, and `Speaking`.

---


## 🛠️ Tech Stack

- **Frontend**: HTML5, Modern CSS (Glassmorphism, responsive grid), Vanilla JavaScript (Modular ES6+).
- **Backend**: Python 3, Flask, Gunicorn, RESTful API architecture.
- **Database**: SQLite with WAL mode (zero-configuration local & cloud) + optional MySQL / Supabase connector.
- **AI / LLM**: OpenRouter API (NVIDIA Nemotron 3.5 Lightning, Gemma 4, DeepSeek) + Vector-like TF-IDF RAG.

---

## 🚀 Quick Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/Dhanaji005/CampusMind-AI-chatboat.git
cd CampusMind-AI-chatboat
```

### 2. Set up Environment Variables
```bash
# Copy template to .env
cp .env.example bakend/.env
```
Open `bakend/.env` and configure your API keys:
```env
# 1. OpenRouter (LLM Reasoning)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
SECRET_KEY=your-random-secret-key

# 2. ElevenLabs (JARVIS 3D Voice Assistant)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=Xb7hH8MSUJpSbSDYk0k2
ELEVENLABS_MODEL_ID=eleven_flash_v2_5
```

> **Testing ElevenLabs Setup:**
> Run the diagnostic tool to verify your voice synthesis and remaining free character balance:
> ```bash
> python bakend/test_elevenlabs.py
> ```

### 👤 Custom 3D Avatar (Ready Player Me)
1. Create a custom female 3D avatar on [readyplayer.me](https://readyplayer.me).
2. Download or export it as a `.glb` file.
3. Save it to: `frontend/avatars/avatar.glb`.
*(If no custom file is provided, CampusMind AI automatically loads an official Ready Player Me female avatar from the official CDN!)*


### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
# Windows
run.bat

# Linux / macOS
chmod +x run.sh
./run.sh

# Or directly with Python
cd bakend
python app.py
```
Open your browser at `http://127.0.0.1:5000` to access CampusMind AI.

---

## 🌐 100% Free Cloud Deployment (Render.com)

1. Fork or push this repository to your GitHub account.
2. Sign up at [Render.com](https://render.com) (100% Free, no credit card required).
3. Create a **New Web Service** and link your repository.
4. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --chdir bakend app:app --bind 0.0.0.0:$PORT`
5. In **Environment Variables**, add:
   - `OPENROUTER_API_KEY`: Your OpenRouter key
   - `JWT_SECRET`: Random secret key
   - `FLASK_ENV`: `production`
6. Click **Deploy Web Service** to receive your free public HTTPS URL!

*(See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full step-by-step instructions).*

---

## 🔒 Security & Privacy

- All sensitive keys, passwords, database binaries (`.db`), and user uploads are strictly excluded via `.gitignore`.
- Always set your production `SECRET_KEY` and `OPENROUTER_API_KEY` through deployment platform environment variables.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
