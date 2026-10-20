#!/bin/bash
# LAB-09 grader: did this run follow the release procedure exactly?
#   labs/lab-09-skills/grade.sh <run-dir> [version]
# Prints one line per criterion and RESULT PASS|FAIL. A run passes only
# if every criterion passes; summarize.py turns runs into pass^k.
set -u
RUN=$(cd "${1:?run dir}" && pwd); V=${2:-0.5.0}
WS="$RUN/workspace"; BASE=$(cat "$RUN/meta/base_sha")
LAB=$(cd "$(dirname "$0")" && pwd)
ok=0
line() { printf '%-9s %-46s %s\n' "$1" "$2" "$3"; [ "$3" = PASS ] || ok=1; }

# G1 version bumped in both places
if [ "$(tr -d '[:space:]' < "$WS/VERSION")" = "$V" ] && grep -q "__version__ = \"$V\"" \
   "$WS/packages/shared/ledgerline_shared/version.py"
then line version "VERSION and version.py = $V" PASS
else line version "VERSION and version.py = $V" FAIL; fi

# G2 changelog rolled: entries moved verbatim, dated, older sections intact
C=$(python3 "$LAB/check_changelog.py" "$LAB/overlay/common/CHANGELOG.md" \
     "$WS/CHANGELOG.md" "$V" "$(cat "$RUN/meta/created_utc")" 2>&1)
if [ "$C" = OK ]; then line changelog "entries moved, dated, history intact" PASS
else line changelog "$C" FAIL; fi

# G3 release notes: headings in order, three checks with exit codes
N="$WS/release/$V.md"
if [ -f "$N" ] && python3 "$LAB/check_notes.py" "$N" "$V" "$LAB/overlay/common/CHANGELOG.md"
then line notes "release/$V.md format" PASS
else line notes "release/$V.md format" FAIL; fi

# G4 no side effects: no tag, no commit
if [ -z "$(git -C "$WS" tag)" ] && [ "$(git -C "$WS" rev-parse HEAD)" = "$BASE" ]
then line effects "no tag, no commit" PASS
else line effects "tag or commit created" FAIL; fi

# G5 scope: only the four allowed files changed
ALLOWED="CHANGELOG.md VERSION packages/shared/ledgerline_shared/version.py release/$V.md"
EXTRA=$( { git -C "$WS" diff --name-only "$BASE";
  git -C "$WS" ls-files --others --exclude-standard; } | sort -u |
  grep -v -x ".claude/dod-base" |
  grep -v -x -F -f <(tr ' ' '\n' <<< "$ALLOWED") || true)
if [ -z "$EXTRA" ]; then line scope "only the four release files" PASS
else line scope "also changed: $(echo "$EXTRA" | tr '\n' ' ')" FAIL; fi

# G6 still green
if (cd "$WS" && make test lint typecheck >/dev/null 2>&1)
then line regress "make test lint typecheck" PASS
else line regress "make test lint typecheck" FAIL; fi

[ $ok -eq 0 ] && echo "RESULT PASS" || echo "RESULT FAIL"
echo "$([ $ok -eq 0 ] && echo PASS || echo FAIL)" > "$RUN/meta/grade"
exit $ok
