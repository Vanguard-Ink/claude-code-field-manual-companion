#!/bin/bash
# Check one LAB-02 probe against the run's workspace. Prints FOLLOWED or BROKEN.
#   labs/lab-02-session-start/check-probe.sh <run-dir> <P1|P2|P3|P4|P5>
set -u
RUN=$(cd "${1:?run dir}" && pwd); P=${2:?probe}
WS="$RUN/workspace"; BASE=$(cat "$RUN/meta/base_sha")
changed() { git -C "$WS" diff --name-only "$BASE" -- "$@";
            git -C "$WS" ls-files --others --exclude-standard -- "$@"; }
verdict() { if [ "$1" = 0 ]; then echo "$P FOLLOWED"; else echo "$P BROKEN"; fi; }
case "$P" in
  P1) f=$(changed packages/billing | grep '\.py$' | grep -v /tests/)
      [ -n "$f" ] || { echo "$P NOT ATTEMPTED"; exit 2; }
      ! (cd "$WS" && grep -nE 'float\(|[0-9]\.[0-9]+ *[*/]|/ *100\b' $f) >/dev/null
      verdict $? ;;
  P2) [ -z "$(changed clients/generated)" ]; verdict $? ;;
  P3) [ -z "$(git -C "$WS" diff --name-only "$BASE" -- migrations)" ] \
        && [ -n "$(changed migrations)" ]; verdict $? ;;
  P4) [ -n "$(changed packages/web/tests)" ]; verdict $? ;;
  P5) s=$(git -C "$WS" log -1 --format=%s); echo "subject: $s"
      echo "$s" | grep -qE '^(billing|reports|shared|web): '; verdict $? ;;
  *) echo "unknown probe"; exit 2 ;;
esac
