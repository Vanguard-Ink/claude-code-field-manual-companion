#!/bin/bash
# Grader validation (spec §2.6): untouched tree passes H1 and fails H2; the
# reference passes H1, H2 and the scoped suite; every mutant fails a check.
# Needs the Roundup venv's python3 first on PATH. No Claude calls.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); K="$HERE/key"
RUNS=${CCFM_RUNS:-$HOME/ccfm-runs}; SRC="$RUNS/_cache/roundup-393187a"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
export PYTHONDONTWRITEBYTECODE=1
fails=0
mkrun() {  # mkrun <name> [patch]: a fake run dir with a git workspace
  local R="$T/$1"; mkdir -p "$R/meta"; cp -R "$SRC/." "$R/workspace"
  git -C "$R/workspace" init -q
  printf '__pycache__/\n*.pyc\n.pytest_cache/\n' >> "$R/workspace/.git/info/exclude"
  git -C "$R/workspace" add -A
  git -C "$R/workspace" -c user.name=t -c user.email=t@t commit -qm base
  git -C "$R/workspace" rev-parse HEAD > "$R/meta/base_sha"
  if [ -n "${2:-}" ]; then git -C "$R/workspace" apply "$2" || return 1; fi
  printf 'python3 -m pytest ... test/test_templating_menu.py\n88 passed\ngit diff --stat\n' \
    > "$R/final.md"
  echo "$R"
}
line() { grep -E "^$2 " "$1" | awk '{print $2}'; }
expect() { local got=$1 want=$2 name=$3
  if [ "$got" = "$want" ]; then echo "PASS  $name"
  else echo "FAIL  $name (got '$got', want '$want')"; fails=1; fi; }

R=$(mkrun pristine); "$HERE/grade.py" "$R" --no-full > "$T/g" 2>&1
expect "$(line "$T/g" H1)/$(line "$T/g" H2)" "PASS/FAIL" "untouched tree: H1 pass, H2 fail"
R=$(mkrun reference "$K/reference.patch"); "$HERE/grade.py" "$R" --no-full > "$T/g" 2>&1
expect "$(line "$T/g" H1)/$(line "$T/g" H2)/$(line "$T/g" SCOPED)/$(line "$T/g" FENCE)" \
  "PASS/PASS/PASS/PASS" "reference: H1, H2, scoped suite, fence pass"
expect "$(grep -c 'BROKEN' "$T/g")" "0" "reference: decisions D1-D4 hold"
for m in "$K"/mutants/*.patch; do
  n=$(basename "$m" .patch)
  R=$(mkrun "m-$n" "$m"); "$HERE/grade.py" "$R" --no-full > "$T/g" 2>&1
  expect "$(line "$T/g" GRADE)" "FAIL" "mutant $n: fails"
done
R=$(mkrun fence "$K/reference.patch")
echo "# x" >> "$R/workspace/share/roundup/templates/classic/html/page.html"
"$HERE/grade.py" "$R" --no-full > "$T/g" 2>&1
expect "$(line "$T/g" FENCE)" "FAIL" "an edit under share/ fails the fence"
expect "$(grep -c 'DECISION D4 BROKEN' "$T/g")" "1" "an edit under share/ breaks D4"
R=$(mkrun untracked "$K/reference.patch"); echo x > "$R/workspace/test/test_extra.py"
"$HERE/grade.py" "$R" --no-full > "$T/g" 2>&1
expect "$(line "$T/g" FENCE)" "FAIL" "an untracked file in test/ fails the fence"
exit "$fails"
