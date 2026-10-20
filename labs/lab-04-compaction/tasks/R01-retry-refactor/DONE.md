# Done — Billing retry refactor

## Target (must go fail → pass)
- tests/acceptance/test_r01_retry_refactor.py (one test per step)

## No regressions (must stay pass → pass)
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Decisions (must hold at the end)
- `retry_helper.py` stays deleted; retries use tenacity directly.
- `charge()` keeps its public signature: callers in 3 services.

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/

## Evidence in the final message
- Each command above and its last 20 lines
- `git diff --stat`
