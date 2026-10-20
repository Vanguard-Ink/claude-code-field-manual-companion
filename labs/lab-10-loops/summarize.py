"""Summarize LAB-10 Part B grades per variant.

    python3 labs/lab-10-loops/summarize.py [runs-dir]
"""

import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

runs = Path(sys.argv[1] if len(sys.argv) > 1
            else os.environ.get("CCFM_RUNS", Path.home() / "ccfm-runs"))
fails: dict[str, Counter[str]] = defaultdict(Counter)
n: Counter[str] = Counter()
for run in sorted(runs.glob("lab-10-*")):
    g = run / "grade.txt"
    if not g.exists():
        continue
    v = (run / "meta/variant").read_text().strip()
    n[v] += 1
    for ln in g.read_text().splitlines():
        parts = ln.split()
        if not parts:
            continue
        if ln.rstrip().endswith("FAIL") and parts[0] != "RESULT":
            fails[v][parts[0]] += 1
        if parts[0] == "loop" and "LOOP" in ln:
            fails[v]["loop"] += 1
        if ln.startswith("RESULT PASS"):
            fails[v]["(runs passing)"] += 1
for v in sorted(n):
    print(f"{v}: {n[v]} runs")
    for k, c in sorted(fails[v].items()):
        print(f"    {k:<16} {c}")
