#!/bin/bash
# LAB-06 grader for task L3 (L1 and L2 are scored with the rubric in README).
#   labs/lab-06-legacy/grade.sh <run-dir>
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
RUN=$(cd "${1:?run dir}" && pwd)
WS="$RUN/workspace"
TASK=$(cat "$RUN/meta/task_dir")
BASE=$(cat "$RUN/meta/base_sha")
ok=0
line() { printf '%-9s %-44s %s\n' "$1" "$2" "$3"; }
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp -R "$WS/." "$TMP/"
cp "$TASK"/acceptance/* "$TMP/tests/acceptance/"

if (cd "$TMP" && python3 -m pytest -q tests/acceptance/test_l3_fee_rounding.py >/dev/null 2>&1)
then line target "ticket case and half-cent cases" PASS
else line target "ticket case and half-cent cases" FAIL; ok=1; fi

if (cd "$TMP" && make test lint typecheck >/dev/null 2>&1)
then line regress "make test lint typecheck" PASS
else line regress "make test lint typecheck" FAIL; ok=1; fi

FENCE=()
while IFS= read -r l; do [ -n "$l" ] && FENCE+=("$l"); done < "$TASK/fence.txt"
CHANGED=$(git -C "$WS" diff --name-only "$BASE" -- "${FENCE[@]}";
  git -C "$WS" ls-files --others --exclude-standard -- "${FENCE[@]}")
if [ -z "$CHANGED" ]; then line fence "fence paths unchanged" PASS
else line fence "changed: $(echo "$CHANGED" | tr '\n' ' ')" FAIL; ok=1; fi

# Characterization committed before the first commit that touches fees.py.
FEES=packages/billing/ledgerline_billing/fees.py
C_CHAR=$(git -C "$WS" log --reverse --format=%H "$BASE"..HEAD -- tests/characterization \
  packages/billing/tests/characterization | head -n 1)
C_FEES=$(git -C "$WS" log --reverse --format=%H "$BASE"..HEAD -- "$FEES" | head -n 1)
if [ -n "$C_CHAR" ] && { [ -z "$C_FEES" ] \
   || git -C "$WS" merge-base --is-ancestor "$C_CHAR" "$C_FEES" && [ "$C_CHAR" != "$C_FEES" ]; }
then line order "characterization committed first" PASS
else line order "characterization committed first" FAIL; ok=1; fi

python3 "$HERE/grade_l3.py" "$TMP" "$BASE" || ok=1
[ $ok -eq 0 ] && echo "RESULT PASS" || echo "RESULT FAIL"
echo "$([ $ok -eq 0 ] && echo PASS || echo FAIL)" > "$RUN/meta/grade"
exit $ok
