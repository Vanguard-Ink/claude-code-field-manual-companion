#!/bin/bash
# Stop gate: block on likely duplicates and on files
# changed outside the task's Scope list in DONE.md.
IN=$(cat)
cd "$CLAUDE_PROJECT_DIR" || exit 0
SID=$(jq -r '.session_id' <<< "$IN")
N_FILE="${TMPDIR:-/tmp}/drift-gate-$SID"
N=$(( $(cat "$N_FILE" 2>/dev/null || echo 0) + 1 ))
BASE=$(cat .claude/dod-base 2>/dev/null || echo HEAD)

MSG=$(python3 .claude/hooks/dupcheck.py --base "$BASE")
DONE=$(ls tasks/*/DONE.md 2>/dev/null | head -n 1)
if [ -n "$DONE" ]; then
  SCOPE=$(sed -n '/^## Scope/,/^## /p' "$DONE" |
    sed -n 's/^- \([^ ]*\).*/\1/p')
  OUT=$( { git diff --name-only "$BASE"
    git ls-files --others --exclude-standard
  } | sort -u | while read -r f; do
    case "$f" in .claude/*|notes/*) continue ;; esac
    hit=no
    for s in $SCOPE; do
      case "$f" in "$s"|"$s"*) hit=yes ;; esac
    done
    [ $hit = no ] && echo "outside scope: $f"
  done)
  MSG=$(printf '%s\n%s' "$MSG" "$OUT" | sed '/^$/d')
fi
# A finding explained in notes/decisions.md is accepted.
if [ -f notes/decisions.md ]; then
  MSG=$(echo "$MSG" | while read -r m; do
    key=$(sed -E 's/.*reuse ([^ ]+).*/\1/; s/^outside scope: //' <<< "$m")
    grep -qF "$key" notes/decisions.md || echo "$m"
  done)
fi
[ -z "$MSG" ] && { rm -f "$N_FILE"; exit 0; }
echo "$N" > "$N_FILE"
if [ "$N" -gt 2 ]; then
  mkdir -p notes
  echo "$MSG" > notes/drift-gate.txt
  exit 0   # let it stop; a human reads the marker
fi
echo "Drift gate ($N/2): $MSG
Reuse the existing helper and keep to Scope, or
explain why not in notes/decisions.md." >&2
exit 2
