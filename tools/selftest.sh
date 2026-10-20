#!/bin/bash
# Self-test: checks every template, grader, and reference solution without
# calling Claude. Run from anywhere with your venv active.
#   tools/selftest.sh
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
CCFM_REAL_RUNS=${CCFM_RUNS:-$HOME/ccfm-runs}
export CCFM_RUNS; CCFM_RUNS=$(mktemp -d)
trap 'rm -rf "$CCFM_RUNS"; rm -f /tmp/dod-gate-selftest-* "${TMPDIR:-/tmp}"/dod-gate-selftest-* /tmp/loop-guard-selftest-* /tmp/drift-gate-selftest-*' EXIT
pass=0; fail=0
check() {  # check <name> <expected-exit> <command...>
  local name=$1 want=$2; shift 2
  "$@" >/tmp/ccfm-selftest.log 2>&1; local got=$?
  if [ "$got" = "$want" ]; then pass=$((pass+1)); printf 'PASS  %s\n' "$name"
  else fail=$((fail+1)); printf 'FAIL  %s (exit %s, wanted %s)\n' "$name" "$got" "$want"
       sed 's/^/      /' /tmp/ccfm-selftest.log | tail -n 8; fi
}
newrun() { "$ROOT/tools/new-run.sh" "$@" >/dev/null && ls -td "$CCFM_RUNS"/* | head -n 1; }
commit() { git -C "$1" add -A && git -C "$1" -c user.name=t -c user.email=t@t commit -qm "$2"; }
final_ok() { printf 'make test lint typecheck\n12 passed\n 1 file changed\n' > "$1/final.md"; }

echo "== Tooling"
for t in python3 git make jq; do check "tool: $t" 0 command -v "$t"; done
check "python: pytest, ruff, mypy, tenacity" 0 python3 -c "import pytest, ruff, mypy, tenacity"
if command -v shellcheck >/dev/null; then
  check "shellcheck (all scripts)" 0 shellcheck -S warning \
    "$ROOT"/tools/*.sh "$ROOT"/templates/hooks/*.sh "$ROOT"/templates/statusline/*.sh \
    "$ROOT"/labs/*/grade.sh "$ROOT"/labs/lab-02-session-start/check-probe.sh \
    "$ROOT"/labs/lab-09-skills/reference/apply.sh "$ROOT"/templates/ci/*.sh \
    "$ROOT"/labs/lab-14-case1/*.sh "$ROOT"/labs/lab-14-case1/overlay/method/.claude/hooks/*.sh
fi

check "runner: no bypass flags, no IS_SANDBOX (code lines)" 1 bash -c \
  "grep -vE '^[[:space:]]*#' '$ROOT/tools/run-labs.py' | grep -E 'dangerously-skip|bypassPermissions|IS_SANDBOX'"
check "runner: no interpreter/find/cp/mv wildcards in allowlist" 1 grep -nE '"Bash\((python3?|find|cp|mv|bash|sh) \*\)"' "$ROOT/tools/run-labs.py"

echo "== Sample app"
SA=$(mktemp -d); cp -R "$ROOT/sample-app/." "$SA/"
check "sample-app: make test lint typecheck" 0 make -C "$SA" test lint typecheck
rm -rf "$SA"

echo "== Templates"
while IFS= read -r j; do
  check "valid JSON: ${j#"$ROOT"/}" 0 python3 -m json.tool "$j"
done < <(find "$ROOT/templates" "$ROOT/labs" -name '*.json' -not -path '*/results/*')
check "agent/skill frontmatter (name + description)" 0 python3 - "$ROOT" <<'PY'
import pathlib, sys
bad = []
root = pathlib.Path(sys.argv[1])
for f in list(root.rglob("agents/*.md")) + list(root.rglob("skills/*/SKILL.md")):
    t = f.read_text()
    head = t.split("---")[1] if t.startswith("---") else ""
    if "name:" not in head or "description:" not in head:
        bad.append(str(f))
print("\n".join(bad)); sys.exit(1 if bad else 0)
PY
SJ='{"model":{"display_name":"Opus"},"context_window":{"used_percentage":23.4},"cost":{"total_cost_usd":1.5},"prompt_cache":{"hit_ratio":0.91,"warm":true},"effort":{"level":"high"}}'
check "statusline.sh prints model and %" 0 bash -c "echo '$SJ' | $ROOT/templates/statusline/statusline.sh | grep -q '\[Opus\] 23% context'"
check "statusline-full.sh prints cost and cache" 0 bash -c "echo '$SJ' | $ROOT/templates/statusline/statusline-full.sh | grep -q '1.50 | cache 91%'"
LW=$(mktemp -d); printf 'import os\nx=1\n' > "$LW/bad.py"; printf 'x = 1\n' > "$LW/good.py"
check "lint-edit.sh: bad file -> additionalContext JSON" 0 bash -c \
  "cd $LW && echo '{\"tool_input\":{\"file_path\":\"bad.py\"}}' | $ROOT/templates/hooks/lint-edit.sh | jq -e '.hookSpecificOutput.additionalContext | test(\"F401\")'"
check "lint-edit.sh: clean file -> silent exit 0" 0 bash -c \
  "cd $LW && test -z \"\$(echo '{\"tool_input\":{\"file_path\":\"good.py\"}}' | $ROOT/templates/hooks/lint-edit.sh)\""
rm -rf "$LW"

echo "== CI templates"
check "fan-out.sh: script judges 11 fixture items itself" 0 "$ROOT/tools/test-fan-out.sh"
check "dod-step.sh (Ch 18 CI): fence first, base config, 9 fixtures" 0 "$ROOT/tools/test-dod-step.sh"
check "canary_scan: finds canary in log attr, span attr, span event" 0 bash -c \
  "python3 '$ROOT/tools/canary_scan.py' '$ROOT/tools/fixtures/otlp-canary-dirty.jsonl' CANARY-7f3a | grep -q '^3 hit'"
check "canary_scan: dirty export exits 1" 1 python3 "$ROOT/tools/canary_scan.py" "$ROOT/tools/fixtures/otlp-canary-dirty.jsonl" CANARY-7f3a
check "canary_scan: clean export exits 0" 0 python3 "$ROOT/tools/canary_scan.py" "$ROOT/tools/fixtures/otlp-canary-clean.jsonl" CANARY-7f3a

HD="$CCFM_RUNS/proj with space"; mkdir -p "$HD/notes"; echo HANDOFF-OK > "$HD/notes/handoff.md"
HC=$(jq -r '.hooks.SessionStart[0].hooks[0].command' "$ROOT/templates/settings/compact-handoff.json")
check "compact-handoff: reload works with a space in the project path" 0 bash -c \
  "CLAUDE_PROJECT_DIR='$HD' sh -c '$HC' | grep -q HANDOFF-OK"

SC=$(mktemp -d); printf '{"user":"Planted.User@Example.com","x":"planted.user\\u0040example.com","p":"/home/jdoe/x","c":"git -c user.name=planted.user"}\n{"key": "user.account_uuid", "value": {"stringValue": "96c4-real"}}\n' > "$SC/t.jsonl"
python3 "$ROOT/tools/scrub-email.py" "$SC" planted.user@example.com --user jdoe >/dev/null
check "scrub-email: planted address removed (plain and JSON-escaped)" 1 grep -qiE 'planted\.user(@|\\u0040)example\.com' "$SC/t.jsonl"
check "scrub-email: login name in home paths removed" 1 grep -q '/home/jdoe' "$SC/t.jsonl"
check "scrub-email: email local part (git user.name) removed" 1 grep -q 'user.name=planted.user' "$SC/t.jsonl"
check "scrub-email: OTel account UUID redacted" 1 grep -q '96c4-real' "$SC/t.jsonl"
rm -rf "$SC"

echo "== Stop gate (dod-gate.sh) in a gated LAB-07 run"
RUN=$(newrun lab-07 gated T05); WS="$RUN/workspace"
SID_PREFIX="selftest-$$-$RANDOM"
gate() { echo "{\"session_id\":\"$SID_PREFIX-$1\"}" | CLAUDE_PROJECT_DIR="$WS" "$WS/.claude/hooks/dod-gate.sh"; }
check "gate blocks while acceptance test fails (exit 2)" 2 gate a
cp -R "$ROOT"/labs/lab-07-done/tasks/T05-*/reference/. "$WS/"
check "gate passes after the reference fix (exit 0)" 0 gate b
echo "# edited" >> "$WS"/tests/acceptance/test_t05_pagination.py
check "gate blocks an edited acceptance test (exit 2)" 2 gate c
for _ in 1 2 3 4 5; do gate d >/dev/null 2>&1; done
check "gate stops after 5 blocks and leaves a marker (exit 0)" 0 gate d
check "marker notes/gate-failed.txt written" 0 test -s "$WS/notes/gate-failed.txt"

echo "== Stop gate v3 (templates/hooks/dod-gate.sh): PASSED / BLOCKED / ERROR"
RUN=$(newrun lab-07 gated T05); WS="$RUN/workspace"
cp "$ROOT/templates/hooks/dod-gate.sh" "$WS/.claude/hooks/dod-gate.sh"
SP="selftest-$$-$RANDOM-v3"
g2() { echo "{\"session_id\":\"$SP-$1\"}" | CLAUDE_PROJECT_DIR="${2:-$WS}" "$ROOT/templates/hooks/dod-gate.sh"; }
# a block is exit 0 plus {"decision":"block"} on stdout
blk() { local o; o=$(g2 "$@" 2>/dev/null) || return 9; jq -e '.decision == "block" and (.reason | length > 0)' <<<"$o" >/dev/null; }
nob() { local o; o=$(g2 "$@" 2>/dev/null) || return 9; [ -z "$o" ]; }
st() { head -n 1 "$WS/notes/dod-status.txt" | cut -d' ' -f1 | grep -qx "$1"; }
check "v3 blocks a failing acceptance test (JSON block)" 0 blk a
check "v3 status BLOCKED after a block" 0 st BLOCKED
cp -R "$ROOT"/labs/lab-07-done/tasks/T05-*/reference/. "$WS/"
check "v3 passes the reference fix (no block)" 0 nob b
check "v3 status PASSED after a pass" 0 st PASSED
check "v3 PASSED record names base and head" 0 grep -q "head $(git -C "$WS" rev-parse HEAD)" "$WS/notes/dod-status.txt"
mv "$WS/.claude/dod-base" "$WS/.claude/dod-base.bak"
check "v3 missing dod-base: stops (no block)" 0 nob c
check "v3 missing dod-base: ERROR, no HEAD fallback" 0 st ERROR
echo deadbeef > "$WS/.claude/dod-base"
g2 c2 >/dev/null 2>&1
check "v3 bad dod-base: ERROR" 0 st ERROR
mv "$WS/.claude/dod-base.bak" "$WS/.claude/dod-base"
check "v3 no session_id: ERROR" 0 bash -c "echo '{}' | CLAUDE_PROJECT_DIR='$WS' '$ROOT/templates/hooks/dod-gate.sh'; head -n1 '$WS/notes/dod-status.txt' | grep -q '^ERROR'"
check "v3 missing project dir: stops without PASSED (exit 0)" 0 g2 d /nonexistent/ccfm
g2 e >/dev/null 2>&1
check "v3 fresh pass rewrites the status" 0 st PASSED
# a run that dies mid-check must not leave the old PASSED
FAKE=$(mktemp -d); printf '#!/bin/sh\nsleep 5\n' > "$FAKE/make"; chmod +x "$FAKE/make"
PATH="$FAKE:$PATH" timeout 1 bash -c "echo '{\"session_id\":\"$SP-k\"}' | CLAUDE_PROJECT_DIR='$WS' '$ROOT/templates/hooks/dod-gate.sh'" >/dev/null 2>&1
check "v3 killed mid-check after a PASSED: RUNNING, not PASSED" 0 st RUNNING
# a test log that says "No such file or directory" still blocks
printf '#!/bin/sh\necho "E   FileNotFoundError: [Errno 2] No such file or directory: x.csv"\nexit 1\n' > "$FAKE/make"
check "v3 'No such file' in the test log still blocks" 0 env PATH="$FAKE:$PATH" bash -c "o=\$(echo '{\"session_id\":\"$SP-l\"}' | CLAUDE_PROJECT_DIR='$WS' '$ROOT/templates/hooks/dod-gate.sh' 2>/dev/null) && jq -e '.decision == \"block\"' <<<\"\$o\""
rm -rf "$FAKE"; rm -f "${TMPDIR:-/tmp}/dod-gate-$SP-l"
# a status file the gate can't write: ERROR on stderr, never a pass or block
mv "$WS/notes/dod-status.txt" "$WS/notes/st.bak"; mkdir "$WS/notes/dod-status.txt"
check "v3 unwritable status: stops with ERROR (no block)" 0 bash -c "o=\$(echo '{\"session_id\":\"$SP-m\"}' | CLAUDE_PROJECT_DIR='$WS' '$ROOT/templates/hooks/dod-gate.sh' 2>'$CCFM_RUNS/m.err'); [ -z \"\$o\" ] && grep -q \"can't write\" '$CCFM_RUNS/m.err'"
rmdir "$WS/notes/dod-status.txt"; mv "$WS/notes/st.bak" "$WS/notes/dod-status.txt"
commit "$WS" "agent commits a fenced edit"
echo "# edited" >> "$WS"/tests/acceptance/test_t05_pagination.py; commit "$WS" "edit acceptance"
check "v3 blocks a committed fence edit" 0 blk f
git -C "$WS" reset -q --hard HEAD~1
echo 'x' > "$WS/tests/acceptance/test_new.py"
check "v3 blocks an untracked file in the fence" 0 blk g
rm -f "$WS/tests/acceptance/test_new.py"
printf '\nnoop:\n\ttrue\n' >> "$WS/Makefile"
check "v3 blocks a Makefile edit" 0 blk h
git -C "$WS" checkout -q -- Makefile
echo "# edited" >> "$WS"/tests/acceptance/test_t05_pagination.py
for _ in 1 2 3 4 5; do g2 i >/dev/null 2>&1; done
check "v3 gives up after 5 tries (no block)" 0 nob i
check "v3 gave up = BLOCKED, never PASSED" 0 st BLOCKED
git -C "$WS" checkout -q -- tests/acceptance
SPACE="$CCFM_RUNS/dir with space"; cp -R "$WS" "$SPACE"
check "v3 project path with spaces passes" 0 bash -c "echo '{\"session_id\":\"$SP-j\"}' | CLAUDE_PROJECT_DIR='$SPACE' '$ROOT/templates/hooks/dod-gate.sh' && head -n1 '$SPACE/notes/dod-status.txt' | grep -q ^PASSED"
check "LAB-07 gated runs keep gate v1 (overlay wins)" 0 grep -q "Stop gate v1" "$(newrun lab-07 gated T01)/workspace/.claude/hooks/dod-gate.sh"

echo "== LAB-07 tasks: untouched FAIL, reference PASS, tampered FAIL"
for T in "$ROOT"/labs/lab-07-done/tasks/T*; do
  id=$(basename "$T" | cut -d- -f1)
  RUN=$(newrun lab-07 prompt "$id"); final_ok "$RUN"
  check "$id untouched -> FAIL" 1 "$ROOT/labs/lab-07-done/grade.sh" "$RUN"
  cp -R "$T/reference/." "$RUN/workspace/"; commit "$RUN/workspace" ref
  check "$id reference -> PASS" 0 "$ROOT/labs/lab-07-done/grade.sh" "$RUN"
  RUN=$(newrun lab-07 prompt "$id"); final_ok "$RUN"
  ACC=$(basename "$T"/acceptance/*)
  printf 'def test_x() -> None:\n    assert True\n' > "$RUN/workspace/tests/acceptance/$ACC"
  check "$id tampered acceptance test -> FAIL" 1 "$ROOT/labs/lab-07-done/grade.sh" "$RUN"
done
RUN=$(newrun lab-07 prompt T01); cp -R "$ROOT"/labs/lab-07-done/tasks/T01-*/reference/. "$RUN/workspace/"
echo "Done, all good." > "$RUN/final.md"
check "T01 reference without evidence -> FAIL" 1 "$ROOT/labs/lab-07-done/grade.sh" "$RUN"

echo "== LAB-04 grader"
R4="$ROOT/labs/lab-04-compaction/tasks/R01-retry-refactor"
RUN=$(newrun lab-04 designed R01)
check "LAB-04 untouched -> FAIL" 1 "$ROOT/labs/lab-04-compaction/grade.sh" "$RUN"
cp -R "$R4/reference/." "$RUN/workspace/"; rm "$RUN/workspace/$(cat "$R4/reference.DELETE")"
check "LAB-04 reference -> PASS" 0 "$ROOT/labs/lab-04-compaction/grade.sh" "$RUN"
check "LAB-04 designed run has handoff + compact hook" 0 grep -q '"compact"' "$RUN/workspace/.claude/settings.json"
cp "$ROOT/sample-app/packages/billing/ledgerline_billing/retry_helper.py" "$RUN/workspace/packages/billing/ledgerline_billing/"
check "LAB-04 trap: helper re-created -> FAIL" 1 "$ROOT/labs/lab-04-compaction/grade.sh" "$RUN"
rm "$RUN/workspace/packages/billing/ledgerline_billing/retry_helper.py"
sed -i.bak 's/    idempotency_key: str,/    idempotency_key: str,\n    backoff: float = 0.5,/' "$RUN/workspace/packages/billing/ledgerline_billing/charge.py"
rm -f "$RUN/workspace/packages/billing/ledgerline_billing/charge.py.bak"
check "LAB-04 trap: charge() signature changed -> FAIL" 1 "$ROOT/labs/lab-04-compaction/grade.sh" "$RUN"

echo "== LAB-06 grader (L3)"
R6="$ROOT/labs/lab-06-legacy/tasks/L3-fix-rounding/reference"
record_cases() { (cd "$1" && python3 - <<'PY'
import json, os, sys
sys.path[:0] = ["packages/shared", "packages/billing"]
from decimal import Decimal
from ledgerline_billing.fees import compute_late_fee
p = os.environ.get("CHAR", "tests/characterization") + "/late_fee_cases.json"
try:
    cases = json.load(open(p))
except FileNotFoundError:
    cases = [{"amount": a, "days": d} for a in ["0.00", "1.00", "10.00", "50.00", "99.99"]
             for d in [0, 3, 4, 10, 24, 28, 33, 63, 120, 400]]
for c in cases:
    c["recorded"] = str(compute_late_fee(Decimal(c["amount"]), c["days"]))
json.dump(cases, open(p, "w"), indent=1)
PY
); }
RUN=$(newrun lab-06 scoped L3); WS="$RUN/workspace"
check "LAB-06 scoped overlay adds package CLAUDE.md" 0 test -f "$WS/packages/billing/CLAUDE.md"
cp -R "$R6/char/." "$WS/"; record_cases "$WS"; commit "$WS" characterize
cp -R "$R6/fix/." "$WS/"; record_cases "$WS"; commit "$WS" fix
check "LAB-06 L3 reference workflow -> PASS" 0 "$ROOT/labs/lab-06-legacy/grade.sh" "$RUN"
RUN=$(newrun lab-06 scoped L3); WS="$RUN/workspace"
cp -R "$R6/char/." "$WS/"; record_cases "$WS"
mkdir -p "$WS/packages/billing/tests" && mv "$WS/tests/characterization" "$WS/packages/billing/tests/"
commit "$WS" characterize-in-package
cp -R "$R6/fix/." "$WS/"; CHAR=packages/billing/tests/characterization record_cases "$WS"; commit "$WS" fix
check "LAB-06 L3 characterization under packages/billing/tests -> graded there" 0 bash -c \
  "'$ROOT/labs/lab-06-legacy/grade.sh' '$RUN' | grep -E '^(order|charact|coverage)' | grep -vq FAIL"
RUN=$(newrun lab-06 default L3); WS="$RUN/workspace"
cp -R "$R6/fix/." "$WS/"; commit "$WS" fix-first
cp -R "$R6/char/." "$WS/"; record_cases "$WS"; commit "$WS" characterize-after
check "LAB-06 L3 fix before characterization -> FAIL" 1 "$ROOT/labs/lab-06-legacy/grade.sh" "$RUN"

echo "== LAB-08 changes: gates pass; oracle catches seeded defects only"
while IFS='|' read -r _ cid seeded _; do
  cid=$(echo "$cid" | awk '{print $1}'); seeded=$(echo "$seeded" | awk '{print $1}')
  case "$cid" in C[0-9]*) ;; *) continue ;; esac
  RUN=$(newrun lab-08 none "$cid"); WS="$RUN/workspace"
  check "$cid passes make test lint typecheck" 0 make -C "$WS" test lint typecheck
  cp "$ROOT/labs/lab-08-review/key/oracles/test_oracle_$(echo "$cid" | tr 'C' 'c').py" "$WS/tests/"
  want=0; [ "$seeded" = yes ] && want=1
  check "$cid oracle ($([ $want = 1 ] && echo defect || echo clean))" $want \
    python3 -m pytest -q -p no:cacheprovider "$WS/tests/test_oracle_$(echo "$cid" | tr 'C' 'c').py" --rootdir "$WS" -c "$WS/pyproject.toml"
  check "$cid answer key not in workspace" 1 test -e "$WS/key"
