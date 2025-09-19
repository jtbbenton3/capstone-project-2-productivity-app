#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://127.0.0.1:5005}"
COOKIES="${COOKIES:-cookies.txt}"
HDR=(-H "Content-Type: application/json" -b "$COOKIES")

echo "== Create a few tasks =="
curl -sS "${HDR[@]}" -d '{"title":"Task A","project_id":1,"priority":"high","status":"todo","due_date":"2025-10-01"}' "$BASE/tasks" | jq .
curl -sS "${HDR[@]}" -d '{"title":"Task B","project_id":1,"priority":"low","status":"todo","due_date":"2025-10-05"}'  "$BASE/tasks" | jq .
curl -sS "${HDR[@]}" -d '{"title":"Task C","project_id":1,"priority":"normal","status":"in_progress","due_date":"2025-09-30"}' "$BASE/tasks" | jq .
curl -sS "${HDR[@]}" -d '{"title":"Task D","project_id":1,"priority":"normal","status":"todo"}' "$BASE/tasks" | jq .

echo "== List tasks (default sort -created_at) =="
curl -sS -b "$COOKIES" "$BASE/tasks?page=1&per_page=10" | jq .

echo "== List tasks (sort by due_date asc, NULLS LAST) =="
curl -sS -b "$COOKIES" "$BASE/tasks?sort=due_date" | jq .

echo "== List tasks (sort by -priority) =="
curl -sS -b "$COOKIES" "$BASE/tasks?sort=-priority" | jq .

echo "== Paginate (per_page=2, sort by title asc) =="
curl -sS -b "$COOKIES" "$BASE/tasks?page=1&per_page=2&sort=title" | jq .

# Grab one task id for subtask tests
TASK_ID=$(curl -sS -b "$COOKIES" "$BASE/tasks?sort=title" | jq -r '.data[0].id')
echo "Using TASK_ID=$TASK_ID"

echo "== Create a subtask on TASK_ID =="
curl -sS "${HDR[@]}" -d "{\"title\":\"Wire up pagination (FE)\",\"task_id\":$TASK_ID,\"status\":\"todo\"}" \
     "$BASE/subtasks" | jq .

# Grab the subtask id
SUB_ID=$(curl -sS -b "$COOKIES" "$BASE/subtasks?task_id=$TASK_ID" | jq -r '.[0].id')
echo "Using SUB_ID=$SUB_ID"

echo "== Update subtask title+status =="
curl -sS "${HDR[@]}" -X PATCH -d '{"title":"Wire up pagination (FE) – updated","status":"in_progress"}' \
     "$BASE/subtasks/$SUB_ID" | jq .

echo "== List subtasks (all for current user) =="
curl -sS -b "$COOKIES" "$BASE/subtasks" | jq .

echo "== Filter subtasks by task_id =="
curl -sS -b "$COOKIES" "$BASE/subtasks?task_id=$TASK_ID" | jq .

echo "== Filter subtasks by status =="
curl -sS -b "$COOKIES" "$BASE/subtasks?status=in_progress" | jq .

echo "== Negative test: invalid task status on create =="
set +e
curl -sS "${HDR[@]}" -d "{\"title\":\"Bad status\",\"project_id\":1,\"status\":\"wat\"}" "$BASE/tasks" | jq .
set -e

echo "== Delete subtask =="
curl -sS -b "$COOKIES" -X DELETE "$BASE/subtasks/$SUB_ID" | jq .

echo "== Delete a task (cascades its subtasks if any) =="
TO_DELETE=$(curl -sS -b "$COOKIES" "$BASE/tasks?sort=title" | jq -r '.data[0].id')
curl -sS -b "$COOKIES" -X DELETE "$BASE/tasks/$TO_DELETE" | jq .

echo "✅ Smoke tests finished."