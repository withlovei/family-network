#!/usr/bin/env bash
# Run backend and frontend (Mac/Linux)
# Usage: ./run.sh [backend|frontend|all]

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

run_backend() {
  echo "Starting backend on http://localhost:8001 ..."
  cd "$ROOT/backend"
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv
  fi
  . .venv/bin/activate
  pip install -q -r requirements.txt
  uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
}

run_frontend() {
  echo "Starting frontend on http://localhost:3008 ..."
  cd "$ROOT/frontend"
  npm run dev
}

case "${1:-all}" in
  backend)  run_backend ;;
  frontend) run_frontend ;;
  all)
    run_backend &
    BACKEND_PID=$!
    sleep 3
    run_frontend
    kill $BACKEND_PID 2>/dev/null || true
    ;;
  *)
    echo "Usage: $0 [backend|frontend|all]"
    exit 1
    ;;
esac
