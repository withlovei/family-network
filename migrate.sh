#!/usr/bin/env bash
# Run database migrations (Mac/Linux)
# Ensure PostgreSQL is running and .env is configured in backend/

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install -q -r requirements.txt
alembic upgrade head
echo "Migrations completed."
