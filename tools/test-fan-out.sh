#!/bin/bash
# Fixture test for templates/ci/fan-out.sh: a fake `claude`
# plays eleven items; the script must judge each one itself.
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
R="$T/repo"; mkdir -p "$R/ci" "$R/a" "$R/b" "$T/bin"
cp "$ROOT/templates/ci/fan-out.sh" "$ROOT/templates/ci/test.sh" "$R/ci/"
printf 'test:\n\t! grep -rl BROKEN --include=*.py .\n' > "$R/Makefile"
for f in good bad-fence turns broke crash sneaky lock junk last; do echo "v1" > "$R/$f.py"; done
echo v1 > "$R/a/x.py"; echo v1 > "$R/b/x.py"; echo "out/" > "$R/.gitignore"
printf '%s\n' crash.py good.py bad-fence.py turns.py broke.py a/x.py b/x.py sneaky.py lock.py junk.py > "$R/tasks.txt"
printf 'last.py' >> "$R/tasks.txt"   # no final newline
git -C "$R" init -q && git -C "$R" add -A && git -C "$R" -c user.name=t -c user.email=t@t commit -qm base
cat > "$T/bin/claude" <<'STUB'
#!/bin/bash
p=$3; f=$(echo "$p" | sed -E 's/^Migrate ([^ ]+) .*/\1/')
ok='{"type":"result","subtype":"success","is_error":false,"num_turns":3}'
case "$f" in
  crash.py) exit 1 ;;
  good.py|a/x.py|b/x.py) echo v2 > "$f"; echo "$ok" ;;
  bad-fence.py) echo v2 > "$f"; echo "noop:" >> Makefile; echo "$ok" ;;
  turns.py) echo '{"subtype":"error_max_turns","is_error":true}'; exit 1 ;;
  broke.py) echo BROKEN > "$f"; echo "$ok" ;;
  sneaky.py) echo v2 > "$f"; echo "noop:" >> Makefile
     git add -A && git -c user.name=t -c user.email=t@t commit -qm sneak
     echo "$ok" ;;
  lock.py) echo v2 > "$f"; touch "$(git rev-parse --git-dir)/index.lock"; echo "$ok" ;;
  junk.py) echo v2 > "$f"; echo "not json" ;;
  last.py) echo v2 > "$f"; echo "$ok" ;;
esac
STUB
chmod +x "$T/bin/claude"
cd "$R" && PATH="$T/bin:$PATH" ANTHROPIC_API_KEY=x ci/fan-out.sh > "$T/log" 2>&1
rc=$?
RES=$(ls -d "$R"/out/*/results.tsv)
row() { awk -F'\t' -v f="$1" '$2==f{print $3"/"$4"/"$5"/"$6"/"$7}' "$RES"; }
fails=0
expect() { got=$(row "$1"); [ "$got" = "$2" ] || { echo "FAIL $1: got $got want $2"; fails=1; }; }
[ "$rc" = 1 ] || { echo "FAIL job exit $rc, want 1"; fails=1; }
expect crash.py "1/none/ok/pass/no"
expect good.py "0/success/ok/pass/yes"
expect bad-fence.py "0/success/changed/pass/no"
expect turns.py "1/error_max_turns/ok/pass/no"
expect broke.py "0/success/ok/fail/no"
expect a/x.py "0/success/ok/pass/yes"
expect b/x.py "0/success/ok/pass/yes"
expect sneaky.py "0/success/changed/pass/no"
expect lock.py "0/success/git-error/pass/no"
expect junk.py "0/none/ok/pass/no"
expect last.py "0/success/ok/pass/yes"
[ "$(ls "$R"/out/*/*.diff | wc -l)" -ge 10 ] || { echo "FAIL want a diff per item"; fails=1; }
cmp -s "$R/tasks.txt" "$(dirname "$RES")/manifest.txt" || { echo "FAIL manifest"; fails=1; }
[ -d "$(dirname "$RES")/wt-0003" ] || { echo "FAIL failed worktree should be kept"; fails=1; }
[ ! -d "$(dirname "$RES")/wt-0002" ] || { echo "FAIL passed worktree should be removed"; fails=1; }
[ "$fails" = 0 ] || { cat "$T/log"; cat "$RES"; }
exit "$fails"
