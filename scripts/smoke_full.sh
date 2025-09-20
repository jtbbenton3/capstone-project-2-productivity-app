#!/usr/bin/env bash
set -euo pipefail

# --- find curl robustly ---
CURL_BIN="${CURL_BIN:-$(command -v curl || true)}"
if [[ -z "${CURL_BIN}" ]]; then
  if [[ -x /usr/bin/curl ]]; then
    CURL_BIN="/usr/bin/curl"
  else
    echo "❌ curl not found. Install with:  brew install curl  (or)  xcode-select --install" >&2
    exit 1
  fi
fi

# --- config ---
API="${API:-http://127.0.0.1:5005}"
COOKIE_JAR="${COOKIE_JAR:-cookies.txt}"

# --- helpers ---
b()  { printf '\033[1m%s\033[0m\n' "$*"; }
ok() { printf '✅ %s\n' "$*"; }
die(){ printf '❌ %s\n' "$*" >&2; exit 1; }

curl_json() {
  # usage: curl_json METHOD PATH [JSON_BODY]
  local METHOD="$1"; shift
  local PATH="$1"; shift
  local DATA="${1:-}"

  if [[ -n "$DATA" ]]; then
    "${CURL_BIN}" -sS -X "$METHOD" "$API$PATH" \
      -H 'Content-Type: application/json' \
      -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
      --data "$DATA"
  else
    "${CURL_BIN}" -sS -X "$METHOD" "$API$PATH" \
      -H 'Content-Type: application/json' \
      -b "$COOKIE_JAR" -c "$COOKIE_JAR"
  fi
}

jqget() { echo "$1" | jq -r "$2"; }
require_jq() { command -v jq >/dev/null || die "jq is required (macOS: brew install jq)"; }

# --- main ---
require_jq
: > "$COOKIE_JAR"

# quick health check so we fail fast if server isn't running
HEALTH="$(curl_json GET /health || true)"
echo "$HEALTH" | jq -e '.status=="ok"' >/dev/null 2>&1 || die "Backend not reachable at $API (start it first)."

TS="$(date +%s)"
USER="smokeuser_${TS}"
EMAIL="smoke_${TS}@example.com"
PASS="pass12345!"

b "Auth: signup (or login if exists)"
RESP="$(curl_json POST /auth/signup "{\"username\":\"$USER\",\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" || true)"
if echo "$RESP" | jq -e '.id' >/dev/null 2>&1; then
  ok "signed up as $USER"
else
  RESP="$(curl_json POST /auth/login "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" || true)"
  echo "$RESP" | jq -e '.id' >/dev/null 2>&1 || die "signup/login failed: $RESP"
  ok "logged in as $EMAIL"
fi

RESP="$(curl_json GET /auth/me)"
[[ "$(jqget "$RESP" '.authenticated')" == "true" ]] || die "/auth/me not authenticated"
ok "/auth/me -> authenticated=true"

b "Create project"
RESP="$(curl_json POST /projects "{\"title\":\"Smoke Project\",\"description\":\"created by smoke\"}")"
PID="$(jqget "$RESP" '.id')"
[[ "$PID" != "null" ]] || die "project create failed: $RESP"
ok "project id=$PID"

b "Create 12 tasks (varied status/priority)"
STATUSES=(todo in_progress done)
PRIORITIES=(low normal high)
for i in $(seq 1 12); do
  S="${STATUSES[$(( (i-1) % 3 ))]}"
  P="${PRIORITIES[$(( (i-1) % 3 ))]}"
  TITLE="Task $i"
  curl_json POST /tasks "{\"project_id\":$PID,\"title\":\"$TITLE\",\"due_date\":null,\"priority\":\"$P\",\"status\":\"$S\"}" >/dev/null
done
ok "12 tasks created"

b "List tasks paginated (per_page=5)"
RESP="$(curl_json GET "/tasks?project_id=$PID&page=1&per_page=5&sort=due_date")"
PAGE="$(jqget "$RESP" '.meta.page')"
PAGES="$(jqget "$RESP" '.meta.pages')"
TOTAL="$(jqget "$RESP" '.meta.total')"
[[ "$PAGE" == "1" ]] || die "expected page 1, got $PAGE"
[[ "$TOTAL" -ge 12 ]] || die "expected total>=12, got $TOTAL"
[[ "$PAGES" -ge 3 ]] || die "expected pages>=3, got $PAGES"
ok "pagination looks good (page=$PAGE pages=$PAGES total=$TOTAL)"

b "Filter by status=done"
RESP="$(curl_json GET "/tasks?project_id=$PID&status=done&per_page=50")"
UNIQ="$(echo "$RESP" | jq -r '[.data[].status] | unique | length')"
if [[ "$UNIQ" -gt 0 ]]; then
  ONE="$(echo "$RESP" | jq -r '[.data[].status] | unique | .[0]')"
  [[ "$ONE" == "done" ]] || die "filter returned non-done tasks"
fi
ok "status filter works"

b "Update one task (status + priority)"
FIRST_ID="$(echo "$RESP" | jq -r '.data[0].id // empty')"
if [[ -z "$FIRST_ID" || "$FIRST_ID" == "null" ]]; then
  FIRST_ID="$(curl_json GET "/tasks?project_id=$PID&per_page=1" | jq -r '.data[0].id')"
fi
curl_json PATCH "/tasks/$FIRST_ID" '{"status":"in_progress","priority":"high"}' >/dev/null
ok "task $FIRST_ID updated"

b "Subtasks CRUD"
ST="$(curl_json POST /subtasks "{\"task_id\":$FIRST_ID,\"title\":\"Implement X\"}")"
SID="$(jqget "$ST" '.id')"
[[ "$SID" != "null" ]] || die "subtask create failed"
curl_json PATCH "/subtasks/$SID" '{"status":"done"}' >/dev/null
LIST="$(curl_json GET "/subtasks?task_id=$FIRST_ID")"
COUNT="$(echo "$LIST" | jq '[.[]] | length')"
[[ "$COUNT" -ge 1 ]] || die "subtask not listed"
curl_json DELETE "/subtasks/$SID" >/dev/null
ok "subtasks create/toggle/delete ok"

b "Delete project (cascade)"
curl_json DELETE "/projects/$PID" >/dev/null
RESP="$(curl_json GET "/tasks?project_id=$PID")"
EMPTY="$(echo "$RESP" | jq -r '.data | length')"
[[ "$EMPTY" == "0" ]] || die "expected tasks empty after project delete"
ok "project delete cascaded"

b "Logout"
curl_json POST /auth/logout >/dev/null
RESP="$(curl_json GET /auth/me)"
[[ "$(jqget "$RESP" '.authenticated')" == "false" ]] || die "still authenticated after logout?"

printf "\n\033[1;32mAll smoke checks passed!\033[0m 🎉\n"