#!/usr/bin/env python3
"""LAB-06 L3 checks that need Python: case count, coverage, smallest change.

    python3 grade_l3.py <workspace> <base-sha>
Prints one line per check; exit 1 if any fails.
"""
import json
import subprocess
import sys
import tempfile
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ws, base = Path(sys.argv[1]), sys.argv[2]
COV = str(Path(tempfile.mkdtemp()) / "cov.json")
fail = 0


def line(k: str, what: str, ok: bool) -> None:
    global fail
    fail |= not ok
    print(f"{k:<9} {what:<44} {'PASS' if ok else 'FAIL'}")


# Root tests/ (default variant) or the package's own tests/ (scoped variant,
# where the session starts in packages/billing).
CHAR = next((d for d in ("tests/characterization", "packages/billing/tests/characterization")
             if (ws / d).is_dir()), "tests/characterization")
cases_file = ws / CHAR / "late_fee_cases.json"
cases = json.loads(cases_file.read_text()) if cases_file.exists() else []
line("charact", f"at least 20 recorded cases ({len(cases)})", len(cases) >= 20)

cov = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
     CHAR, "--cov=ledgerline_billing.fees",
     "--cov-report=json:" + COV],
    cwd=ws, capture_output=True, text=True)
pct = 0.0
if cov.returncode == 0 and Path(COV).exists():
    pct = json.loads(Path(COV).read_text())["totals"]["percent_covered"]
line("coverage", f"fees.py covered by characterization ({pct:.0f}%)", pct >= 90)

old_src = subprocess.run(
    ["git", "-C", str(ws), "show", f"{base}:packages/billing/ledgerline_billing/fees.py"],
    capture_output=True, text=True).stdout
new_src = (ws / "packages/billing/ledgerline_billing/fees.py").read_text()


def load(src: str):  # type: ignore[no-untyped-def]
    ns: dict = {}
    exec(compile(src, "fees", "exec"), ns)
    return ns["compute_late_fee"]


old_f, new_f = load(old_src), load(new_src)
bad = []
for amt in ("1.00", "10.00", "33.33", "50.00", "99.99", "250.00", "1234.56"):
    for days in range(0, 400, 1):
        a = Decimal(amt)
        o, n = old_f(a, days), new_f(a, days)
        if o == n:
            continue
        late = days - 3
        exact = a * Decimal("0.015") * Decimal(late) / Decimal(30)
        exact = max(exact, Decimal("0.5"))
        half = (exact * 1000) % 10 == 5
        if not (half and n == exact.quantize(Decimal("0.01"), ROUND_HALF_UP)):
            bad.append((amt, days, str(o), str(n)))
line("smallest", f"only half-cent cases changed ({len(bad)} other)", not bad)
for b in bad[:5]:
    print("          unexpected change:", b)
sys.exit(fail)
