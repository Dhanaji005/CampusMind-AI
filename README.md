# 🎓 CampusMind AI — Intelligent Autonomous Campus Operating System & 3D Academic Companion

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge&logo=target)](https://github.com/Dhanaji005/CampusMind-AI-chatboat)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask Backend](https://img.shields.io/badge/Backend-Flask%20%7C%20REST%20API-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Three.js & 3D WebGL](https://img.shields.io/badge/3D%20Graphics-Three.js%20%7C%20Ready%20Player%20Me-049EF4?style=for-the-badge&logo=threedotjs&logoColor=white)](https://threejs.org/)
[![ElevenLabs TTS](https://img.shields.io/badge/Voice%20AI-ElevenLabs%20Neural%20TTS-FF6B6B?style=for-the-badge&logo=soundcharts&logoColor=white)](https://elevenlabs.io/)
[![SPPU Compliance](https://img.shields.io/badge/Compliance-SPPU%2075%25%20Mandate-orange?style=for-the-badge)](http://www.unipune.ac.in/)
[![Database](https://img.shields.io/badge/Database-SQLite%20(WAL)%20%7C%20Supabase-4169E1?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 📌 Executive Summary

**CampusMind AI** is an end-to-end, multi-tier autonomous campus operating system and academic mentor engineered specifically for higher education institutions. Built and deeply grounded for **Vidya Pratishthan's Commerce and Science College, Indapur (VPCSC Indapur)** under **Savitribai Phule Pune University (SPPU)**, the platform replaces fragmented university counter systems, manual attendance calculation, and generic search engines with an integrated, intelligent, and interactive AI-driven ecosystem.

Featuring a **JARVIS-Style 3D Animated Female Voice Assistant** with millisecond-accurate viseme lip-sync, an **Automated HOD Attendance Processing Engine** enforcing the SPPU 75% rule, and **Deterministic Institutional RAG (Retrieval-Augmented Generation)**, CampusMind AI bridges the communication and operational gap between Students, Faculty, Department HODs, Administrators, and College Leadership.

---

## 📑 Table of Contents

1. [🌟 Flagship Innovations & Features](#-flagship-innovations--features)
2. [🏛️ Institutional Grounding (VPCSC Indapur & SPPU)](#-institutional-grounding-vpcsc-indapur--sppu)
3. [🏗️ System Architecture & Data Pipeline](#️-system-architecture--data-pipeline)
4. [👥 Demo Credentials (Instant Judge Access)](#-demo-credentials-instant-judge-access)
5. [🖥️ Role-Based Portals Deep Dive](#️-role-based-portals-deep-dive)
6. [✨ JARVIS 3D Voice Assistant Architecture](#-jarvis-3d-voice-assistant-architecture)
7. [📊 Automated Attendance & SPPU 75% Rule Engine](#-automated-attendance--sppu-75-rule-engine)
8. [🛠️ Tech Stack](#️-tech-stack)
9. [🚀 Quickstart & Local Setup](#-quickstart--local-setup)
10. [🧪 Automated Diagnostics & Verification](#-automated-diagnostics--verification)
11. [🌐 100% Free Cloud Deployment Guide](#-100-free-cloud-deployment-guide)
12. [📂 Project Structure](#-project-structure)
13. [🔒 Security & Privacy Architecture](#-security--privacy-architecture)
14. [👥 Project Team & Affiliation](#-project-team--affiliation)

---

## 🌟 Flagship Innovations & Features

### 1. 🤖 Context-Aware Campus RAG AI Chatbot
- **Deterministic Grounding**: Zero hallucinations regarding college-specific inquiries (HOD names, counter procedures, university exam schedules, semester syllabus).
- **High-Availability AI Cascade**: Primary queries routed via OpenRouter (NVIDIA Nemotron 3.5, Gemma 4, DeepSeek) with immediate offline fallback to high-precision TF-IDF vector matching.
- **Multimodal Document & Diagram Analysis**: Students and professors can upload notes, question papers, handwritten sheets, or PDF syllabus directly into the chat for instant synthesis.
- **Multi-Turn Session Persistence**: Memory-augmented conversation history with persona adaptation based on authenticated user role.

### 2. 🎙️ 3D JARVIS-Style Animated Voice Assistant
- **Three.js & Ready Player Me**: Full 3D rigged female avatar rendered directly in WebGL within the browser.
- **Viseme-Based Lip-Sync**: Powered by `TalkingHead.js` with real-time morph target blendshapes synchronized to spoken audio phonemes.
- **ElevenLabs Neural Voice Engine**: Expressive, natural human speech synthesis with character-level alignment timestamps.
- **"Hey Campus" Hands-Free Wake Word**: Continuous browser-level voice activation using Web Speech API with dynamic audio state visualizers (`Idle`, `Listening`, `Thinking`, `Speaking`).

### 3. 📊 Automated Attendance Engine & SPPU 75% Compliance
- **HOD 1-Click CSV Ingestion**: Drag-and-drop attendance sheets for instant automatic percentage calculation and defaulter categorization across classes.
- **SPPU Mandate Categorization**:
  - `≥ 75%`: **Good** (Eligible for university examination hall ticket)
  - `60% - 74.9%`: **Average** (Warning: At risk of defaulter list)
  - `< 60%`: **Critical Defaulter** (Mandatory guardian notification & exam hold)
- **Conversational Attendance Query**: Students can query the AI in natural language (*"What is my attendance?"* or *"Meri attendance kitni hai?"*) to receive certified lecture counts and eligibility breakdowns.

### 4. 🏛️ Complete Role-Based Access Control (RBAC)
- Dedicated interfaces for **Students**, **Faculty**, **Department HODs**, **Principal**, **System Administrators**, and **Guests**.
- Cryptographically signed **JWT tokens** with role validation and password hashing via industry-standard `pbkdf2:sha256`.

---

## 🏛️ Institutional Grounding (VPCSC Indapur & SPPU)

CampusMind AI is deeply grounded with the official curriculum, staff directories, and operational counter manuals of **Vidya Pratishthan's Commerce and Science College, Indapur**:

- **Departments Covered**:
  - BBA(CA) — Bachelor of Business Administration (Computer Applications)
  - BCS / B.Sc (Computer Science)
  - Plain B.Sc (Physics, Chemistry, Mathematics, Botany, Zoology)
  - B.Com (Commerce & Accountancy)
  - BBA (General Business Administration)
  - M.Sc (Postgraduate Computer Science)
- **Administrative Counter Manual (Single-Window System)**:
  - **Window 1 (Admission & Eligibility)**: Handled by Mr. Waghmare
  - **Window 2 (Scholarship & MahaDBT)**: Handled by Mr. Pandit
  - **Window 3 (Bonafide & Attestation)**: Handled by Mr. Kadam
  - **Window 4 (University Exam & Hall Tickets)**: Handled by Exam Cell
  - **Window 5 (Transfer Certificate & Migration)**: Handled by Student Section
- **Leadership & Faculty Integration**:
  - College Principal: **Dr. Lalasaheb Kashid**
  - HOD BBA(CA): **Prof. Nilesh Kaldate**
  - HOD BCS: **Prof. Shaikh Sarfaraz Yusuf**
  - HOD B.Com: **Prof. Bhosale S. D.**
  - HOD BBA: **Prof. Bhong S. N.**
  - HOD B.Sc: **Prof. Shaikh M. D.**

---

## 🏗️ System Architecture & Data Pipeline

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT TIER                                       |
|  HTML5 / CSS3 Glassmorphism UI  |  Three.js 3D WebGL Canvas  |  Web Speech API    |
+------------------------------------------+----------------------------------------+
                                           | HTTP REST / JSON / JWT
                                           v
+-----------------------------------------------------------------------------------+
|                             API GATEWAY & MIDDLEWARE                              |
|   Flask Application Router  |  JWT Role-Based Access (RBAC)  |  CORS Middleware   |
+----+-------------------------------------+------------------------------------+---+
     |                                     |                                    |
     v                                     v                                    v
+--------------------+   +------------------------------------+   +-----------------+
| AUTH & USER MGMT   |   |        CAMPUS RAG AI ENGINE        |   | ATTENDANCE &    |
| - JWT Generation   |   | - OpenRouter LLM Router            |   | ACADEMICS       |
| - Role Validation  |   | - TF-IDF Vector Semantic Retriever |   | - CSV Ingestion |
| - Password Hashing |   | - Multi-Modal Vision Parser (PDF)  |   | - SPPU 75% Rule |
| - Profile State    |   | - Grounded VPCSC Knowledge Base    |   | - Defaulter Log |
+--------------------+   +------------------------------------+   +-----------------+
                                           |
                                           v
                         +------------------------------------+
                         |     3D VOICE SYNTHESIS ENGINE      |
                         | - ElevenLabs Neural Voice API      |
                         | - TalkingHead Viseme Alignment     |
                         | - Phoneme Timestamp Extraction     |
                         +------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                                  STORAGE TIER                                     |
|   SQLite with WAL Mode (Zero-Config High Concurrency) + Supabase Cloud PostgreSQL |
+-----------------------------------------------------------------------------------+
```

---

## 👥 Demo Credentials (Instant Judge Access)

For evaluators, judges, and testing, the following accounts are pre-seeded into the system:

| Role | Name | Email | Password | Access Highlights |
| :--- | :--- | :--- | :--- | :--- |
| **Principal** | Dr. Lalasaheb Kashid | `principal@vpcscindapur.org` | `Principal@123` | Institutional overview, college circulars, department analytics |
| **HOD BBA(CA)** | Prof. Nilesh Kaldate | `hod_bbaca@vpcscindapur.org` | `Hod@123` | BBA(CA) attendance upload, defaulter lists, department timetable |
| **HOD BCS** | Prof. Shaikh Sarfaraz | `hod_bcs@vpcscindapur.org` | `Hod@123` | BCS attendance management, syllabus, departmental circulars |
| **System Admin** | Admin Director | `admin@campusmind.ai` | `Admin@123` | Document RAG knowledge base ingestion, user management |
| **Student (3rd Yr)** | Priya Patel | `thirdyear@campusmind.ai` | `Student@123` | Real-time attendance, SPPU hall ticket eligibility, syllabus |
| **Student (1st Yr)** | Aarav Sharma | `firstyear@campusmind.ai` | `Student@123` | First-year NEP credits, subject guide, exam schedule |
| **Faculty Member** | Dr. Rajesh Verma | `faculty@campusmind.ai` | `Faculty@123` | Academic syllabus review, student academic records |
| **Alumni Member** | Neha Deshmukh | `alumni@campusmind.ai` | `Alumni@123` | Alumni directory, campus mentorship network |

---

## 🖥️ Role-Based Portals Deep Dive

### 1. 🎓 Student Cockpit (`/pages/student-dashboard.html`)
- **Verified Attendance Card**: Displays overall attendance percentage with visual color-coded badges (`Good`, `Average`, `Critical Defaulter`).
- **Subject-Wise Lecture Breakdown**: Shows conducted vs attended lectures per subject.
- **Syllabus & Timetable Explorer**: Dynamic syllabus viewer by department and semester with credit breakdowns.
- **Examination Tracker**: Seat number, examination dates, hall ticket verification status.

### 2. 👔 Department HOD Cockpit (`/pages/hod-dashboard.html`)
- **Bulk CSV Upload Engine**: Ingest raw attendance sheets with one click.
- **Defaulter Analytics**: Automatically filters students with `< 75%` and `< 60%` attendance.
- **Notice & Circular Manager**: Publish notices specific to department cohorts.
- **Timetable Management**: Manage weekly lecture slots and classroom assignments.

### 3. 🏛️ Principal Master Dashboard (`/pages/principal-dashboard.html`)
- **Institution-Wide Metrics**: Real-time roll counts, total faculty, and departmental performance across all 6 streams.
- **College Circulars Broadcast**: Issue official orders and notices college-wide.
- **Department Comparison Matrix**: Comparative attendance and performance charts.

### 4. 🛠️ Admin Knowledge Portal (`/pages/admin-dashboard.html`)
- **RAG Knowledge Base Uploader**: Upload new institutional guidelines, PDF rulebooks, or circulars to immediately ground the AI.
- **Student & Faculty Registry**: Add, edit, or verify campus user accounts.

---

## ✨ JARVIS 3D Voice Assistant Architecture

```
User Voice Input ("Hey Campus, what is my attendance?")
                       │
                       ▼ Web Speech API SpeechRecognition
                  Text Prompt
                       │
                       ▼ POST /api/chatbot/chat
          CampusMind AI RAG Pipeline
                       │
                       ▼ Generated Answer
                       │
                       ▼ POST /api/voice/synthesize
        ElevenLabs Neural TTS (Model: Flash v2.5)
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
Audio Stream (MP3)         Phoneme / Viseme Timestamps
       │                               │
       └───────────────┬───────────────┘
                       ▼
           TalkingHead.js Runtime
  (Maps visemes to blendshapes in real-time)
                       │
                       ▼ Three.js WebGL Renderer
3D Female Avatar Lip-Sync Animation (Zero Desynchronization!)
```

- **Blendshape Compatibility**: Built for Ready Player Me ARKit morph targets (`jawOpen`, `mouthSmile`, `mouthFunnel`, `viseme_aa`, `viseme_E`, etc.).
- **Automatic Fallback**: If local `.glb` is absent, the engine falls back to high-resolution cloud avatars seamlessly.

---

## 📊 Automated Attendance & SPPU 75% Rule Engine

The Attendance Module implements Savitribai Phule Pune University's strict Ordinance 0.60 regarding student eligibility for semester examinations:

$$\text{Attendance Percentage} = \left( \frac{\text{Attended Lectures}}{\text{Conducted Lectures}} \right) \times 100$$

| Percentage Range | SPPU Status | UI Badge | Examination Eligibility |
| :--- | :--- | :--- | :--- |
| **$\ge$ 75.0%** | **Good** | Green | ✅ Eligible for Hall Ticket |
| **60.0% – 74.9%** | **Average** | Yellow | ⚠️ Warning Notice / Make-up assignments required |
| **$<$ 60.0%** | **Critical** | Red | ❌ Defaulter / Exam Hall Ticket Withheld |

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend UI** | HTML5, CSS3 Glassmorphism, Modern Vanilla JavaScript (ES6+ Modules) |
| **3D & Animation** | Three.js (r180), TalkingHead.js, Ready Player Me Rigged 3D Avatars (`.glb`) |
| **Voice & Speech** | ElevenLabs Flash v2.5 Neural Voice API, Web Speech API (Recognition & Synthesis) |
| **Backend API** | Python 3.10+, Flask, Gunicorn, RESTful Blueprint Architecture |
| **AI / LLM Engine** | OpenRouter API (NVIDIA Nemotron 3.5, Gemma 4, DeepSeek) + Custom RAG Retriever |
| **Security & RBAC** | PyJWT (JSON Web Tokens), PBKDF2:SHA256 Password Hashing, CORS Protection |
| **Database** | SQLite (WAL Mode for high concurrency) + Supabase Cloud PostgreSQL connector |
| **Deployment** | Render.com Web Services, Koyeb, Vercel Edge, Gunicorn Production Server |

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.10 or higher installed ([Download Python](https://www.python.org/))
- Git installed ([Download Git](https://git-scm.com/))
- Modern browser (Google Chrome or Microsoft Edge recommended for Web Speech API)

### 1. Clone the Repository
```bash
git clone https://github.com/Dhanaji005/CampusMind-AI-chatboat.git
cd CampusMind-AI-chatboat
```

### 2. Configure Environment Variables
```bash
# Copy the environment template
copy .env.example bakend\.env    # Windows
cp .env.example bakend/.env      # Linux / macOS
```
Edit `bakend/.env` with your API keys:
```env
# AI Reasoning (Get free key from https://openrouter.ai/keys)
OPENROUTER_API_KEY=sk-or-v1-your-key-here
SECRET_KEY=your-random-secret-key

# Voice Assistant (Get free key from https://elevenlabs.io)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=Xb7hH8MSUJpSbSDYk0k2
ELEVENLABS_MODEL_ID=eleven_flash_v2_5
```

### 3. Launch Application (1-Click)

#### On Windows:
Double-click `run.bat` or run:
```cmd
run.bat
```

#### On Linux / macOS:
```bash
chmod +x run.sh
./run.sh
```

#### Or Run Directly with Python:
```bash
pip install -r requirements.txt
cd bakend
python app.py
```

Open your browser and navigate to:
- **Landing Page**: `http://127.0.0.1:5000`
- **AI Chatbot & 3D Assistant**: `http://127.0.0.1:5000/pages/chat.html`
- **Student Dashboard**: `http://127.0.0.1:5000/pages/student-dashboard.html`
- **HOD Cockpit**: `http://127.0.0.1:5000/pages/hod-dashboard.html`
- **Principal Dashboard**: `http://127.0.0.1:5000/pages/principal-dashboard.html`
- **Admin Portal**: `http://127.0.0.1:5000/pages/admin-dashboard.html`

---

## 🧪 Automated Diagnostics & Verification

CampusMind AI includes automated validation test suites to verify system integrity before live presentations:

### 1. Full System Health & Chatbot Validation
```bash
python bakend/run_test.py
```
*Validates API health, status endpoints, student dashboards, notice boards, admin documents, multi-turn chat memory, and grounded college queries.*

### 2. ElevenLabs TTS & Viseme Lip-Sync Diagnostic
```bash
python bakend/test_elevenlabs.py
```
*Verifies ElevenLabs API key validity, subscription character balance, voice ID binding, and timing marker viseme generation.*

---

## 🌐 100% Free Cloud Deployment Guide

CampusMind AI is engineered to deploy **100% Free** on [Render.com](https://render.com) with **zero credit card required**:

1. Fork or push this repository to your GitHub account.
2. Sign up at [Render.com](https://render.com) and click **New + > Web Service**.
3. Link this repository.
4. Set the following build and run parameters:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --chdir bakend app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free ($0/mo)
5. Add Environment Variables:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - `ELEVENLABS_API_KEY`: Your ElevenLabs key
   - `SECRET_KEY`: A random secure string
   - `FLASK_ENV`: `production`
6. Click **Deploy Web Service** to obtain your public production HTTPS URL!

*(See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full step-by-step instructions).*

---

## 📂 Project Structure

```
CampusMind-AI-chatboat/
├── .env.example                    # Global environment configuration template
├── .gitignore                      # Strict privacy & security exclusions
├── DEPLOYMENT_GUIDE.md             # Free cloud deployment handbook
├── Procfile                        # Cloud server process configuration
├── README.md                       # Master documentation & presentation guide
├── requirements.txt                # Unified root Python dependencies
├── run.bat                         # 1-Click Windows development launcher
├── run.sh                          # 1-Click Linux/macOS launcher
├── sync_github.bat                 # 1-Click GitHub push & sync tool
├── auto_git_sync.py                # Automated real-time Git sync engine
│
├── bakend/                         # Core Flask REST Backend & AI Services
│   ├── .env.example                # Backend environment template
│   ├── app.py                      # Flask Application Entrypoint & Static Router
│   ├── database.py                 # SQLite WAL Engine & Supabase Connector
│   ├── requirements.txt            # Backend Python dependencies
│   ├── run_test.py                 # Automated system validation test suite
│   ├── seed_vpcsc_data.py          # VPCSC Indapur curricula & counter seeder
│   ├── test_elevenlabs.py          # ElevenLabs TTS & viseme diagnostic script
│   ├── supabase_schema.sql         # Cloud PostgreSQL schema
│   ├── supabase_security_fix.sql   # Supabase RLS security resolution script
│   │
│   ├── config/
│   │   └── config.py               # Centralized configuration & environment loader
│   ├── middleware/
│   │   └── auth_middleware.py      # JWT authentication & RBAC decorators
│   ├── routes/
│   │   ├── admin_routes.py         # Admin document ingestion & user management
│   │   ├── attendance_routes.py    # Attendance CSV upload & SPPU calculations
│   │   ├── auth_routes.py          # Signin, signup, profile & JWT issuance
│   │   ├── chatbot_routes.py       # AI chat sessions, file parsing & RAG router
│   │   ├── hod_routes.py           # HOD dashboard, timetables & circulars
│   │   ├── principal_routes.py     # Principal master dashboard & college notices
│   │   ├── student_routes.py       # Student dashboard, syllabus & notices
│   │   └── voice_assistant_routes.py # ElevenLabs TTS & viseme synthesis API
│   └── services/
│       ├── academic_service.py     # Subjects, syllabus & credit systems
│       ├── embedding_service.py    # Text chunking & vector indexing
│       ├── file_service.py         # PDF text extraction & image processing
│       ├── openrouter_service.py   # Multi-model LLM router & prompt formatting
│       ├── rag_service.py          # Knowledge base semantic retrieval
│       └── user_service.py         # User credentials & password hashing
│
├── frontend/                       # Modern Glassmorphic Web Client
│   ├── index.html                  # Institutional landing & showcase page
│   ├── auth/
│   │   ├── signin.html             # Role-based login portal
│   │   └── signup.html             # New student & faculty registration
│   ├── avatars/
│   │   ├── avatar.glb              # Ready Player Me 3D female avatar model
│   │   └── README.md               # 3D Avatar customization guide
│   ├── css/
│   │   ├── auth.css                # Authentication styles
│   │   ├── chat.css                # Chatbot & 3D avatar viewport styling
│   │   ├── dashboard.css           # Common dashboard widgets
│   │   ├── features.css            # Feature showcase styles
│   │   ├── how-it-works.css        # Architecture guide styles
│   │   ├── pages.css               # General page layouts
│   │   └── style.css               # Core design tokens & typography
│   ├── js/
│   │   ├── auth.js                 # JWT token handling & auth state
│   │   ├── chatbot.js              # Chat messaging, file attachments & markdown
│   │   ├── script.js               # Common navigation & UI interactions
│   │   ├── voice-avatar.js         # TalkingHead 3D controller & wake word engine
│   │   ├── talkinghead/            # TalkingHead.js viseme & lip-sync library
│   │   └── three/                  # Three.js 3D WebGL engine & GLTF loaders
│   └── pages/
│       ├── about.html              # College & project background
│       ├── admin-dashboard.html    # Administrative management cockpit
│       ├── chat.html               # 3D JARVIS Assistant & chat interface
│       ├── features.html           # Full feature directory
│       ├── hod-dashboard.html      # Department HOD management cockpit
│       ├── how-it-works.html       # Visual system architecture
│       ├── principal-dashboard.html# Principal institutional cockpit
│       └── student-dashboard.html  # Student academic & attendance dashboard
│
└── project_info/
    └── CAMPUSMIND_AI_FULL_EXPLANATION_GUIDE.html # Presentation Q&A handbook
```

---

## 🔒 Security & Privacy Architecture

1. **Zero Secret Leakage**:
   - `.env`, API credentials, private certificates, and local SQLite databases (`.db`, `.db-wal`, `.db-shm`) are strictly ignored via `.gitignore`.
2. **Cryptographic Protection**:
   - User passwords are irreversibly hashed with `pbkdf2:sha256` with randomized salts.
   - Session authentication uses JSON Web Tokens (JWT) signed with HMAC-SHA256.
3. **Role-Based Isolation**:
   - Strict server-side route decorators (`@token_required`, `@role_required`) guarantee that students cannot access HOD, Principal, or Admin administrative functions.

---

## 👥 Project Team & Affiliation

- **Project Title**: CampusMind AI — Intelligent Academic Companion & Campus Portal
- **Institution**: **Vidya Pratishthan's Commerce and Science College, Indapur (VPCSC Indapur)**
- **Affiliation**: **Savitribai Phule Pune University (SPPU)**
- **Category**: Research & Project Presentation / Avishkar
- **Lead Developer**: Dhanaji Mali & Team
- **Repository**: [https://github.com/Dhanaji005/CampusMind-AI-chatboat](https://github.com/Dhanaji005/CampusMind-AI-chatboat)

---

<p align="center">
  <b>CampusMind AI</b> — Empowering Higher Education with Autonomous Intelligence 🎓🚀
</p>
