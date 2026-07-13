@echo off
cd /d "%~dp0"
title Lorex Camera Dashboard
color 0b

echo ============================================================
echo   Lorex Camera Dashboard - Windows Launcher
echo ============================================================
echo.

rem ---- Try to find a working Python ----
set PYTHON_CMD=

echo [1/4] Looking for Python...

rem Try python first (but skip MS Store stub)
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :FOUND_PYTHON
)

rem Try py launcher
py -3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py -3
    goto :FOUND_PYTHON
)

py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    goto :FOUND_PYTHON
)

echo.
echo ERROR: Python not found or not working!
echo.
echo This is often the Microsoft Store Python stub.
echo To fix this:
echo.
echo   1. Open Start menu, search "Manage App Execution Aliases"
echo   2. Turn OFF "App Installer" for python.exe and python3.exe
echo   3. Install Python from https://python.org (NOT the Store)
echo   4. Make sure to check "Add Python to PATH"
echo.
pause
exit /b 1

:FOUND_PYTHON
echo Found: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo [2/4] Installing required package (requests)...
%PYTHON_CMD% -m pip install requests
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: pip install had an issue, trying to continue...
)
echo.

echo [3/4] Starting dashboard server...
echo.
echo Dashboard will open at: http://localhost:8888
echo Press Ctrl+C in this window to stop the server.
echo.
echo ============================================================
%PYTHON_CMD% "%~dp0dashboard.py"

echo.
echo The dashboard server has stopped.
pause
