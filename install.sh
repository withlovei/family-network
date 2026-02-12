#!/usr/bin/env bash
# Install dependencies for backend and frontend (Mac/Linux)
# Run from repo root: ./install.sh

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== Backend ==="
cd "$ROOT/backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "Created .venv"
fi
. .venv/bin/activate
pip install -r requirements.txt
echo "Backend deps OK"

if [ ! -f ".env" ]; then
  cp .env.sample .env
  echo "Copied .env.sample to .env — please set DATABASE_URL and SECRET_KEY"
fi

echo ""
echo "=== Frontend ==="
cd "$ROOT/frontend"
npm install
echo "Frontend deps OK"

if [ ! -f ".env" ]; then
  cp .env.sample .env
  echo "Copied .env.sample to .env"
fi

echo ""
echo "Done. Next: run ./migrate.sh then ./run.sh (or run.bat on Windows)."
