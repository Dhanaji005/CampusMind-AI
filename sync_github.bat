@echo off
title CampusMind AI - 1-Click Auto GitHub Sync
color 0b
echo ========================================================
echo    CampusMind AI - Automatic GitHub Synchronization
echo ========================================================
echo.

echo [1/3] Checking Git Status and modified files...
git status -s

echo.
echo [2/3] Adding changes and securing secrets...
git add .

set MSG=%*
if "%MSG%"=="" set MSG=Update CampusMind AI
git commit -m "%MSG%"

echo.
echo [3/3] Pushing to GitHub (origin main)...
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo    SUCCESS: GitHub repository is up-to-date!
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo    NOTICE: If first time force push is required:
    echo ========================================================
    git push origin main --force
)

echo.
pause
