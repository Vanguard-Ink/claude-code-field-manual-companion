#!/bin/bash
# Stop gate v3: ends as PASSED, BLOCKED or ERROR.
# Letting Claude stop is not acceptance: trust only
# a PASSED record whose head is the commit you are
# checking, and re-run the checks in CI.
IN=$(cat)
RUN="$(date -u +%FT%TZ) pid $$"
cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || {
  echo "DoD gate ERROR: no project dir" >&2; exit 0; }

status() {  # one record per run, first line = state
  mkdir -p notes 2>/dev/null &&
    printf '%s %s\n%s\n' "$1" "$RUN" "$2" \
      2>/dev/null > notes/dod-status.txt
}
say() { echo "DoD gate: $1" >&2; }
error() {   # the gate can't run: stop, not PASSED
  status ERROR "$1" || say "can't write status"
  say "ERROR: $1"
  exit 0
}
# Invalidate the last verdict first. If this run
# dies or times out, RUNNING is left, never an old
# PASSED.
status RUNNING "checks started" ||
  error "can't write notes/dod-status.txt"

command -v jq >/dev/null || error "jq not found"
SID=$(jq -r '.session_id // empty' <<<"$IN")
[ -n "$SID" ] || error "no session_id in input"
BASE=$(cat .claude/dod-base 2>/dev/null)
git rev-parse -q --verify "$BASE^{commit}" \
  >/dev/null || error "missing or bad dod-base"

N_FILE="${TMPDIR:-/tmp}/dod-gate-$SID"
N=$(cat "$N_FILE" 2>/dev/null)
N=$(( ${N//[^0-9]/} + 1 ))
block() {
  echo "$N" > "$N_FILE"
  if [ "$N" -gt 5 ]; then
    status BLOCKED "gave up after 5 tries: $1" ||
      say "can't write status"
    exit 0   # Claude may stop; the task is NOT done
  fi
  status BLOCKED "try $N/5: $1" ||
    say "can't write status"
  # JSON, not exit 2: a reason that quotes a test
  # log stays a block whatever the log says.
  jq -n --arg r "DoD gate ($N/5): $1" \
    '{decision: "block", reason: $r}'
  exit 0
}

LOG=$(mktemp) || error "mktemp failed"
make test lint typecheck > "$LOG" 2>&1 \
  || block "checks failed. Fix the cause; don't
skip or edit tests. $(tail -n 30 "$LOG")"

FENCE=(tests/acceptance migrations .github Makefile)
CHANGED=$(git diff --name-only "$BASE" -- \
  "${FENCE[@]}") || error "git diff failed"
NEW=$(git ls-files --others --exclude-standard \
  -- "${FENCE[@]}") || error "git ls-files failed"
[ -z "$CHANGED$NEW" ] || block "fenced files changed:
$CHANGED $NEW"

rm -f "$N_FILE"
status PASSED "base $BASE head $(git rev-parse HEAD)" \
  || error "can't write notes/dod-status.txt"
exit 0
