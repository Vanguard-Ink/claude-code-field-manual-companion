#!/bin/bash
# PostToolUse: lint the edited file; report problems.
F=$(jq -r '.tool_input.file_path // empty')
case "$F" in *.py) ;; *) exit 0 ;; esac
OUT=$(ruff check "$F" 2>&1) && exit 0
jq -n --arg o "$OUT" '{hookSpecificOutput: {
  hookEventName: "PostToolUse",
  additionalContext: ("Lint errors:\n" + $o)}}'
