# Done — Retry gateway timeouts

## Target (must go fail → pass)
- tests/acceptance/test_t02_retry_timeout.py
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
- packages/billing/ledgerline_billing/gateway.py

## Evidence in the final message
- Each command above and its last 20 lines
- `git diff --stat`
