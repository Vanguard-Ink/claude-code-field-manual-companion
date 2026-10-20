# Done — Report counts by owner

## Requirements
- `counts_by_owner()` returns a dict of owner → number of reports, owners sorted alphabetically.

## No regressions
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/
