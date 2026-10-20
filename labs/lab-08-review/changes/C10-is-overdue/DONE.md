# Done — Overdue check

## Requirements
- `is_overdue(due, today)` is true only when today is after the due date.

## No regressions
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/