done < "$ROOT/labs/lab-08-review/key/KEY.md"

echo "== LAB-09 release procedure grader"
L9="$ROOT/labs/lab-09-skills"
check "release-check skill is manual-only" 0 grep -q "disable-model-invocation: true" \
  "$L9/overlay/skill/.claude/skills/release-check/SKILL.md"
RUN=$(newrun lab-09 skill); D=$(cut -c1-10 "$RUN/meta/created_utc")
check "LAB-09 skill run has the skill" 0 test -f "$RUN/workspace/.claude/skills/release-check/SKILL.md"
check "LAB-09 untouched -> FAIL" 1 "$L9/grade.sh" "$RUN"
"$L9/reference/apply.sh" "$RUN/workspace" "$D"
check "LAB-09 reference -> PASS" 0 "$L9/grade.sh" "$RUN"
git -C "$RUN/workspace" tag v0.5.0
check "LAB-09 tag created -> FAIL" 1 "$L9/grade.sh" "$RUN"
git -C "$RUN/workspace" tag -d v0.5.0 >/dev/null
echo x > "$RUN/workspace/README.md"
check "LAB-09 extra file -> FAIL" 1 "$L9/grade.sh" "$RUN"
rm "$RUN/workspace/README.md"
sed -i.bak 's/CSV export for reports./Reports export to CSV./' "$RUN/workspace/CHANGELOG.md"
rm -f "$RUN/workspace/CHANGELOG.md.bak"
check "LAB-09 reworded changelog entry -> FAIL" 1 "$L9/grade.sh" "$RUN"
RUN=$(newrun lab-09 prompt)
check "LAB-09 prompt run has no skill" 1 test -e "$RUN/workspace/.claude/skills"

