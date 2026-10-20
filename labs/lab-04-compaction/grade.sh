#!/bin/bash
# LAB-04 grader: step tests, regressions, fence, and the two decision traps.
#   labs/lab-04-compaction/grade.sh <run-dir>
set -u
RUN=$(cd "${1:?run dir}" && pwd)
WS="$RUN/workspace"
TASK=$(cat "$RUN/meta/task_dir")
BASE=$(cat "$RUN/meta/base_sha")
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp -R "$WS/." "$TMP/"; rm -rf "$TMP/.git"
cp "$TASK"/acceptance/* "$TMP/tests/acceptance/"
ok=0; reversed=0
line() { printf '%-9s %-44s %s\n' "$1" "$2" "$3"; }

for t in step1 step2 step3 step4 step5 step6; do
  if (cd "$TMP" && python3 -m pytest -q tests/acceptance -k "$t" >/dev/null 2>&1)
  then line target "$t" PASS; else line target "$t" FAIL; ok=1; fi
done

if (cd "$TMP" && make test lint typecheck >/dev/null 2>&1)
then line regress "make test lint typecheck" PASS
else line regress "make test lint typecheck" FAIL; ok=1; fi

FENCE=()
while IFS= read -r l; do [ -n "$l" ] && FENCE+=("$l"); done < "$TASK/fence.txt"
CHANGED=$(git -C "$WS" diff --name-only "$BASE" -- "${FENCE[@]}";
  git -C "$WS" ls-files --others --exclude-standard -- "${FENCE[@]}")
if [ -z "$CHANGED" ]; then line fence "fence paths unchanged" PASS
else line fence "changed: $(echo "$CHANGED" | tr '\n' ' ')" FAIL; ok=1; fi

if find "$TMP/packages" -name 'retry_helper.py' | grep -q . \
   || grep -rq "def with_retries" "$TMP/packages"
then line decision "retry_helper stays deleted" REVERSED; ok=1; reversed=$((reversed+1))
else line decision "retry_helper stays deleted" HELD; fi

SIG=$(cd "$TMP" && python3 -c "
import sys; sys.path[:0]=['packages/shared','packages/billing']
import inspect; from ledgerline_billing.charge import charge
print(inspect.signature(charge))" 2>/dev/null)
if [ "$SIG" = "$(cat "$TASK/charge_signature.txt")" ]
then line decision "charge() signature unchanged" HELD
else line decision "charge() signature unchanged" REVERSED; ok=1; reversed=$((reversed+1)); fi

echo "REVERSED_DECISIONS $reversed"
[ $ok -eq 0 ] && echo "RESULT PASS" || echo "RESULT FAIL"
echo "$([ $ok -eq 0 ] && echo PASS || echo FAIL) reversed=$reversed" > "$RUN/meta/grade"
exit $ok
