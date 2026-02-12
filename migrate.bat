@echo off
REM Run database migrations (Windows)
REM Ensure PostgreSQL is running and .env is configured in backend\

set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
cd /d "%ROOT%\backend"
if not exist ".venv" python -m venv .venv
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
alembic upgrade head
echo Migrations completed.