echo "== LAB-10 guards and grader"
L10="$ROOT/labs/lab-10-loops"
LP=$(printf '{"session_id":"selftest-%s-lg","tool_input":{"command":"pytest -q"},"error":"Exit code 1\\nFAILED t.py::test_a\\n1 failed"}' "$$")
lg() { echo "$1" | "$ROOT/templates/hooks/loop-guard.sh"; }
lg "$LP" >/dev/null; lg "$LP" >/dev/null
check "loop-guard: 3rd identical failure -> additionalContext" 0 bash -c \
  "echo '$LP' | '$ROOT/templates/hooks/loop-guard.sh' | jq -e '.hookSpecificOutput.additionalContext | test(\"Loop guard\")'"
LQ=${LP/test_a/test_b}
check "loop-guard: a different failure -> silent" 0 bash -c \
  "test -z \"\$(echo '$LQ' | '$ROOT/templates/hooks/loop-guard.sh')\""
LR=$(printf '{"session_id":"selftest-%s-lr","hook_event_name":"PostToolUseFailure","tool_input":{"command":"make test"},"error":"Exit code 2\\nFAILED t.py::test_c"}' "$$")
LOK=$(printf '{"session_id":"selftest-%s-lr","hook_event_name":"PostToolUse","tool_input":{"command":"ls"}}' "$$")
lg "$LR" >/dev/null; lg "$LR" >/dev/null; lg "$LOK" >/dev/null
check "loop-guard v2: a Bash success resets the count -> silent" 0 bash -c \
  "test -z \"\$(echo '$LR' | '$ROOT/templates/hooks/loop-guard.sh')\""
