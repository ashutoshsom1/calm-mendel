@echo off
setlocal enabledelayedexpansion
title LinkedIn Job Hunter - Control Center

echo ================================================================
echo       LinkedIn Premium Job Hunter (Zero-Setup Launcher)
echo ================================================================
echo.

:: 1. Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python was not detected on your system.
    echo [*] Attempting automated installation via Windows Package Manager (winget)...
    where winget >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [*] Installing Python 3.12 silently... Please approve if prompted.
        winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
        echo [*] Python installed! Please close and re-open run.bat to refresh your PATH.
        pause
        exit /b
    ) else (
        echo [ERROR] Neither Python nor winget was found.
        echo Please download and install Python from: https://www.python.org/downloads/
        echo (Make sure to check "Add python.exe to PATH" during installation)
        pause
        exit /b
    )
)

:: 2. Check and setup virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [*] First-time setup detected. Initializing environment...
    python -m venv .venv
    echo [*] Installing dependencies and package...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
    .\.venv\Scripts\python.exe -m pip install -e .
    .\.venv\Scripts\python.exe -m linkedin_jobhunter init
    echo [OK] Setup completed successfully!
    echo.
)

:: 3. Interactive Main Menu
:menu
cls
echo ================================================================
echo       LinkedIn Premium Job Hunter - Control Center
echo ================================================================
echo.
echo   [1] One-Time Login (Connect your LinkedIn Premium account)
echo   [2] Search & Match Jobs (Scrape roles & hiring team leads)
echo   [3] Review & Apply (Co-Pilot: review each job before submit)
echo   [4] Autonomous Apply (Fast batch apply within safety caps)
echo   [5] View Discovered Hiring Managers & InMail Pitches
echo   [6] View Application Pipeline Status
echo   [7] Export Applications to CSV / Excel
echo   [8] Open Configuration File (config\profile.yaml)
echo   [9] Exit
echo.
echo ================================================================
set /p choice="Enter your choice [1-9]: "

if "%choice%"=="1" goto do_login
if "%choice%"=="2" goto do_search
if "%choice%"=="3" goto do_review_apply
if "%choice%"=="4" goto do_auto_apply
if "%choice%"=="5" goto do_leads
if "%choice%"=="6" goto do_status
if "%choice%"=="7" goto do_export
if "%choice%"=="8" goto do_config
if "%choice%"=="9" goto do_exit

echo Invalid selection. Please enter a number between 1 and 9.
timeout /t 2 >nul
goto menu

:do_login
cls
echo Starting login assistant...
.\.venv\Scripts\python.exe -m linkedin_jobhunter login
pause
goto menu

:do_search
cls
set /p search_kw="Enter job title [Press Enter for 'Program Manager']: "
if "%search_kw%"=="" set search_kw=Program Manager
set /p search_loc="Enter location [Press Enter for 'Remote']: "
if "%search_loc%"=="" set search_loc=Remote
set /p search_pages="How many pages to scan? [Default: 2]: "
if "%search_pages%"=="" set search_pages=2

echo Searching for %search_kw% in %search_loc%...
.\.venv\Scripts\python.exe -m linkedin_jobhunter search --keyword "%search_kw%" --location "%search_loc%" --pages %search_pages%
pause
goto menu

:do_review_apply
cls
echo Starting Co-Pilot Apply Mode (will pause at final review screen)...
.\.venv\Scripts\python.exe -m linkedin_jobhunter apply --review
pause
goto menu

:do_auto_apply
cls
set /p app_limit="How many jobs to apply for? [Default: 10]: "
if "%app_limit%"=="" set app_limit=10
.\.venv\Scripts\python.exe -m linkedin_jobhunter apply --limit %app_limit%
pause
goto menu

:do_leads
cls
.\.venv\Scripts\python.exe -m linkedin_jobhunter leads
echo.
set /p lead_id="Enter Lead ID to view full InMail pitch (or press Enter to return): "
if not "%lead_id%"=="" (
    .\.venv\Scripts\python.exe -m linkedin_jobhunter leads --view-draft %lead_id%
)
pause
goto menu

:do_status
cls
.\.venv\Scripts\python.exe -m linkedin_jobhunter status
pause
goto menu

:do_export
cls
.\.venv\Scripts\python.exe -m linkedin_jobhunter export
pause
goto menu

:do_config
start notepad.exe "config\profile.yaml"
goto menu

:do_exit
exit /b
