#!/bin/bash
# LAB-07 grader. Checks a finished run against its DONE.md.
#   labs/lab-07-done/grade.sh <run-dir>
# Uses pristine acceptance tests from this repository, never the
# workspace copy, so an edited test can't make a task pass.
set -u
RUN=$(cd "${1:?run dir}" && pwd)
WS="$RUN/workspace"
TASK=$(cat "$RUN/meta/task_dir")
BASE=$(cat "$RUN/meta/base_sha")
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp -R "$WS/." "$TMP/"; rm -rf "$TMP/.git"
cp "$TASK"/acceptance/* "$TMP/tests/acceptance/"
TARGET=$(basename "$(ls "$TASK"/acceptance/*)")
ok=0
line() { printf '%-9s %-44s %s\n' "$1" "$2" "$3"; }

if (cd "$TMP" && python3 -m pytest -q "tests/acceptance/$TARGET" >/dev/null 2>&1)
then line target "tests/acceptance/$TARGET" PASS
else line target "tests/acceptance/$TARGET" FAIL; ok=1; fi

if (cd "$TMP" && make test lint typecheck >/dev/null 2>&1)
then line regress "make test lint typecheck" PASS
else line regress "make test lint typecheck" FAIL; ok=1; fi

FENCE=()
while IFS= read -r l; do [ -n "$l" ] && FENCE+=("$l"); done < "$TASK/fence.txt"
CHANGED=$(git -C "$WS" diff --name-only "$BASE" -- "${FENCE[@]}";
  git -C "$WS" ls-files --others --exclude-standard -- "${FENCE[@]}")
if [ -z "$CHANGED" ]; then line fence "git diff --name-only (fence paths)" PASS
else line fence "changed: $(echo "$CHANGED" | tr '\n' ' ')" FAIL; ok=1; fi

F="$RUN/final.md"
# git diff --stat prints nothing when the only change is a new, untracked
# file; then the evidence can't contain "files changed", so don't require it.
TRACKED=$(git -C "$WS" diff --stat "$BASE" | tail -n 1)
if [ -f "$F" ] && grep -q "make test" "$F" && grep -q "lint" "$F" \
   && grep -q "typecheck" "$F" && grep -Eq "[0-9]+ passed" "$F" \
   && { [ -z "$TRACKED" ] || grep -Eq "files? changed" "$F"; }
then line evidence "final message has commands + output" PASS
else line evidence "final message has commands + output" FAIL; ok=1; fi

[ $ok -eq 0 ] && echo "RESULT PASS" || echo "RESULT FAIL"
echo "$([ $ok -eq 0 ] && echo PASS || echo FAIL)" > "$RUN/meta/grade"
exit $ok
