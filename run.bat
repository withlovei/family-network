@echo off
REM Run backend and frontend (Windows)
REM Usage: run.bat [backend|frontend|all]

set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%

if "%1"=="" set CMD=all
if "%1"=="backend" set CMD=backend
if "%1"=="frontend" set CMD=frontend
if "%1"=="all" set CMD=all

if "%CMD%"=="backend" goto backend
if "%CMD%"=="frontend" goto frontend
if "%CMD%"=="all" goto all
echo Usage: run.bat [backend^|frontend^|all]
exit /b 1

:backend
echo Starting backend on http://localhost:8001 ...
cd /d "%ROOT%\backend"
if not exist ".venv" python -m venv .venv
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
goto end

:frontend
echo Starting frontend on http://localhost:3008 ...
cd /d "%ROOT%\frontend"
call npm run dev
goto end

:all
start "Backend" cmd /k "cd /d %ROOT%\backend && (if not exist .venv python -m venv .venv) && .venv\Scripts\activate.bat && pip install -q -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 5 /nobreak >nul
start "Frontend" cmd /k "cd /d %ROOT%\frontend && npm run dev"
goto end

:end
