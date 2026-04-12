@echo off
REM =========================================================================
REM  OrgoLife - ONE-CLICK STARTUP SCRIPT (Windows)
REM =========================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo   ================================================
echo     OrgoLife - Organ Donation Platform
echo   ================================================
echo.

REM -- Python Check --
python --version >nul 2>nul
if errorlevel 1 (
    echo   [ERROR] Python not found! Please install Python from https://python.org
    pause
    exit /b 1
)
echo   [OK] Python is installed.

REM -- Virtual Environment --
if not exist "venv" (
    echo   [*] Setup: Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

REM -- Install Dependencies --
echo   [*] Checking packages (this may take 20 seconds)...
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt
python -m pip install -q psycopg2-binary
echo   [OK] Resources ready.

REM -- Launch --
echo.
echo   ================================================
echo     Starting OrgoLife...
echo   ================================================
echo.
echo   Backend API : http://localhost:8000
echo   Application : http://localhost:8000
echo.
echo   Press CTRL+C to stop the server.
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo   [!] Application stopped.
pause
