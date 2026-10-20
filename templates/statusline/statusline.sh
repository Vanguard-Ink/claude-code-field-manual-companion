#!/bin/bash
# Reads session JSON on stdin; prints one line.
input=$(cat)
model=$(echo "$input" | jq -r '.model.display_name')
pct=$(echo "$input" \
  | jq -r '.context_window.used_percentage // 0')
echo "[$model] ${pct%.*}% context"