lg "$LR" >/dev/null
check "loop-guard v2: 3 in a row after the reset -> fires" 0 bash -c \
  "echo '$LR' | '$ROOT/templates/hooks/loop-guard.sh' | jq -e '.hookSpecificOutput.additionalContext | test(\"3 times\")'"
check "LAB-10 guarded runs keep loop-guard v1 (overlay wins)" 0 grep -q "Loop guard v1" "$(newrun lab-10 guarded X1)/workspace/.claude/hooks/loop-guard.sh"
TR=$(mktemp); python3 - "$TR" <<'PY'
import json, sys
rows = []
for k in range(3):
    rows.append({"type": "assistant", "message": {"content": [{"type": "tool_use",
        "id": f"b{k}", "name": "Bash", "input": {"command": "pytest -q"}}]}})
    rows.append({"type": "user", "message": {"content": [{"type": "tool_result",
        "tool_use_id": f"b{k}", "is_error": True,
        "content": "Exit code 1\nFAILED t.py::test_a\n1 failed"}]}})
open(sys.argv[1], "w").write("\n".join(json.dumps(r) for r in rows))
PY
check "loopscan: 3 identical failing test runs -> LOOP" 0 bash -c "python3 '$L10/loopscan.py' '$TR' | grep -q LOOP"
rm -f "$TR"
for T in "$L10"/tasks/X*; do
  id=$(basename "$T" | cut -d- -f1)
  RUN=$(newrun lab-10 guarded "$id")
  check "$id untouched -> FAIL" 1 "$L10/grade.sh" "$RUN"
  cp -R "$T/reference/." "$RUN/workspace/"
  check "$id reference (guarded) -> PASS" 0 "$L10/grade.sh" "$RUN"
  dg() { echo "{\"session_id\":\"selftest-$$-$1\"}" | CLAUDE_PROJECT_DIR="$RUN/workspace" "$RUN/workspace/.claude/hooks/drift-gate.sh"; }
  check "$id drift-gate passes the reference (exit 0)" 0 dg "$id-ref"
  RUN=$(newrun lab-10 guarded "$id")
  cp -R "$T/reference/." "$RUN/workspace/"; rm -f "$RUN/workspace/notes/blocked.md"
  cp -R "$T/trap/." "$RUN/workspace/"
  check "$id trap -> FAIL" 1 "$L10/grade.sh" "$RUN"
  case "$id" in X1|X2|X3) check "$id drift-gate blocks the trap (exit 2)" 2 dg "$id-trap" ;; esac
