#!/usr/bin/env bash
# Reset admin password to ADMIN_EMAIL / ADMIN_PASSWORD in backend/.env (Mac/Linux)
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/backend"
. .venv/bin/activate
python -m app.scripts.reset_admin
