#!/bin/bash
# Fixture test for templates/ci/dod-step.sh (Ch 18 CI fence).
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
STEP="$ROOT/templates/ci/dod-step.sh"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
fails=0
new() {  # fresh repo with base commit; sets B
  rm -rf "$T/r"; mkdir -p "$T/r/.claude" "$T/r/test" "$T/r/src"
  cd "$T/r" || exit 1
  cat > .claude/dod.conf <<'CONF'
DOD_CMD="echo RAN-DOD > $RUNNER_TEMP/ran; test ! -e src/BROKEN"
FENCE="test src .github"
FENCE_OK='^src/app\.py$'
CONF
  echo a > src/app.py; echo t > test/test_a.py
  git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm base
  B=$(git rev-parse HEAD)
}
pr() { git add -A && git -c user.name=t -c user.email=t@t commit -qm pr; }
run() { RUNNER_TEMP="$T/tmp" BASE="$1" "$STEP" > "$T/log" 2>&1; }
exp() { local name=$1 want=$2 got=$3
  [ "$got" = "$want" ] && echo "PASS  $name" || { echo "FAIL  $name (got $got want $want)"; cat "$T/log"; fails=1; }; }
mkdir -p "$T/tmp"
new; echo b > src/app.py; pr; rm -f "$T/tmp/ran"
run "$B"; exp "allowed change: passes, DoD ran" "0/1" "$?/$(test -e "$T/tmp/ran" && echo 1 || echo 0)"
new; echo x >> test/test_a.py; pr; rm -f "$T/tmp/ran"
run "$B"; exp "test edit: fails before the DoD runs" "1/0" "$?/$(test -e "$T/tmp/ran" && echo 1 || echo 0)"
new; echo 'FENCE="docs"; FENCE_OK=".*"; DOD_CMD=true' > .claude/dod.conf; echo x >> test/test_a.py; pr
run "$B"; exp "PR weakens dod.conf: base config still applies" "1" "$?"
new; echo x > conftest.py; pr
run "$B"; exp "new top-level conftest.py: fails" "1" "$?"
new; printf '[pytest]\naddopts = -k nothing\n' > pytest.ini; pr
run "$B"; exp "new root pytest.ini: fails" "1" "$?"
new; echo '[pytest]' > pytest.toml; pr
run "$B"; exp "new pytest.toml: fails" "1" "$?"
new; mkdir -p lib; echo x > lib/conftest.py; pr
run "$B"; exp "nested conftest.py outside the fence: fails" "1" "$?"
new; touch src/BROKEN; echo b > src/app.py; git add -A; git -c user.name=t -c user.email=t@t commit -qm pr
run "$B"; exp "DoD failure fails the step" "1" "$?"
new; echo b > src/app.py; pr
run "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"; r=$?; exp "unknown base SHA: fails (nonzero)" "1" "$([ $r -ne 0 ] && echo 1 || echo 0)"
exit "$fails"
