#!/usr/bin/env python3
"""Recount lab usage from stream-json transcripts.

`result` events report `modelUsage` and `total_cost_usd` cumulatively for the
whole session (a --resume continues the count), and include subagents,
/compact and bundled local commands such as /code-review. The top-level
`usage` field covers only the main loop's last turn. So: per session_id,
take the result with the highest cumulative cost; sum those across sessions.
Usage: recount_usage.py <runs-dir> [model] > usage.csv
"""
import csv, glob, json, os, sys, collections

root = sys.argv[1]
MAIN = sys.argv[2] if len(sys.argv) > 2 else "sonnet"  # the --model the labs ran with
w = csv.writer(sys.stdout)
w.writerow(["run", "lab", "sessions", "total_tokens", "main_model_tokens", "other_model_tokens",
            "other_models", "output_tokens", "cache_read", "cost_usd_list", "denials"])
for run in sorted(glob.glob(os.path.join(root, "lab-*"))):
    best, den = {}, 0
    for t in sorted(glob.glob(run + "/transcripts/*.jsonl")):
        for line in open(t, encoding="utf-8", errors="replace"):
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get("type") != "result":
                continue
            den += len(o.get("permission_denials") or [])
            sid = o.get("session_id")
            if sid not in best or (o.get("total_cost_usd") or 0) >= (best[sid].get("total_cost_usd") or 0):
                best[sid] = o
    tot = main = other = out = cr = 0
    cost = 0.0
    others = set()
    for o in best.values():
        cost += o.get("total_cost_usd") or 0
        mu = o.get("modelUsage") or {}
        top = next((m for m in mu if MAIN in m), max(mu, key=lambda m: mu[m]["outputTokens"], default=None))
        for m, v in mu.items():
            n = v["inputTokens"] + v["outputTokens"] + v["cacheReadInputTokens"] + v["cacheCreationInputTokens"]
            tot += n; out += v["outputTokens"]; cr += v["cacheReadInputTokens"]
            if m == top:
                main += n
            else:
                other += n; others.add(m)
    name = os.path.basename(run)
    w.writerow([name, name[:6], len(best), tot, main, other, " ".join(sorted(others)), out, cr, round(cost, 4), den])
