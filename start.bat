@echo off
setlocal enabledelayedexpansion
title TradeFlow Launcher

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"

echo ========================================
echo    TradeFlow One-Click Launcher
echo ========================================
echo.

rem ---- [1/5] Check environment ----
echo [1/5] Checking environment...

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo   [X] python not found. Please install Python 3.10+
    pause
    exit /b 1
)
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo   [X] node not found. Please install Node.js 18+
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set "PY_VER=%%i"
for /f "tokens=1" %%i in ('node --version 2^>^&1') do set "NODE_VER=%%i"
echo   [OK] Python !PY_VER!
echo   [OK] Node !NODE_VER!

rem ---- [2/5] Check and free ports ----
echo.
echo [2/5] Checking ports...
call :kill_port 3001
call :kill_port 5173

rem ---- [3/5] Check backend deps ----
echo.
echo [3/5] Checking backend dependencies...
python -c "import fastapi" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   [OK] Backend deps installed
) else (
    echo   Installing backend deps...
    pushd "%BACKEND_DIR%"
    pip install -r requirements.txt -q
    if !ERRORLEVEL! neq 0 (
        echo   [X] Backend deps install failed
        popd
        pause
        exit /b 1
    )
    popd
    echo   [OK] Backend deps installed
)

rem ---- [4/5] Check frontend deps ----
echo.
echo [4/5] Checking frontend dependencies...
if exist "%FRONTEND_DIR%\node_modules" (
    echo   [OK] Frontend deps installed
) else (
    echo   Installing frontend deps...
    pushd "%FRONTEND_DIR%"
    call npm install --silent
    if !ERRORLEVEL! neq 0 (
        echo   [X] Frontend deps install failed
        popd
        pause
        exit /b 1
    )
    popd
    echo   [OK] Frontend deps installed
)

rem ---- [5/5] Start services ----
echo.
echo [5/5] Starting services...

rem Start backend in a new window
pushd "%BACKEND_DIR%"
start "TradeFlow-Backend" cmd /k "cd /d %BACKEND_DIR% && python -m main"
popd

rem Wait for backend to be ready
set "BACKEND_READY=0"
for /l %%i in (1,1,30) do (
    >nul 2>&1 curl -sf http://localhost:3001/docs
    if !ERRORLEVEL! equ 0 (
        set "BACKEND_READY=1"
        goto :backend_ok
    )
    timeout /t 1 /nobreak >nul
)
:backend_ok
if !BACKEND_READY! equ 1 (
    echo   [OK] Backend running -^> http://localhost:3001
    echo        Swagger API -^> http://localhost:3001/docs
) else (
    echo   [!] Backend start timeout. Check the "TradeFlow-Backend" window.
)

rem Start frontend in a new window
pushd "%FRONTEND_DIR%"
start "TradeFlow-Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"
popd

rem Wait for frontend to be ready
set "FRONTEND_READY=0"
for /l %%i in (1,1,30) do (
    >nul 2>&1 curl -sf http://localhost:5173
    if !ERRORLEVEL! equ 0 (
        set "FRONTEND_READY=1"
        goto :frontend_ok
    )
    timeout /t 1 /nobreak >nul
)
:frontend_ok
if !FRONTEND_READY! equ 1 (
    echo   [OK] Frontend running -^> http://localhost:5173
) else (
    echo   [!] Frontend start timeout. Check the "TradeFlow-Frontend" window.
)

echo.
echo ========================================
echo    TradeFlow is ready!
echo ========================================
echo    Frontend : http://localhost:5173
echo    Backend  : http://localhost:3001
echo    Swagger  : http://localhost:3001/docs
echo.
echo    Accounts : admin    / admin
echo              user001  / 123456
echo.
echo    Backend and frontend run in separate windows.
echo    Close a window to stop that service.
echo ========================================

pause
exit /b 0


rem ----------------------------------------
rem Subroutine: kill process on given port
rem NOTE: batch vars are global - use KPORT, NOT
rem PORT, or it will override the app's PORT
rem and start the backend on the wrong port!
rem ----------------------------------------
:kill_port
set "KPORT=%~1"
set "FOUND="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%KPORT% "') do (
    if not "%%p"=="0" (
        set "FOUND=1"
        echo   [!] Port !KPORT! is used by PID %%p, killing...
        taskkill /f /pid %%p >nul 2>&1
    )
)
if not defined FOUND (
    echo   [OK] Port !KPORT! is free
) else (
    timeout /t 1 /nobreak >nul
    echo   [OK] Port !KPORT! released
)
exit /b 0
