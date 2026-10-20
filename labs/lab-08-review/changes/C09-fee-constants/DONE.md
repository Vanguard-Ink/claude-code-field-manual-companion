# Done — Name the fee constants

## Requirements
- Replace the magic minimum-fee number in fees.py with a named constant; no behavior change.

## No regressions
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/
