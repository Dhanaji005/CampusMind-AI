@echo off
REM =====================================================
REM CAMPUSMIND AI - WINDOWS RUNNER
REM Starts the Flask backend and a static frontend server
REM =====================================================

setlocal ENABLEDELAYEDEXPANSION

REM ---- CONFIG ----
set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%bakend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"
set "VENV_DIR=%BACKEND_DIR%\.venv"
set "BACKEND_PORT=5000"
set "FRONTEND_PORT=8000"

REM ---- COLORS (optional) ----
echo.
echo ====================================================
echo   CampusMind AI - Startup Script (Windows)
echo ====================================================
echo.

REM ---- 1) CHECK PYTHON ----
echo [1/4] Checking for Python...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

REM ---- 2) CREATE / ACTIVATE VIRTUAL ENVIRONMENT ----
echo [2/4] Setting up backend virtual environment...
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtual environment at %VENV_DIR% ...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)
echo.

REM ---- 3) INSTALL REQUIREMENTS ----
echo [3/4] Installing backend dependencies...
call "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip >nul
call "%VENV_DIR%\Scripts\python.exe" -m pip install -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)
echo Dependencies installed.
echo.

REM ---- 4) START SERVERS ----
echo [4/4] Starting servers...
echo   - Backend  (Flask)  -> http://127.0.0.1:%BACKEND_PORT%
echo   - Frontend (Static) -> http://127.0.0.1:%FRONTEND_PORT%
echo.
echo Press Ctrl+C in each window to stop the servers.
echo.

REM Start the backend in a new window
start "CampusMind Backend (Flask :%BACKEND_PORT%)" cmd /k ^
    "cd /d %BACKEND_DIR% && call %VENV_DIR%\Scripts\activate && python app.py"

REM Wait a moment so the backend boots first
timeout /t 2 /nobreak >nul

REM Start the frontend in a new window
start "CampusMind Frontend (Static :%FRONTEND_PORT%)" cmd /k ^
    "cd /d %FRONTEND_DIR% && python -m http.server %FRONTEND_PORT%"

echo Both servers are starting in separate windows.
echo.
echo Open the app in your browser:
echo   Home : http://localhost:%FRONTEND_PORT%/index.html
echo   Chat : http://localhost:%FRONTEND_PORT%/pages/chat.html
echo.
echo Close the two server windows to stop the app.
echo.
pause
endlocal