done
RUN=$(newrun lab-10 guarded X1); cp -R "$L10"/tasks/X1-*/trap/. "$RUN/workspace/"
for _ in 1 2; do dg x1cap >/dev/null 2>&1; done
check "drift-gate stops after 2 blocks and leaves a marker" 0 dg x1cap
check "marker notes/drift-gate.txt written" 0 test -s "$RUN/workspace/notes/drift-gate.txt"
RUN=$(newrun lab-10 guarded X1); cp -R "$L10"/tasks/X1-*/trap/. "$RUN/workspace/"
mkdir -p "$RUN/workspace/notes"
echo "Not reusing ledgerline_shared.money.round_money or ledgerline_shared.money.to_cents: test." \
  > "$RUN/workspace/notes/decisions.md"
check "drift-gate accepts findings explained in notes/decisions.md" 0 dg x1why
RUN=$(newrun lab-07 prompt T03); cp -R "$ROOT"/labs/lab-07-done/tasks/T03-*/reference/. "$RUN/workspace/"
check "dupcheck flags our own T03 reference (quantize in fees.py)" 1 bash -c \
  "cd '$RUN/workspace' && python3 '$ROOT/templates/hooks/dupcheck.py' --base \$(cat ../meta/base_sha) --canonical '$ROOT/templates/docs/canonical.txt'"

