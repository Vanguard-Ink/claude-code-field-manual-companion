#!/bin/bash
# Zip finished lab runs (transcripts, grades, CSVs) for the book's writer.
#   SCRUB_EMAIL=you@example.com tools/pack-results.sh <destination-folder>
# Leaves out the runner's private Claude Code config (login data) and
# LAB-14's cached Roundup tree. With SCRUB_EMAIL set, the zip is made from a
# copy with that address, your login name in paths, and OTel account IDs
# replaced, and without tool caches (Chapter 15's privacy rule).
set -eu
DEST=${1:?destination folder}
RUNS=${CCFM_RUNS:-$HOME/ccfm-runs}
OUT="$DEST/lab-runs-$(date -u +%Y%m%dT%H%MZ).zip"
SRC="$RUNS"
if [ -n "${SCRUB_EMAIL:-}" ]; then
  T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
  (cd "$RUNS" && tar -cf - --exclude=./_claude-config --exclude=./_cache \
    --exclude='*/grade-ws' --exclude='*/.mypy_cache' --exclude='*/.ruff_cache' \
    --exclude='*/.hypothesis' --exclude='*/__pycache__' \
    --exclude='*/.pytest_cache' .) | tar -xf - -C "$T"
  python3 "$(dirname "$0")/scrub-email.py" "$T" "$SCRUB_EMAIL" --user "$(id -un)" \
    --host "$(hostname)"
  if grep -rqiF -e "$SCRUB_EMAIL" -e "/home/$(id -un)/" \
    -e "$(id -un)@" -e "$(hostname)" "$T"; then
    echo "scrub incomplete: address still present; not packing" >&2; exit 1
  fi
  SRC="$T"
else
  echo "warning: SCRUB_EMAIL not set; transcripts may hold your email" >&2
fi
(cd "$SRC" && zip -qr "$OUT" . -x '_claude-config/*' -x '_cache/*' \
  -x '*/grade-ws/*')
echo "Wrote $OUT"
