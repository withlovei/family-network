#!/usr/bin/env bash
# Run auto tests (API and/or frontend E2E)
# Usage: ./run-tests.sh [api|frontend|all]
# Prerequisites: backend on 8001 (api), frontend on 3008 (frontend)

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

run_api() {
  echo "=== API Tests ==="
  cd api
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv
  fi
  . .venv/bin/activate
  pip install -q -r requirements.txt
  pytest -v
  cd ..
}

run_frontend() {
  echo "=== Frontend E2E Tests ==="
  cd frontend
  npm install --silent
  npx playwright install chromium 2>/dev/null || true
  npx playwright test
  cd ..
}

case "${1:-all}" in
  api)      run_api ;;
  frontend) run_frontend ;;
  all)
    run_api
    run_frontend
    ;;
  *)
    echo "Usage: $0 [api|frontend|all]"
    exit 1
    ;;
esac

echo "Tests completed."
