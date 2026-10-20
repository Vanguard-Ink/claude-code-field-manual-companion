# Done — Delete permission

## Requirements
- Only admins may delete a report: `can_delete(role)`.

## No regressions
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/
