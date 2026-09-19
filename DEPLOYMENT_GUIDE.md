# CampusMind AI - 100% Free Cloud Deployment Guide 🚀

This guide explains how to deploy **CampusMind AI** (Frontend + Backend + Database + Attendance System + OpenRouter AI) **100% Free of Cost** with **zero credit card required**.

---

## 🎯 Best Free Deployment Platforms

| Platform | Free Plan Details | Best For | Credit Card Required? |
| :--- | :--- | :--- | :--- |
| **Render.com** (Recommended) | 750 free instance hrs/month, Free SSL, Git auto-deploy | Complete App (Flask + Static Frontend + SQLite) | ❌ **No** |
| **Koyeb** | 1 Nano service (512MB RAM), no sleep | Flask Backend API | ❌ **No** |
| **Vercel** | Unlimited static bandwidth, global edge CDN | Frontend UI | ❌ **No** |
| **Supabase** | 500MB PostgreSQL, Auth, Edge Functions | Hosted Cloud Database (Optional) | ❌ **No** |

---

## 🌟 Method 1: Render.com (Easiest - All-in-One Free)

Because `bakend/app.py` has built-in static frontend serving, your **entire project (Frontend + API + AI + Attendance)** runs as a single web service.

### Step 1: Push Code to GitHub
1. Open your terminal in this project folder:
   ```bash
   git add .
   git commit -m "Add attendance system and deployment config"
   git push origin main
   ```

### Step 2: Create a Free Web Service on Render
1. Go to [https://render.com](https://render.com) and **Sign Up** using your GitHub account (Free, no credit card).
2. Click **New +** -> Select **Web Service**.
3. Choose **Build and deploy from a Git repository** -> Click **Next**.
4. Select your **CampusMind-AI** repository.

### Step 3: Configure Service Settings
- **Name:** `campusmind-ai` (or any name you like)
- **Region:** Singapore or Frankfurt (Closest to India)
- **Branch:** `main`
- **Runtime:** `Python 3`
- **Build Command:**
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  gunicorn --chdir bakend app:app --bind 0.0.0.0:$PORT
  ```
- **Plan Type:** Select **Free** ($0 / month)

### Step 4: Add Environment Variables
Under the **Environment Variables** section on Render, add:
- `PYTHON_VERSION`: `3.11.8`
- `OPENROUTER_API_KEY`: `your-openrouter-api-key-here`
- `JWT_SECRET`: `your-super-secret-random-key`
- `FLASK_ENV`: `production`

### Step 5: Click "Create Web Service"
- Render will build your dependencies and start Gunicorn.
- Within 2-3 minutes, you will receive a free public HTTPS URL:
  `https://campusmind-ai.onrender.com/`
- You can visit this URL from your phone, laptop, or share it with college professors and students!

---

## 🌟 Method 2: Koyeb (Fast & Never Sleeps)

1. Sign up at [https://www.koyeb.com](https://www.koyeb.com) (Free, no credit card).
2. Click **Create Service** -> **GitHub**.
3. Select your repository.
4. Set:
   - **Build type:** Buildpack
   - **Run command:** `gunicorn --chdir bakend app:app --bind 0.0.0.0:8000`
   - **Port:** `8000`
5. Add your `OPENROUTER_API_KEY` in Environment variables.
6. Deploy!

---

## 📋 Attendance System Quick Guide

### For Department HOD / Faculty:
1. Login to **Dedicated HOD Cockpit** (`/pages/hod-dashboard.html`) or **Admin Portal** (`/pages/admin-dashboard.html`).
2. Go to the **Attendance Engine** tab.
3. You have 2 options:
   - **Option A: Bulk Upload Attendance Sheet**
     - Click **Download Sample CSV Template** to get the standard format.
     - Fill in Roll No, Student Name, Email, Subject, Conducted Lectures, and Attended Lectures.
     - Drag & drop the `.csv` file into the upload zone and click **Auto-Read & Publish Attendance Sheet**.
     - The system automatically parses all records, computes percentages, and assigns SPPU compliance statuses.
   - **Option B: Manual Student Entry**
     - Select Department, Year of Study, Subject, enter Total and Attended lectures, then click **Record Attendance**.

### For Students:
1. Login to **Student Dashboard** (`/student-dashboard.html`).
2. If HOD has **not** yet uploaded attendance:
   - Dashboard displays a clean status: *"Attendance has not yet been published by your Department HOD. Once marked or uploaded, it will automatically appear here."*
3. Once HOD uploads attendance:
   - Student immediately sees their **Overall Attendance Badge** (e.g., `87.9% Good`), colored progress bar, and subject-by-subject lecture breakdown.
   - **Chatbot Companion**: Student can ask in the chat: *"Meri attendance kitni hai?"* or *"What is my attendance?"* and the AI will reply with their exact certified attendance numbers and SPPU university exam eligibility.
