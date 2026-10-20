"""Summarize LAB-09 grades: pass^k and per-criterion pass rate per variant.

    python3 labs/lab-09-skills/summarize.py [runs-dir]

Reads every lab-09 run's grade.txt (written by the runner or by you:
grade.sh <run> > <run>/grade.txt).
"""

import os
import sys
from collections import defaultdict
from pathlib import Path

runs = Path(sys.argv[1] if len(sys.argv) > 1
            else os.environ.get("CCFM_RUNS", Path.home() / "ccfm-runs"))
rows: dict[str, list[dict[str, bool]]] = defaultdict(list)
for run in sorted(runs.glob("lab-09-*")):
    g = run / "grade.txt"
    if not g.exists():
        continue
    variant = (run / "meta/variant").read_text().strip()
    crit = {ln.split()[0]: ln.rstrip().endswith("PASS")
            for ln in g.read_text().splitlines() if ln and not ln.startswith("RESULT")}
    crit["ALL"] = "RESULT PASS" in g.read_text()
    rows[variant].append(crit)

for variant, rs in sorted(rows.items()):
    k = len(rs)
    print(f"{variant}: k={k}  pass^k={'yes' if all(r['ALL'] for r in rs) else 'no'}"
          f"  runs passing={sum(r['ALL'] for r in rs)}/{k}")
    for c in [c for c in rs[0] if c != "ALL"]:
        print(f"    {c:<10} {sum(r.get(c, False) for r in rs)}/{k}")
