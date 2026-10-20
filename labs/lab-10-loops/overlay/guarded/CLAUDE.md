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

## Before you write new code
- Search for an existing helper first and reuse it.
  `.claude/canonical.txt` lists the canonical ones.
- Change only what the task's Scope list allows. No new
  modules or public names the task didn't ask for.
- Same failure twice after a fix: stop and write
  `notes/blocked.md` instead of trying a third variant.
