# scripts/smoke_auth.sh
#!/usr/bin/env bash
set -euo pipefail
BASE="${1:-http://127.0.0.1:5005}"

jar=$(mktemp)
trap 'rm -f "$jar"' EXIT

# signup
curl -sS -X POST -H "Content-Type: application/json" \
  -c "$jar" -b "$jar" \
  -d '{"username":"alice","email":"alice@example.com","password":"pass"}' \
  "$BASE/auth/signup" | jq .

# me
curl -sS -c "$jar" -b "$jar" "$BASE/auth/me" | jq .

# logout
curl -sS -X POST -c "$jar" -b "$jar" "$BASE/auth/logout" -o /dev/null -w "%{http_code}\n"