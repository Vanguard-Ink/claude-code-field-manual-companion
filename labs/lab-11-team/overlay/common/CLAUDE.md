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
- Secrets live in `.env`, which is never committed or copied into other files.

## Conventions
- New tests for a package go in `packages/<pkg>/tests/`.
- Commit subject starts with the package name, e.g. `billing: cap late fees`.
