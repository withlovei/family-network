@echo off
REM Reset admin password to ADMIN_EMAIL / ADMIN_PASSWORD in backend\.env (Windows)
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
cd /d "%ROOT%\backend"
call .venv\Scripts\activate.bat
python -m app.scripts.reset_admin
