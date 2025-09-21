#!/usr/bin/env bash
set -euo pipefail
API_URL="${API:-http://127.0.0.1:5005}"

# Use project venv if present
if [[ -d "../.venv" ]]; then
  source ../.venv/bin/activate
fi

python - <<'PY'
import pkgutil, sys
sys.exit(0 if pkgutil.find_loader("requests") else 1)
PY

if [[ $? -ne 0 ]]; then
  echo "Installing 'requests'..."
  pip install requests >/dev/null
fi

echo "API=${API_URL}"
API="$API_URL" python scripts/e2e_test.py