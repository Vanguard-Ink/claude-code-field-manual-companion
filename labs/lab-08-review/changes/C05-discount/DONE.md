# Done — Percentage discounts

## Requirements
- `apply_discount(amount, percent)` returns the discounted amount rounded half-up to the cent.
- Money stays Decimal end to end (CLAUDE.md).

## No regressions
- `make test`  exits 0
- `make lint typecheck`  exits 0

## Fence (must not change)
- tests/acceptance/, migrations/, .github/
- clients/generated/, vendor/
