# Done — Nightly job in the customer's time zone

## Requirements
- `next_run_at(customer_tz, now)` returns the next 02:00 in the customer's local time, as a UTC datetime.
- Existing behavior for UTC customers is unchanged.

## No regressions
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/
