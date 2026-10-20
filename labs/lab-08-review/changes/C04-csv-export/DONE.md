# Done — CSV export with formula protection

## Requirements
- `to_csv(report)` returns header then rows in column order.
- Cells starting with `=`, `+`, `-`, or `@` are prefixed with `'` so spreadsheets don't run them as formulas.

## No regressions
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/