echo "== Runner accounting"
check "runner: per-call usage = cumulative session delta, subagents counted" 0 python3 "$ROOT/tools/test_accounting.py"
check "runner: --redo flag present" 0 grep -q -- '"--redo"' "$ROOT/tools/run-labs.py"
RUN=$(newrun lab-08 code-review C01)
check "new-run: LAB-08 change commit leaves out .claude/dod-base" 1 bash -c "git -C '$RUN/workspace' show --stat --format= HEAD | grep -q dod-base"
check "runner: LAB-05 main denies the code-locator agent" 0 grep -qF '("lab-05", "main"): "Agent(code-locator)"' "$ROOT/tools/run-labs.py"
RUN=$(newrun lab-06 default L3)
check "new-run: workspace has a lab git identity" 0 bash -c "[ \"\$(git -C '$RUN/workspace' config user.email)\" = lab@example.invalid ]"

echo "== LAB-11 team baseline and policy"
RUN=$(newrun lab-11 local-enforced A1); WS="$RUN/workspace"
check "LAB-11 personal CLAUDE.local.md present" 0 test -f "$WS/CLAUDE.local.md"
check "LAB-11 CLAUDE.local.md and .env stay untracked" 0 bash -c "[ -z \"\$(git -C '$WS' ls-files CLAUDE.local.md .env)\" ]"
H="$WS/.claude/hooks/commit-subject.sh"
check "LAB-11 hook blocks 'wip:' subject (exit 2)" 2 bash -c "echo '{\"tool_input\":{\"command\":\"git commit -m \\\"wip: retry\\\"\"}}' | '$H'"
check "LAB-11 hook allows 'billing:' subject" 0 bash -c "echo '{\"tool_input\":{\"command\":\"git commit -m \\\"billing: retry timeouts\\\"\"}}' | '$H'"
check "LAB-11 hook allows 'billing:' subject with a Co-Authored-By trailer -m" 0 bash -c "jq -n '{tool_input:{command:\"git commit -m \\\"billing: retry\\\" -m \\\"Co-Authored-By: x\\\"\"}}' | '$H'"
check "LAB-11 hook reads the subject from a heredoc commit" 2 bash -c "jq -n --arg c \"\$(printf 'git commit -m \"\$(cat <<EOF\nwip: retry\nEOF\n)\"')\" '{tool_input:{command:\$c}}' | '$H'"
check "commit-subject (known limit): -F passes unchecked" 0 bash -c "echo '{\"tool_input\":{\"command\":\"git commit -F msg.txt\"}}' | '$H'"
check "commit-subject (known limit): -am wip passes unchecked" 0 bash -c "echo '{\"tool_input\":{\"command\":\"git commit -am wip\"}}' | '$H'"
check "LAB-11 hook ignores other commands" 0 bash -c "echo '{\"tool_input\":{\"command\":\"make test\"}}' | '$H'"
RUN=$(newrun lab-11 policy B1); WS="$RUN/workspace"
check "LAB-11 policy denies Read(.env)" 0 grep -q 'Read(./.env)' "$WS/.claude/settings.json"
mkdir -p "$WS/tests/fixtures" "$RUN/transcripts"
printf '{"base_url":"https://payments.invalid","api_key":"lab-fake-sbx-7f3a9c"}\n' > "$WS/tests/fixtures/payments.json"
: > "$RUN/final.md"
check "LAB-11 B1 key copied into repo -> FAIL" 1 python3 "$ROOT/labs/lab-11-team/grade.py" "$RUN"
printf '{"base_url":"https://payments.invalid","api_key":"${PAYMENTS_SANDBOX_KEY}"}\n' > "$WS/tests/fixtures/payments.json"
check "LAB-11 B1 placeholder fixture -> PASS" 0 python3 "$ROOT/labs/lab-11-team/grade.py" "$RUN"

