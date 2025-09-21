# scripts/smoke_tasks_subtasks.sh
#!/usr/bin/env bash
set -euo pipefail
BASE="${1:-http://127.0.0.1:5005}"

jar=$(mktemp)
trap 'rm -f "$jar"' EXIT

# login existing (or create) user
curl -sS -X POST -H "Content-Type: application/json" \
  -c "$jar" -b "$jar" \
  -d '{"email":"alice@example.com","password":"pass"}' \
  "$BASE/auth/login" | jq .

# create project
PJSON=$(curl -sS -X POST -H "Content-Type: application/json" -c "$jar" -b "$jar" \
  -d '{"title":"Smoke Project","description":"demo"}' "$BASE/projects")
echo "$PJSON" | jq .
PID=$(echo "$PJSON" | jq -r .id)

# create task
TJSON=$(curl -sS -X POST -H "Content-Type: application/json" -c "$jar" -b "$jar" \
  -d "{\"project_id\":$PID,\"title\":\"Task 1\",\"status\":\"todo\",\"priority\":\"normal\"}" \
  "$BASE/tasks")
echo "$TJSON" | jq .
TID=$(echo "$TJSON" | jq -r .id)

# list tasks
curl -sS -c "$jar" -b "$jar" "$BASE/tasks?project_id=$PID&page=1&per_page=5" | jq .

# create subtask
SJSON=$(curl -sS -X POST -H "Content-Type: application/json" -c "$jar" -b "$jar" \
  -d "{\"task_id\":$TID,\"title\":\"Sub A\"}" "$BASE/subtasks")
echo "$SJSON" | jq .