# Done — L3 Fix late-fee rounding

## Target (must go fail → pass)
- tests/acceptance/test_l3_fee_rounding.py

## Characterization first
- tests/characterization/test_late_fee.py and late_fee_cases.json,
  committed before any change to fees.py, at least 20 cases
- Those tests alone cover fees.py (line coverage at least 90%)

## Smallest change
- Outputs change only where the exact fee ends in half a cent

## No regressions
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/, packages/legacy-pay/
