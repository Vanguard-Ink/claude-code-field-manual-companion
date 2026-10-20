#!/bin/bash
# Loop guard v2. PostToolUseFailure (Bash): the same
# command failing the same way 3 times, with no Bash
# success in between, means a loop. Say so.
# PostToolUse (Bash): a success resets the count.
IN=$(cat)
SID=$(jq -r '.session_id' <<< "$IN")
S="${TMPDIR:-/tmp}/loop-guard-$SID"
EV=$(jq -r '.hook_event_name // ""' <<< "$IN")
[ "$EV" = PostToolUse ] && { rm -f "$S"; exit 0; }
CMD=$(jq -r '.tool_input.command // ""' <<< "$IN")
# Signature: command + exit line + failing test ids.
ERR=$(jq -r '.error // ""' <<< "$IN")
SIG=$( { echo "$CMD"; head -n 1 <<< "$ERR";
  grep -oE '^(FAILED|ERROR) [^ ]+' <<< "$ERR" | sort
} | cksum)
{ read -r LAST N < "$S"; } 2>/dev/null || N=0
[ "$LAST" = "${SIG// /_}" ] && N=$((N + 1)) || N=1
echo "${SIG// /_} $N" > "$S"
[ "$N" -lt 3 ] && exit 0
jq -n --arg c "$CMD" --arg n "$N" '{hookSpecificOutput: {
  hookEventName: "PostToolUseFailure",
  additionalContext: ("Loop guard: `" + $c + "` failed"
  + " the same way " + $n + " times in a row. Stop"
  + " editing. Write notes/blocked.md: what you tried,"
  + " the failing output, two hypotheses. Then stop.")}}'
