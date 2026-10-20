#!/bin/bash
# Create an isolated lab run: a fresh copy of sample-app in its own git repo.
#   tools/new-run.sh <lab> <variant> [task-or-change]
#   e.g. tools/new-run.sh lab-07 gated T01
# Runs live in $CCFM_RUNS (default: ~/ccfm-runs). Graders and answer keys
# stay in this repository and are never copied into the workspace.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
LAB=${1:?lab, e.g. lab-07}; VARIANT=${2:?variant}; ITEM=${3:-}
RUNS=${CCFM_RUNS:-$HOME/ccfm-runs}
STAMP=$(date +%Y%m%d-%H%M%S)-$$
RUN="$RUNS/$LAB-${ITEM:+$ITEM-}$VARIANT-$STAMP"
WS="$RUN/workspace"; META="$RUN/meta"
LABDIR=$(ls -d "$ROOT"/labs/"$LAB"-* | head -n 1)
mkdir -p "$WS" "$META"
if [ "$LAB" = lab-14 ]; then  # Case 1: pinned Roundup tree, see setup-roundup.sh
  SRC="$RUNS/_cache/roundup-393187a"
  [ -f "$SRC/roundup/cgi/templating.py" ] \
    || { echo "run labs/lab-14-case1/setup-roundup.sh first" >&2; exit 1; }
  cp -R "$SRC/." "$WS/"
else
  cp -R "$ROOT/sample-app/." "$WS/"
fi
rm -rf "$WS"/.pytest_cache "$WS"/.mypy_cache "$WS"/.ruff_cache
find "$WS" -name __pycache__ -type d -prune -exec rm -rf {} +

overlay() {  # copy a directory's contents over the workspace
  [ -d "$1" ] && cp -R "$1/." "$WS/"
  rm -f "$WS/.keep"
  return 0
}

# Lab-level files shared by every variant, then the variant overlay.
# A variant like "enforced-A" also gets overlay/enforced (team part) first.
overlay "$LABDIR/overlay/common"
[ "${VARIANT%-*}" != "$VARIANT" ] && overlay "$LABDIR/overlay/${VARIANT%-*}"
overlay "$LABDIR/overlay/$VARIANT"
# Fixture env files ship as "dot-env" so the repository never commits a .env;
# the workspace gets the real name (LAB-11 needs a gitignored .env).
[ -f "$WS/dot-env" ] && mv "$WS/dot-env" "$WS/.env"

# Task material (LAB-04, 06, 07, 10): DONE.md, TASK.md, acceptance tests.
if [ -n "$ITEM" ] && [ -d "$LABDIR/tasks" ]; then
  TDIR=$(ls -d "$LABDIR"/tasks/"$ITEM"* | head -n 1)
  mkdir -p "$WS/tasks/$(basename "$TDIR")"
  cp "$TDIR"/TASK.md "$TDIR"/DONE.md "$WS/tasks/$(basename "$TDIR")/"
  [ -d "$TDIR/acceptance" ] && cp "$TDIR"/acceptance/* "$WS/tests/acceptance/"
  echo "$TDIR" > "$META/task_dir"
fi

# Variants with hooks get the template hook files their settings name.
if [ -f "$WS/.claude/settings.json" ]; then
  HOOKS=$(grep -oE '\.claude/hooks/[A-Za-z0-9_.-]+' "$WS/.claude/settings.json" \
    | sed 's#.*/##' | sort -u || true)
  if [ -n "$HOOKS" ]; then
    mkdir -p "$WS/.claude/hooks"
    for h in $HOOKS; do  # overlay copies win; else take the template
      [ -e "$WS/.claude/hooks/$h" ] || [ ! -e "$ROOT/templates/hooks/$h" ] \
        || cp "$ROOT/templates/hooks/$h" "$WS/.claude/hooks/"
    done
    if echo "$HOOKS" | grep -q drift-gate; then
      cp "$ROOT/templates/hooks/dupcheck.py" "$WS/.claude/hooks/"
      cp "$ROOT/templates/docs/canonical.txt" "$WS/.claude/canonical.txt"
    fi
    chmod +x "$WS"/.claude/hooks/*
  fi
fi

git -C "$WS" init -q
# Roundup has no .gitignore for bytecode; keep it out of fence checks.
[ "$LAB" = lab-14 ] && printf '__pycache__/\n*.pyc\n.pytest_cache/\n' \
  >> "$WS/.git/info/exclude"
# A local identity so agents can commit (LAB-02 P5, LAB-06 L3) without
# reaching for the user's own name or email.
git -C "$WS" config user.name "Lab Agent"
git -C "$WS" config user.email "lab@example.invalid"
git -C "$WS" add -A
git -C "$WS" -c user.name=lab -c user.email=lab@example.invalid \
  commit -q -m "lab base: $LAB $VARIANT $ITEM"
git -C "$WS" rev-parse HEAD > "$META/base_sha"

# Untracked, per-developer files (LAB-11): CLAUDE.local.md, a local .env.
# They land after the base commit and stay out of git, as on a real laptop.
# "enforced-A" gets local/A (the developer) and local/enforced-A if present.
for d in "$LABDIR/local/${VARIANT##*-}" "$LABDIR/local/$VARIANT"; do
  [ -d "$d" ] || continue
  [ "$d" = "$LABDIR/local/$VARIANT" ] && [ "${VARIANT##*-}" = "$VARIANT" ] \
    && [ -n "${DONE_LOCAL:-}" ] && continue
  DONE_LOCAL=1
  cp -R "$d/." "$WS/"
  (cd "$d" && find . -type f | sed 's#^\./#/#') >> "$WS/.git/info/exclude"
done
cp "$META/base_sha" "$WS/.claude/dod-base" 2>/dev/null \
  || { mkdir -p "$WS/.claude"; cp "$META/base_sha" "$WS/.claude/dod-base"; }

# LAB-08: apply the change under review as a second commit.
if [ -n "$ITEM" ] && [ -d "$LABDIR/changes" ]; then
  CDIR=$(ls -d "$LABDIR"/changes/"$ITEM"* | head -n 1)
  cp -R "$CDIR/files/." "$WS/"
  mkdir -p "$WS/tasks/$(basename "$CDIR")"
  cp "$CDIR/DONE.md" "$WS/tasks/$(basename "$CDIR")/"
  # DONE.md goes in the change commit, like a PR description. The harness's
  # .claude/dod-base does not: reviewers flagged it as noise in the diff.
  git -C "$WS" add -A -- . ':(exclude).claude/dod-base'
  git -C "$WS" -c user.name=lab -c user.email=lab@example.invalid \
    commit -q -m "change $(basename "$CDIR")"
  echo "$CDIR" > "$META/change_dir"
fi

printf '%s\n' "$LAB" > "$META/lab"
printf '%s\n' "$VARIANT" > "$META/variant"
printf '%s\n' "$ITEM" > "$META/item"
date -u +%FT%TZ > "$META/created_utc"
cat <<MSG
Run created: $RUN
  1. cd "$WS"   (activate your venv first: see labs/README.md)
  2. claude     (fresh session; follow $(basename "$LABDIR")/README.md)
  3. Save Claude's final message to: $RUN/final.md
  4. Grade (labs with a grader): $LABDIR/grade.sh "$RUN"
MSG
