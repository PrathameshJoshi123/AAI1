@echo off
title PS-21 Platform Launcher
color 0B
echo ===============================================================================
echo          PS-21 Conversational Insurance Acquisition & Onboarding
echo ===============================================================================
echo.
echo  Starting FastAPI Backend and Next.js Frontend services...
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

:: 1. Verify Backend Directory
if not exist "%BACKEND_DIR%" (
    echo [ERROR] Backend directory not found at: %BACKEND_DIR%
    pause
    exit /b 1
)

:: 2. Verify Frontend Directory
if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found at: %FRONTEND_DIR%
    pause
    exit /b 1
)

:: 3. Launch FastAPI Backend in a separate window
echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "PS-21 Backend (FastAPI - Port 8000)" cmd /k "cd /d "%BACKEND_DIR%" && title PS-21 Backend API && color 0A && echo =================================================== && echo   PS-21 Backend API running on http://127.0.0.1:8000 && echo   Swagger Docs: http://127.0.0.1:8000/docs && echo =================================================== && if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

:: Wait 2 seconds for backend initialization
timeout /t 2 /nobreak >nul

:: 4. Launch Next.js Frontend in a separate window
echo [2/2] Launching Next.js Frontend on http://localhost:3000 ...
start "PS-21 Frontend (Next.js - Port 3000)" cmd /k "cd /d "%FRONTEND_DIR%" && title PS-21 Next.js Frontend && color 09 && echo =================================================== && echo   PS-21 Next.js Frontend running on http://localhost:3000 && echo =================================================== && npm run dev"

echo.
echo ===============================================================================
echo  Both services launched in dedicated terminal windows!
echo.
echo   * Customer Portal:      http://localhost:3000/customer
echo   * Admin Dashboard:      http://localhost:3000/admin
echo   * Advisor Dashboard:    http://localhost:3000/advisor
echo   * Backend REST API:     http://127.0.0.1:8000
echo   * Swagger API Docs:     http://127.0.0.1:8000/docs
echo ===============================================================================
echo.
echo You may close this launcher window; background processes will stay active.
echo.
pause

