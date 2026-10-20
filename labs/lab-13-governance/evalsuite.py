#!/usr/bin/env python3
"""LAB-13 part B: turn finished lab runs into a team eval-suite report. No tokens.

    python3 labs/lab-13-governance/evalsuite.py [--labs lab-07,lab-10] [--no-regrade]

For every finished run of the given labs in $CCFM_RUNS, it does two things:
- It re-runs that lab's grader, so grader fixes apply to old runs. Pass
  --no-regrade to read meta/grade instead.
- It recounts the run's tokens and list-price cost from the transcripts.

It then reports, per task and variant:
- the pass rate,
- pass^k (whether every trial passed),
- median tokens per run,
- cost per passing run.

It also prints a go/no-go line against the thresholds in --gate.
"""
import argparse
import json
import os
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = Path(os.environ.get("CCFM_RUNS", Path.home() / "ccfm-runs"))
ap = argparse.ArgumentParser()
ap.add_argument("--labs", default="lab-07,lab-10")
ap.add_argument("--no-regrade", action="store_true")
ap.add_argument("--gate", default="pass_rate>=0.9,flaky<=1",
                help="go/no-go thresholds for each variant")
args = ap.parse_args()


def usage(run: Path):
    best = {}
    for t in sorted((run / "transcripts").glob("*.jsonl")):
        for ln in t.read_text(errors="replace").splitlines():
            try:
                o = json.loads(ln)
            except ValueError:
                continue
            if o.get("type") == "result":
                sid = o.get("session_id")
                if sid not in best or (o.get("total_cost_usd") or 0) >= (best[sid].get("total_cost_usd") or 0):
                    best[sid] = o
    tok = sum(v["inputTokens"] + v["outputTokens"] + v["cacheReadInputTokens"] + v["cacheCreationInputTokens"]
              for o in best.values() for v in (o.get("modelUsage") or {}).values())
    return tok, sum(o.get("total_cost_usd") or 0 for o in best.values()), bool(best)


cells = defaultdict(list)   # (lab, variant, item) -> [(pass, tokens, cost)]
for lab in args.labs.split(","):
    grader = next((ROOT / "labs").glob(f"{lab}-*/grade.sh"), None)
    for run in sorted(RUNS.glob(f"{lab}-*")):
        meta = run / "meta"
        if not (meta / "variant").exists():
            continue
        tok, cost, has = usage(run)
        if not has:          # interrupted before a result was recorded
            continue
        if grader and not args.no_regrade:
            ok = subprocess.run([str(grader), str(run)], capture_output=True).returncode == 0
        else:
            ok = (meta / "grade").exists() and (meta / "grade").read_text().strip() == "PASS"
        key = (lab, (meta / "variant").read_text().strip(), (meta / "item").read_text().strip())
        cells[key].append((ok, tok, cost))

gate = dict(x.split(">=") if ">=" in x else (x.split("<=")[0], x.split("<=")[1]) for x in args.gate.split(","))
print("| Lab | Variant | Task | Runs | Pass | pass^k | Median tokens | $ per pass |")
print("|---|---|---|---|---|---|---|---|")
summary = defaultdict(lambda: {"runs": 0, "pass": 0, "flaky": 0, "failing": 0})
for (lab, var, item), rs in sorted(cells.items()):
    n, p = len(rs), sum(r[0] for r in rs)
    cost = sum(r[2] for r in rs)
    print(f"| {lab} | {var} | {item} | {n} | {p} | {'yes' if p == n else 'no'} | "
          f"{statistics.median(r[1] for r in rs):,.0f} | {cost / p if p else float('nan'):.3f} |")
    s = summary[(lab, var)]
    s["runs"] += n
    s["pass"] += p
    s["flaky"] += int(0 < p < n)
    s["failing"] += int(p == 0)
print()
for (lab, var), s in sorted(summary.items()):
    rate = s["pass"] / s["runs"] if s["runs"] else 0
    go = rate >= float(gate.get("pass_rate", 0)) and s["flaky"] <= int(gate.get("flaky", 99))
    print(f"{lab} {var}: pass rate {rate:.0%} ({s['pass']}/{s['runs']}), flaky tasks {s['flaky']}, "
          f"always-failing tasks {s['failing']} -> {'GO' if go else 'NO-GO'} ({args.gate})")
