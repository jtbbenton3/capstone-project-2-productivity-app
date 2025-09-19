#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${1:-http://127.0.0.1:5005}   # override with 5001 if you’re running there
JAR="cookies.txt"
TMP_EMAIL="smoke_user_$(date +%s)@example.com"
TMP_PASS="pass1234"
TMP_USER="smoke-$(date +%s)"

echo "== Signup =="
curl -s -i -c "$JAR" -H "Content-Type: application/json" \
  -d "{\"username\":\"$TMP_USER\",\"email\":\"$TMP_EMAIL\",\"password\":\"$TMP_PASS\"}" \
  "$BASE_URL/auth/signup" | sed -n '1,10p'

echo
echo "== Me (after signup, should be authenticated) =="
curl -s -i -b "$JAR" "$BASE_URL/auth/me" | sed -n '1,10p'

echo
echo "== Logout =="
curl -s -i -b "$JAR" -X POST "$BASE_URL/auth/logout" | sed -n '1,10p'

echo
echo "== Me (after logout, should be not authenticated) =="
curl -s -i -b "$JAR" "$BASE_URL/auth/me" | sed -n '1,10p'

echo
echo "== Login with same credentials =="
curl -s -i -b "$JAR" -c "$JAR" -H "Content-Type: application/json" \
  -d "{\"email\":\"$TMP_EMAIL\",\"password\":\"$TMP_PASS\"}" \
  "$BASE_URL/auth/login" | sed -n '1,10p'

echo
echo "== Me (after login, should be authenticated again) =="
curl -s -i -b "$JAR" "$BASE_URL/auth/me" | sed -n '1,10p'

echo
echo "✅ Auth smoke complete."