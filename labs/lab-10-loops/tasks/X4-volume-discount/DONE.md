# Done — Volume discount

## Target (must go fail → pass)
- tests/acceptance/test_x4_volume_discount.py
  (committed before the task starts)

## No regressions (must stay pass → pass)
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Scope (may change; nothing else)
- packages/billing/ledgerline_billing/discounts.py (new)
- packages/billing/tests/ (new tests only)
- notes/blocked.md (only if blocked)

## Fence (must not change)
- tests/acceptance/
- migrations/
- .github/
- clients/generated/
- vendor/

## Evidence in the final message
- Each command above and its last 20 lines
- `git diff --stat`

## If you can't finish
If the task can't be done as written (conflicting
requirements, missing information), don't force it.
Write `notes/blocked.md`: what conflicts, the evidence
(test names, output), and what you need. Then stop
and say you're blocked.
