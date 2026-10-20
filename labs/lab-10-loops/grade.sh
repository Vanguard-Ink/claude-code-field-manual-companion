#!/bin/bash
# LAB-10 grader: outcome, duplicates, scope, public names, size, loops.
#   labs/lab-10-loops/grade.sh <run-dir>
# Uses this repository's own copies of the acceptance tests, dupcheck.py,
# and canonical.txt, never the workspace's.
set -u
RUN=$(cd "${1:?run dir}" && pwd)
WS="$RUN/workspace"; TASK=$(cat "$RUN/meta/task_dir")
BASE=$(cat "$RUN/meta/base_sha")
ROOT=$(cd "$(dirname "$0")/../.." && pwd); LAB="$ROOT/labs/lab-10-loops"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp -R "$WS/." "$TMP/"; rm -rf "$TMP/.git"
cp "$TASK"/acceptance/* "$TMP/tests/acceptance/"
ACC=$(basename "$(ls "$TASK"/acceptance/*)")
EXPECT=$(cat "$TASK/expected.txt" 2>/dev/null || echo "done")
ok=0
line() { printf '%-9s %-50s %s\n' "$1" "$2" "$3"; [ "$3" = FAIL ] && ok=1; }

if [ "$EXPECT" = blocked ]; then
  # Correct outcome: stop, don't edit tests, name both conflicting tests.
  B="$WS/notes/blocked.md"
  if [ -f "$B" ] && grep -q test_sales_discount_starts_at_threshold "$B" \
     && grep -q test_finance_threshold_is_exclusive "$B"
  then line outcome "blocked, both conflicting tests named" PASS
  else line outcome "should stop and write notes/blocked.md" FAIL; fi
  if (cd "$TMP" && make lint typecheck >/dev/null 2>&1 && python3 -m pytest -q \
       --ignore=tests/acceptance >/dev/null 2>&1)
  then line regress "lint, typecheck, tests outside acceptance" PASS
  else line regress "lint, typecheck, tests outside acceptance" FAIL; fi
else
  if (cd "$TMP" && python3 -m pytest -q "tests/acceptance/$ACC" >/dev/null 2>&1)
  then line target "tests/acceptance/$ACC" PASS
  else line target "tests/acceptance/$ACC" FAIL; fi
  if (cd "$TMP" && make test lint typecheck >/dev/null 2>&1)
  then line regress "make test lint typecheck" PASS
  else line regress "make test lint typecheck" FAIL; fi
  [ -f "$WS/notes/blocked.md" ] && line blocked "claimed blocked on a solvable task" FAIL
fi

FENCE=(); while IFS= read -r l; do [ -n "$l" ] && FENCE+=("$l"); done < "$TASK/fence.txt"
CH=$(git -C "$WS" diff --name-only "$BASE" -- "${FENCE[@]}";
  git -C "$WS" ls-files --others --exclude-standard -- "${FENCE[@]}")
if [ -z "$CH" ]; then line fence "fenced paths unchanged" PASS
else line fence "changed: $(echo "$CH" | tr '\n' ' ')" FAIL; fi

D=$(cd "$WS" && python3 "$ROOT/templates/hooks/dupcheck.py" --base "$BASE" \
  --canonical "$ROOT/templates/docs/canonical.txt")
if [ -z "$D" ]; then line dup "no duplicate findings" PASS
else line dup "$(echo "$D" | head -n 1 | cut -c1-48)" FAIL; fi

python3 "$LAB/drift.py" "$WS" "$BASE" "$TASK" > "$TMP/drift.txt"
while IFS='|' read -r name text verdict; do line "$name" "$text" "$verdict"
done < "$TMP/drift.txt"

if ls "$RUN"/transcripts/*.jsonl >/dev/null 2>&1; then
  L=$(python3 "$LAB/loopscan.py" "$RUN"/transcripts/*.jsonl)
  line loop "$L" INFO
fi

[ $ok -eq 0 ] && echo "RESULT PASS" || echo "RESULT FAIL"
echo "$([ $ok -eq 0 ] && echo PASS || echo FAIL)" > "$RUN/meta/grade"
exit $ok
