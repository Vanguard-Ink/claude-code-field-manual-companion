#!/usr/bin/env python3
"""Summarize LAB-07 runs: false-done rate and pass^k per variant.

    python3 labs/lab-07-done/summarize.py [runs-dir]

A run counts as a claim of done when final.md exists. A false done is a
claim whose grade is FAIL. pass^k for a task = 1 if all k graded runs of
that task passed, else 0; reported as the share of tasks.
"""
import sys
from collections import defaultdict
from pathlib import Path

runs = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "ccfm-runs")
by_variant: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
for meta in sorted(runs.glob("lab-07-*/meta")):
    run = meta.parent
    if not (run / "final.md").exists() or not (meta / "grade").exists():
        continue
    variant = (meta / "variant").read_text().strip()
    item = (meta / "item").read_text().strip()
    by_variant[variant][item].append((meta / "grade").read_text().strip() == "PASS")

for variant, tasks in sorted(by_variant.items()):
    claims = [g for gs in tasks.values() for g in gs]
    false_done = sum(1 for g in claims if not g)
    k = min(len(g) for g in tasks.values())
    pass_k = sum(1 for g in tasks.values() if all(g[:k])) / len(tasks)
    print(f"{variant}: {len(claims)} claims, false-done "
          f"{false_done}/{len(claims)} = {false_done / len(claims):.0%}, "
          f"pass^{k} = {pass_k:.0%} over {len(tasks)} tasks")
