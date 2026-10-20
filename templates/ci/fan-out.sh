#!/usr/bin/env bash
# One capped run per task line, each in its own git
# worktree from a frozen start commit. The script
# decides each outcome itself: exit code, subtype, a
# diff fence against the start, and its own test run.
# Any failed item makes the whole job fail.
set -uo pipefail
: "${ANTHROPIC_API_KEY:?missing: set it in CI}"
TOP=$(git rev-parse --show-toplevel) || exit 1
START=$(git rev-parse --verify "HEAD^{commit}") || exit 1
OUT="$TOP/out/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT" || exit 1
cp tasks.txt "$OUT/manifest.txt" || exit 1
echo "$START" > "$OUT/start.txt" || exit 1
R="$OUT/results.tsv"
printf 'id\tfile\trc\tsubtype\tfence\ttests\tok\n' > "$R"
i=0; bad=0
while IFS= read -r f || [ -n "$f" ]; do
  [ -n "$f" ] || continue
  i=$((i + 1)); id=$(printf '%04d' "$i")
  wt="$OUT/wt-$id"
  git worktree add -q --detach "$wt" "$START" \
    2>/dev/null || { bad=1; printf \
    '%s\t%s\t-\tsetup-error\t-\t-\tno\n' "$id" "$f" \
    >> "$R"; continue; }
  (cd "$wt" && claude --bare -p "Migrate $f to the \
v2 client API. Change only $f, then run ci/test.sh." \
    --permission-mode dontAsk \
    --allowedTools "Read,Edit,Bash(ci/test.sh)" \
    --max-turns 20 --max-budget-usd 2.00 \
    --output-format json) > "$OUT/$id.json" < /dev/null
  rc=$?
  sub=$(jq -r '.subtype // "none"' "$OUT/$id.json" \
    2>/dev/null); sub=${sub:-none}
  # Fence: the final tree against the frozen start, so
  # commits and new files count too. The only change
  # allowed is the task's file. A git error is a fail.
  fence=git-error
  if git -C "$wt" add -A &&
     git -C "$wt" diff --cached "$START" \
       > "$OUT/$id.diff" &&
     names=$(git -C "$wt" diff --cached --name-only \
       "$START"); then
    other=$(grep -vxF -- "$f" <<<"$names")
    fence=ok; [ -z "$other" ] || fence=changed
  fi
  # Tests: the trusted copy, run by this script.
  (cd "$wt" && "$TOP/ci/test.sh") \
    > "$OUT/$id.test.log" 2>&1 && t=pass || t=fail
  ok=no
  [ "$rc" = 0 ] && [ "$sub" = success ] \
    && [ "$fence" = ok ] && [ "$t" = pass ] && ok=yes
  [ "$ok" = yes ] || bad=1
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "$f" \
    "$rc" "$sub" "$fence" "$t" "$ok" >> "$R"
  [ "$ok" = yes ] && git worktree remove --force "$wt"
done < "$OUT/manifest.txt"
cat "$R"
exit "$bad"
