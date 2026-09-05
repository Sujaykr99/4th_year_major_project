@echo off
title Matrix - Career Intelligence Platform
echo.
echo  ================================
echo   MATRIX - Cleaning old processes
echo  ================================

:: Kill anything on port 8000 (backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: Kill anything on ports 5173-5176 (frontend / Vite)
for %%p in (5173 5174 5175 5176) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p 2^>nul') do (
        taskkill /PID %%a /F >nul 2>&1
    )
)

echo  Old processes cleared.
echo.
echo  ================================
echo   Starting Backend (port 8000)...
echo  ================================
start "Matrix Backend" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo  ================================
echo   Starting Frontend (port 5173)...
echo  ================================
start "Matrix Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo  ================================
echo   READY
echo   Backend:  http://localhost:8000/api/v1/docs
echo   Frontend: http://localhost:5173
echo  ================================
echo.
pause
