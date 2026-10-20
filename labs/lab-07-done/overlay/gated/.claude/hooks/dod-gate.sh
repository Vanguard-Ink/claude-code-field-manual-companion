#!/bin/bash
# Stop gate v1 (as run in LAB-07B, 2026-10-07).
# The book prints v2: templates/hooks/dod-gate.sh.
IN=$(cat)
cd "$CLAUDE_PROJECT_DIR" || exit 0
SID=$(echo "$IN" | jq -r '.session_id')
N_FILE="/tmp/dod-gate-$SID"
N=$(( $(cat "$N_FILE" 2>/dev/null || echo 0) + 1 ))

fail() {
  echo "$N" > "$N_FILE"
  if [ "$N" -gt 5 ]; then
    echo "GATE FAILED: $1" > notes/gate-failed.txt
    exit 0   # stop and leave a marker for the human
  fi
  echo "DoD gate ($N/5): $1" >&2
  exit 2
}

LOG=$(mktemp)
make test lint typecheck > "$LOG" 2>&1 \
  || fail "checks failed. Fix the cause; don't
skip or edit tests. $(tail -n 30 "$LOG")"

BASE=$(cat .claude/dod-base 2>/dev/null || echo HEAD)
FENCE="tests/acceptance migrations .github"
CHANGED=$(git diff --name-only "$BASE" -- $FENCE;
  git ls-files --others --exclude-standard -- $FENCE)
[ -n "$CHANGED" ] && fail "fenced files changed:
$CHANGED"

rm -f "$N_FILE"
exit 0
