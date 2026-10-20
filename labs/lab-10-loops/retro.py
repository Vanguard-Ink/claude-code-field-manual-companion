"""Part A: scan finished runs of another lab for loops and duplicates.

    python3 labs/lab-10-loops/retro.py [lab-07] [runs-dir]

Costs no tokens: it reads the transcripts and workspaces the runs left.
Prints one row per run and a total per variant.
"""

import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
lab = sys.argv[1] if len(sys.argv) > 1 else "lab-07"
runs = Path(sys.argv[2] if len(sys.argv) > 2
            else os.environ.get("CCFM_RUNS", Path.home() / "ccfm-runs"))
tot: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
print("run | variant | item | loops | duplicates")
for run in sorted(runs.glob(f"{lab}-*")):
    ws, meta = run / "workspace", run / "meta"
    if not (meta / "base_sha").exists():
        continue
    variant = (meta / "variant").read_text().strip()
    item = (meta / "item").read_text().strip()
    tr = sorted((run / "transcripts").glob("*.jsonl"))
    loop = ""
    if tr:
        loop = subprocess.run([sys.executable, str(HERE / "loopscan.py"), *map(str, tr)],
                              capture_output=True, text=True).stdout.strip()
    dup = subprocess.run(
        [sys.executable, str(ROOT / "templates/hooks/dupcheck.py"),
         "--base", (meta / "base_sha").read_text().strip(),
         "--canonical", str(ROOT / "templates/docs/canonical.txt")],
        cwd=ws, capture_output=True, text=True).stdout.strip().splitlines()
    t = tot[variant]
    t[0] += 1
    t[1] += "LOOP" in loop
    t[2] += bool(dup)
    print(f"{run.name} | {variant} | {item} | {loop or 'no transcript'} | {len(dup)}")
print()
for v, (n, loops, dups) in sorted(tot.items()):
    print(f"{v}: {n} runs, {loops} with a loop, {dups} with duplicate findings")
