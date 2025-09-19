#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:5005}"
COOKIE_JAR="cookies.txt"

# unique creds each run
TS="$(date +%s)"
USERNAME="smokeuser_${TS}"
EMAIL="smoke_${TS}@example.com"
PASSWORD="smokepass123"

json() { jq -r "$1"; }

echo "== Signup (fresh unique user) =="
curl -sS -i -c "$COOKIE_JAR" -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  "$BASE_URL/auth/signup" | tee /dev/stderr | awk 'BEGIN{ok=0}/^HTTP\/1\.[01] 201/{ok=1}END{exit !ok}'

echo
echo "== Me (should be authenticated) =="
ME="$(curl -sS -b "$COOKIE_JAR" "$BASE_URL/auth/me")"
echo "$ME"
AUTH="$(echo "$ME" | jq -r '.authenticated')"
if [ "$AUTH" != "true" ]; then
  echo "ERROR: not authenticated right after signup" >&2
  exit 1
fi

echo
echo "== Logout =="
curl -sS -i -b "$COOKIE_JAR" -X POST "$BASE_URL/auth/logout" | tee /dev/stderr >/dev/null

echo
echo "== Me (after logout, should be false) =="
curl -sS -b "$COOKIE_JAR" "$BASE_URL/auth/me"
echo

echo
echo "== Login with same credentials =="
curl -sS -i -c "$COOKIE_JAR" -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  "$BASE_URL/auth/login" | tee /dev/stderr >/dev/null

echo
echo "== Me (after login, should be authenticated) =="
ME2="$(curl -sS -b "$COOKIE_JAR" "$BASE_URL/auth/me")"
echo "$ME2"
AUTH2="$(echo "$ME2" | jq -r '.authenticated')"
[ "$AUTH2" = "true" ] || { echo "ERROR: login did not authenticate"; exit 1; }

echo
echo "✅ Auth smoke complete."