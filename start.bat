@echo off
cd /d "%~dp0"
title Lorex Camera Dashboard

color 0b
echo ============================================================
echo   Lorex Camera Dashboard - Windows Launcher
echo ============================================================
echo.

REM ---- Check Python ----
echo [1/4] Checking for Python...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Python not found!
    echo Please install Python 3 from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
python --version
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Python failed to start!
    pause
    exit /b 1
)
echo.

REM ---- Install requests ----
echo [2/4] Installing required package (requests)...
python -m pip install requests
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: pip install had an issue, trying to continue...
)
echo.

REM ---- Start Dashboard ----
echo [3/4] Starting dashboard server...
echo.
echo Dashboard will open at: http://localhost:8888
echo Press Ctrl+C in this window to stop the server.
echo.
echo ============================================================
python "%~dp0dashboard.py"

REM If we get here the server stopped
echo.
echo The dashboard server has stopped.
pause
