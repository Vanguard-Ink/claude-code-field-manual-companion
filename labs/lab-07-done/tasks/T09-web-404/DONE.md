# Done — 404 for a missing report

## Target (must go fail → pass)
- tests/acceptance/test_t09_web_404.py
  (committed before the task starts)

## No regressions (must stay pass → pass)
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/
- migrations/
- .github/
- clients/generated/
- vendor/

## Evidence in the final message
- Each command above and its last 20 lines
- `git diff --stat`
