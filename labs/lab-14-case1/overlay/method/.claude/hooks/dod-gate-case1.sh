#!/bin/bash
# Stop gate v2 for LAB-14 (Chapter 8's gate with Case 1's DoD and fence).
# Ends PASSED, BLOCKED or ERROR in notes/dod-status.txt. Stopping isn't
# acceptance: the hidden grader re-runs everything outside the workspace.
IN=$(cat)
cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || {
  echo "DoD gate ERROR: no project dir" >&2; exit 0; }
# The runner switches the gate on after the plan turn.
[ -e .claude/gate-on ] || exit 0

status() {
  mkdir -p notes &&
    printf '%s %s\n%s\n' "$1" "$(date -u +%FT%TZ)" \
      "$2" > notes/dod-status.txt
}
error() { status ERROR "$1"; echo "DoD gate ERROR: $1" >&2; exit 0; }

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
    status BLOCKED "gave up after 5 tries: $1"
    exit 0
  fi
  status BLOCKED "try $N/5: $1"
  echo "DoD gate ($N/5): $1" >&2
  exit 2
}

LOG=$(mktemp) || error "mktemp failed"
export PYTHONDONTWRITEBYTECODE=1
timeout 600 python3 -m pytest -p no:cacheprovider -q \
  test/test_templating.py test/test_cgi.py \
  test/test_templating_menu.py > "$LOG" 2>&1 \
  || block "checks failed. Fix the cause; don't
skip or edit tests. $(tail -n 30 "$LOG")"

OK='^(roundup/cgi/templating\.py|test/test_templating_menu\.py'
OK="$OK|CHANGES\.txt|notes/.*|\.claude/gate-on)$"
CHANGED=$(git diff --name-only "$BASE" --) \
  || error "git diff failed"
NEW=$(git ls-files --others --exclude-standard) \
  || error "git ls-files failed"
BAD=$(printf '%s\n%s\n' "$CHANGED" "$NEW" \
  | grep -E '^(test/|share/|roundup/|pyproject\.toml$|\.github/)' \
  | grep -vE "$OK" | sort -u)
[ -z "$BAD" ] || block "fenced files changed:
$BAD"

rm -f "$N_FILE"
status PASSED "base $BASE head $(git rev-parse HEAD)" \
  || error "can't write notes/dod-status.txt"
exit 0
