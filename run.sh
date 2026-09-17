#!/usr/bin/env bash
# =====================================================
# CAMPUSMIND AI - UNIX RUNNER
# Starts the Flask backend and a static frontend server
# =====================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/bakend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
BACKEND_PORT=5000
FRONTEND_PORT=8000

echo
echo "===================================================="
echo "  CampusMind AI - Startup Script (Unix)"
echo "===================================================="
echo

# ---- 1) CHECK PYTHON ----
echo "[1/4] Checking for Python..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] python3 is not installed or not in PATH."
    exit 1
fi
python3 --version
echo

# ---- 2) CREATE / ACTIVATE VIRTUAL ENVIRONMENT ----
echo "[2/4] Setting up backend virtual environment..."
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Creating virtual environment at $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
echo

# ---- 3) INSTALL REQUIREMENTS ----
echo "[3/4] Installing backend dependencies..."
pip install --upgrade pip >/dev/null
pip install -r "$BACKEND_DIR/requirements.txt"
echo "Dependencies installed."
echo

# ---- 4) START SERVERS ----
echo "[4/4] Starting servers..."
echo "  - Backend  (Flask)  -> http://127.0.0.1:$BACKEND_PORT"
echo "  - Frontend (Static) -> http://127.0.0.1:$FRONTEND_PORT"
echo
echo "Press Ctrl+C to stop both servers."
echo

# Trap to clean up child processes on exit
cleanup() {
    echo
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup INT TERM

# Start backend
(cd "$BACKEND_DIR" && python app.py) &
BACKEND_PID=$!

# Give backend a moment to boot
sleep 2

# Start frontend
(cd "$FRONTEND_DIR" && python3 -m http.server "$FRONTEND_PORT") &
FRONTEND_PID=$!

echo "Both servers are running."
echo
echo "Open the app in your browser:"
echo "  Home : http://localhost:$FRONTEND_PORT/index.html"
echo "  Chat : http://localhost:$FRONTEND_PORT/pages/chat.html"
echo

# Wait for any process to exit
wait