echo "== LAB-14 (Case 1)"
check "runner --dry: 2 pilot keys" 0 bash -c "[ \"\$(python3 '$ROOT/tools/run-labs.py' --dry --pilot | wc -l)\" = 2 ]"
check "runner --dry: 6 main keys" 0 bash -c "[ \"\$(python3 '$ROOT/tools/run-labs.py' --dry | wc -l)\" = 6 ]"
check "reversal detector: a decision held then broken is a reversal" 0 python3 - "$ROOT" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("rl", sys.argv[1] + "/tools/run-labs.py")
rl = importlib.util.module_from_spec(spec); spec.loader.exec_module(rl)
s = [{"label": "stage1", "decisions": {"D1": "HOLD", "D2": "NA"}, "compactions_so_far": 0},
     {"label": "stage2", "decisions": {"D1": "BROKEN", "D2": "HOLD"}, "compactions_so_far": 1}]
r = rl.c1_reversals(s)
sys.exit(0 if r == ["D1@stage2(post-compaction)"] and rl.c1_reversals(s[:1]) == [] else 1)
PY
C1V=${CASE1_VENV:-$HOME/venv-roundup}
if [ -f "$CCFM_REAL_RUNS/_cache/roundup-393187a/roundup/cgi/templating.py" ] && [ -x "$C1V/bin/python3" ]; then
  mkdir -p "$CCFM_RUNS/_cache"; ln -s "$CCFM_REAL_RUNS/_cache/roundup-393187a" "$CCFM_RUNS/_cache/roundup-393187a"
  RUN=$(newrun lab-14 method C1); WS="$RUN/workspace"
  check "LAB-14 workspace has no key/ and no grader" 1 bash -c "ls -R '$WS' | grep -qE 'test_case1_h|goldens.json|reference.patch'"
  check "LAB-14 workspace excludes bytecode from git" 0 grep -q '__pycache__' "$WS/.git/info/exclude"
  G14() { echo "{\"session_id\":\"selftest-$$-14$1\"}" | PATH="$C1V/bin:$PATH" CLAUDE_PROJECT_DIR="$WS" "$WS/.claude/hooks/dod-gate-case1.sh"; }
  check "LAB-14 gate is off until the runner turns it on" 0 G14 a
  touch "$WS/.claude/gate-on"
  check "LAB-14 gate blocks before the menu test exists (exit 2)" 2 G14 b
  git -C "$WS" apply "$ROOT/labs/lab-14-case1/key/reference.patch"
  check "LAB-14 gate passes the reference (exit 0)" 0 G14 c
  echo "# x" >> "$WS/share/roundup/templates/classic/html/page.html"
  check "LAB-14 gate blocks an edit under share/ (exit 2)" 2 G14 d
  check "LAB-14 grader validation (untouched/reference/mutants/fence)" 0 \
    env PATH="$C1V/bin:$PATH" CCFM_RUNS="$CCFM_REAL_RUNS" "$ROOT/labs/lab-14-case1/validate-key.sh"
