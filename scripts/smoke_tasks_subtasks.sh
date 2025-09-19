#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:5005}"
COOKIE_JAR="cookies.txt"

need_login() {
  AME="$(curl -sS -b "$COOKIE_JAR" "$BASE_URL/auth/me" || true)"
  echo "$AME" | jq -e '.authenticated == true' >/dev/null 2>&1
}

if ! need_login; then
  echo "Not logged in; please run ./scripts/smoke_auth.sh first." >&2
  exit 1
fi

echo "== Create a few tasks =="
# Create a throwaway project first
PROJ="$(curl -sS -b "$COOKIE_JAR" -H "Content-Type: application/json" \
  -d '{"title":"Smoke Project","description":"created by smoke script"}' \
  "$BASE_URL/projects")"
echo "$PROJ"
PID="$(echo "$PROJ" | jq -r '.id')"

# three tasks
for payload in \
  "{\"title\":\"Set up routes\",\"project_id\":$PID,\"status\":\"todo\",\"priority\":\"high\",\"due_date\":\"2025-09-25\"}" \
  "{\"title\":\"Frontend polish\",\"project_id\":$PID,\"status\":\"todo\",\"priority\":\"normal\",\"due_date\":\"2025-10-05\"}" \
  "{\"title\":\"Wire up pagination\",\"project_id\":$PID,\"status\":\"in_progress\",\"priority\":\"low\",\"due_date\":\"2025-09-30\"}"
do
  curl -sS -b "$COOKIE_JAR" -H "Content-Type: application/json" -d "$payload" "$BASE_URL/tasks" | jq .
done

echo "== List tasks (sort by due_date) =="
curl -sS -b "$COOKIE_JAR" "$BASE_URL/tasks?project_id=$PID&sort=due_date" | jq .

echo "== Create a subtask on the third task =="
TASKS="$(curl -sS -b "$COOKIE_JAR" "$BASE_URL/tasks?project_id=$PID&sort=due_date")"
TID="$(echo "$TASKS" | jq -r '.data[-1].id')"  # last one by due_date sort (adjust if needed)
SUB1="$(curl -sS -b "$COOKIE_JAR" -H "Content-Type: application/json" \
  -d "{\"title\":\"Implement backend pagination\",\"task_id\":$TID,\"status\":\"todo\"}" \
  "$BASE_URL/subtasks")"
echo "$SUB1" | jq .
SID="$(echo "$SUB1" | jq -r '.id')"

echo "== Update subtask title+status =="
curl -sS -b "$COOKIE_JAR" -X PATCH -H "Content-Type: application/json" \
  -d '{"title":"Implement backend pagination – updated","status":"in_progress"}' \
  "$BASE_URL/subtasks/$SID" | jq .

echo "== List subtasks for the task =="
curl -sS -b "$COOKIE_JAR" "$BASE_URL/subtasks?task_id=$TID" | jq .

echo "== Delete subtask =="
curl -sS -b "$COOKIE_JAR" -X DELETE "$BASE_URL/subtasks/$SID" | jq .

echo "== Delete the project (cascades tasks/subtasks) =="
curl -sS -b "$COOKIE_JAR" -X DELETE "$BASE_URL/projects/$PID" | jq .

echo "✅ Smoke tests finished."