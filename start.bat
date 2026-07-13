@echo off
echo ============================================================
echo   Lorex Camera Dashboard - Windows Launcher
echo ============================================================
echo.
echo Checking Python...

where python3 >nul 2>&1
if %ERRORLEVEL%==0 (
    set PYTHON=python3
) else (
    where python >nul 2>&1
    if %ERRORLEVEL%==0 (
        set PYTHON=python
    ) else (
        echo ERROR: Python not found! Please install Python 3 from https://python.org
        pause
        exit /b 1
    )
)

echo Installing required package (requests)...
%PYTHON% -m pip install requests -q

echo Starting dashboard...
%PYTHON% "%~dp0dashboard.py"
pause
