# Ledgerline

## Commands
- Setup once: `python3 -m venv .venv`, activate it, `make setup`
- Run one test file: `python3 -m pytest path/to/test_x.py`
- Before saying a task is done: `make test lint typecheck`

## Decisions
- Money is `Decimal` in code and integer cents at the gateway; never float.
- Never edit `clients/generated/` or `vendor/`. They are generated or vendored.
- Never edit a migration in `migrations/` after it exists; add a new one.
- `packages/legacy-pay/` is deprecated. Do not import from it.

# Compact instructions

When you are using compact, keep: decisions and their
reasons, the current plan step, failing test names, and
any file the user said not to touch. Drop exploratory
output that led nowhere.

## Handoff
- Keep notes/handoff.md current: update it after every step.