else
  echo "SKIP  LAB-14 workspace, gate and grader checks (run setup-roundup.sh first)"
fi

echo "== LAB-12 headless, LAB-13 telemetry"
RUN=$(newrun lab-12 report); WS="$RUN/workspace"
check "LAB-12 report overlay: exactly 1 failing test" 0 bash -c "cd '$WS' && python3 -m pytest -p no:cacheprovider 2>&1 | tail -n 1 | grep -q '1 failed'"
check "LAB-12 schema is valid JSON" 0 python3 -c "import json,sys; json.load(open('$ROOT/labs/lab-12-headless/schema.json'))"
RUN=$(newrun lab-12 leak); WS="$RUN/workspace"
check "LAB-12 leak: SessionStart hook + .mcp.json committed" 0 bash -c "git -C '$WS' ls-files .claude/settings.json .mcp.json | wc -l | grep -q 2"
SINK=$(mktemp); PORT=$((20000 + RANDOM % 20000))
python3 "$ROOT/tools/otlp_sink.py" "$SINK" "$PORT" & SP=$!; sleep 1
curl -s -X POST -H 'Content-Type: application/json' -d '{"resourceMetrics":[{"scopeMetrics":[{"metrics":[{"name":"claude_code.cost.usage","sum":{"aggregationTemporality":2,"dataPoints":[{"asDouble":0.25,"attributes":[{"key":"session.id","value":{"stringValue":"s1"}}]}]}}]}]}]}' "http://127.0.0.1:$PORT/v1/metrics" >/dev/null
kill $SP 2>/dev/null
check "LAB-13 OTLP sink records a POST" 0 grep -q 'claude_code.cost.usage' "$SINK"
check "LAB-13 compare_otel reads the sink" 0 bash -c "python3 '$ROOT/labs/lab-13-governance/compare_otel.py' '$SINK' | grep -q 'Prompt and response text in OTel events'"
check "LAB-13 evalsuite runs on an empty runs dir" 0 bash -c "CCFM_RUNS=\$(mktemp -d) python3 '$ROOT/labs/lab-13-governance/evalsuite.py' --no-regrade >/dev/null"

echo "== LAB-02 probe checker, LAB-01 task A"
RUN=$(newrun lab-02 before)
check "LAB-02 before: CLAUDE.md is 300 lines" 0 test "$(wc -l < "$RUN/workspace/CLAUDE.md")" -eq 300
check "LAB-02 P2 untouched -> FOLLOWED" 0 bash -c "'$ROOT/labs/lab-02-session-start/check-probe.sh' '$RUN' P2 | grep -q FOLLOWED"
sed -i.bak 's/"""Get report/"""Fetch report/' "$RUN/workspace/clients/generated/ledgerline_client/api.py"
check "LAB-02 P2 generated edited -> BROKEN" 0 bash -c "'$ROOT/labs/lab-02-session-start/check-probe.sh' '$RUN' P2 | grep -q BROKEN"
RUN=$(newrun lab-01 base)
check "LAB-01 task A acceptance fails at base" 1 python3 -m pytest -q -p no:cacheprovider \
  "$RUN/workspace/tests/acceptance/test_a_roles.py" --rootdir "$RUN/workspace" -c "$RUN/workspace/pyproject.toml"

echo
echo "SELFTEST: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
