#!/bin/bash
# Fuller status line: model, effort, context %, cost, cache hit ratio.
# Field names: code.claude.com/docs/en/statusline (verified 2026-10-06).
input=$(cat)
get() { echo "$input" | jq -r "$1"; }
model=$(get '.model.display_name // "?"')
effort=$(get '.effort.level // "-"')
pct=$(get '.context_window.used_percentage // 0')
cost=$(get '.cost.total_cost_usd // 0')
hit=$(get '.prompt_cache.hit_ratio // empty')
warm=$(get '.prompt_cache.warm // empty')
cache="cache -"
if [ -n "$hit" ]; then
  cache="cache $(awk "BEGIN{printf \"%d\", $hit*100}")%"
  [ "$warm" = "false" ] && cache="$cache (cold)"
fi
printf '[%s/%s] %s%% ctx | $%.2f | %s\n' \
  "$model" "$effort" "${pct%.*}" "$cost" "$cache"
