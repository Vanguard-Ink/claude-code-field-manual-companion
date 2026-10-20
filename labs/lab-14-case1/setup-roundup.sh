#!/bin/bash
# LAB-14 one-time setup: pinned Roundup tree, its venv, and the baseline.
#   labs/lab-14-case1/setup-roundup.sh            (about 15 minutes)
# Never runs Roundup's setup.py, make, or repo scripts; it does run the
# test suite, which executes the repo's conftest.py (treat it as code).
set -euo pipefail
SHA=393187a6c459f4c4b5625f399541583ddc5593c8
RUNS=${CCFM_RUNS:-$HOME/ccfm-runs}
CACHE="$RUNS/_cache"; SRC="$CACHE/roundup-393187a"
BASE="$CACHE/roundup-baseline"; VENV=${CASE1_VENV:-$HOME/venv-roundup}
HERE=$(cd "$(dirname "$0")" && pwd)
[ "$(id -u)" != 0 ] || { echo "run as a normal user, not root" >&2; exit 1; }
mkdir -p "$CACHE" "$BASE"

echo "== 1. pinned source ($SHA)"
if [ ! -f "$SRC/roundup/cgi/templating.py" ]; then
  T=$(mktemp -d)
  git clone -q https://github.com/roundup-tracker/roundup "$T/r"
  git -C "$T/r" checkout -q "$SHA"
  [ "$(git -C "$T/r" rev-parse HEAD)" = "$SHA" ] \
    || { echo "checkout is not $SHA" >&2; exit 1; }
  mkdir -p "$SRC"
  git -C "$T/r" archive "$SHA" | tar -x -C "$SRC"
  rm -rf "$T"
fi
echo "$SHA" > "$BASE/source_sha"

echo "== 2. venv at $VENV"
if [ ! -x "$VENV/bin/python3" ]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -q pytest pytest-cov pytest-env pytest-subtests \
  coverage hypothesis mock pyjwt requests markdown2 pygments \
  beautifulsoup4 docutils jinja2 mistune==0.8.4 pytz whoosh Markdown \
  brotli justhtml zstd
"$VENV/bin/python3" -V > "$BASE/python_version"
"$VENV/bin/pip" freeze > "$BASE/pip-freeze.txt"

echo "== 3. grader self-check on a scratch copy (no Claude calls)"
PATH="$VENV/bin:$PATH" "$HERE/validate-key.sh"

echo "== 4. baseline: scoped suite, then the full suite twice (~10 min)"
W=$(mktemp -d); cp -R "$SRC/." "$W/"
cd "$W"
export PYTHONDONTWRITEBYTECODE=1
PT=("$VENV/bin/python3" -m pytest -p no:cacheprovider -q)
s0=$(date +%s)
"${PT[@]}" test/test_templating.py test/test_cgi.py > "$BASE/scoped.log" 2>&1 \
  || true
echo "scoped_seconds $(( $(date +%s) - s0 ))" > "$BASE/timing.txt"
for n in 1 2; do
  s0=$(date +%s)
  "${PT[@]}" -r fE test/ > "$BASE/full-$n.log" 2>&1 || true
  echo "full${n}_seconds $(( $(date +%s) - s0 ))" >> "$BASE/timing.txt"
done
# Failures in either baseline run are not counted against an agent.
grep -hoE '^(FAILED|ERROR) [^ ]+' "$BASE"/full-[12].log \
  | awk '{print $2}' | sort -u > "$BASE/failing.txt" || true
"${PT[@]}" --cov=roundup.cgi.templating --cov-branch \
  --cov-report=json:"$BASE/coverage-before.json" \
  test/test_templating.py test/test_cgi.py > /dev/null 2>&1 || true
cd - > /dev/null; rm -rf "$W"
tail -n 1 "$BASE"/full-1.log "$BASE"/full-2.log
cat "$BASE/timing.txt"
echo "baseline failures (ignored by the grader): $(wc -l < "$BASE/failing.txt")"
echo "Setup done. Baseline in $BASE"
