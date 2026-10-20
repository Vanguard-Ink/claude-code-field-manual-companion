# Ledgerline — Project Guide for Claude

This file tells Claude everything about Ledgerline. Read it fully before every task.

## Overview

Ledgerline is an invoicing and reporting service. It lets finance teams create invoices,
charge customers through a payment gateway, compute late fees, schedule a nightly invoice
job, and produce reports that can be listed, paged, and exported. The codebase is a Python
monorepo with several packages. Each package has its own source folder and tests folder.
The service is used by several internal teams and has been in production for years.

## Directory layout

- `./.gitignore`
- `./CLAUDE.md`
- `./Makefile`
- `./pyproject.toml`
- `./requirements-dev.txt`
- `./requirements.txt`
- `./clients/generated/ledgerline_client/__init__.py`
- `./clients/generated/ledgerline_client/api.py`
- `./migrations/0001_init.sql`
- `./migrations/0002_reports.sql`
- `./notes/.gitkeep`
- `./packages/billing/ledgerline_billing/__init__.py`
- `./packages/billing/ledgerline_billing/charge.py`
- `./packages/billing/ledgerline_billing/fees.py`
- `./packages/billing/ledgerline_billing/gateway.py`
- `./packages/billing/ledgerline_billing/invoice_numbers.py`
- `./packages/billing/ledgerline_billing/invoices.py`
- `./packages/billing/ledgerline_billing/retry_helper.py`
- `./packages/billing/tests/test_charge.py`
- `./packages/billing/tests/test_invoices.py`
- `./packages/legacy-pay/ledgerline_legacy_pay/__init__.py`
- `./packages/legacy-pay/ledgerline_legacy_pay/fees.py`
- `./packages/reports/ledgerline_reports/__init__.py`
- `./packages/reports/ledgerline_reports/flags.py`
- `./packages/reports/ledgerline_reports/models.py`
- `./packages/reports/ledgerline_reports/permissions.py`
- `./packages/reports/ledgerline_reports/service.py`
- `./packages/reports/tests/test_reports.py`
- `./packages/shared/ledgerline_shared/__init__.py`
- `./packages/shared/ledgerline_shared/clock.py`
- `./packages/shared/ledgerline_shared/money.py`
- `./packages/shared/ledgerline_shared/settings.py`
- `./packages/shared/tests/test_money.py`
- `./packages/shared/tests/test_settings.py`
- `./packages/web/ledgerline_web/__init__.py`
- `./packages/web/ledgerline_web/handlers.py`
- `./packages/web/tests/test_handlers.py`
- `./tasks/.gitkeep`
- `./tests/conftest.py`
- `./tests/acceptance/README.md`
- `./vendor/sdk/payments_sdk/__init__.py`
- `./vendor/sdk/payments_sdk/client.py`

## Tech stack

- Python 3.11+. Python is a dynamically typed language; we use type hints everywhere.
- pytest is the test framework. pytest discovers files named test_*.py.
- ruff is the linter. It checks style and common bugs.
- mypy is the type checker. It reads type hints and reports type errors.
- tenacity is a retry library. It provides decorators and a Retrying class.
- zoneinfo is the standard-library time zone module.
- Decimal is the standard-library decimal type for exact arithmetic.
- Make is used to run common commands via the Makefile.

## Python style

- Use four spaces for indentation.
- Use snake_case for functions and variables.
- Use PascalCase for classes.
- Keep lines under 88 characters.
- Write docstrings for public functions.
- Prefer f-strings over format().
- Avoid mutable default arguments.
- Use pathlib for paths.
- Use dataclasses for simple records.
- Prefer composition over inheritance.
- Keep functions short and focused.
- Name things clearly.
- Avoid global state.
- Handle errors explicitly.
- Write clean code.
- Don't repeat yourself.
- Use type hints on every function.
- Sort imports with ruff.
- Avoid wildcard imports.
- Use context managers for files.

## Commands

- Create a virtual environment: `python3 -m venv .venv`
- Activate it: `source .venv/bin/activate`
- Install dependencies: `make setup`
- Run all tests: `make test`
- Run the linter: `make lint`
- Run the type checker: `make typecheck`
- Run everything: `make check`
- Run one test file: `python3 -m pytest path/to/test_x.py`

## Testing philosophy

Tests are the safety net of the codebase. Every change should be covered by tests. We value fast tests that run in milliseconds. Tests should be deterministic and isolated. Avoid sleeping in tests; inject a sleep function instead. Avoid network access in tests. Prefer small unit tests, and add a few integration tests where packages meet. A test should fail for one reason only. Name tests after the behavior they check. When you fix a bug, first write a test that reproduces it. Keep fixtures small. 
Tests are the safety net of the codebase. Every change should be covered by tests. We value fast tests that run in milliseconds. Tests should be deterministic and isolated. Avoid sleeping in tests; inject a sleep function instead. Avoid network access in tests. Prefer small unit tests, and add a few integration tests where packages meet. A test should fail for one reason only. Name tests after the behavior they check. When you fix a bug, first write a test that reproduces it. Keep fixtures small. 
Tests are the safety net of the codebase. Every change should be covered by tests. We value fast tests that run in milliseconds. Tests should be deterministic and isolated. Avoid sleeping in tests; inject a sleep function instead. Avoid network access in tests. Prefer small unit tests, and add a few integration tests where packages meet. A test should fail for one reason only. Name tests after the behavior they check. When you fix a bug, first write a test that reproduces it. Keep fixtures small. 
Tests are the safety net of the codebase. Every change should be covered by tests. We value fast tests that run in milliseconds. Tests should be deterministic and isolated. Avoid sleeping in tests; inject a sleep function instead. Avoid network access in tests. Prefer small unit tests, and add a few integration tests where packages meet. A test should fail for one reason only. Name tests after the behavior they check. When you fix a bug, first write a test that reproduces it. Keep fixtures small. 
Tests are the safety net of the codebase. Every change should be covered by tests. We value fast tests that run in milliseconds. Tests should be deterministic and isolated. Avoid sleeping in tests; inject a sleep function instead. Avoid network access in tests. Prefer small unit tests, and add a few integration tests where packages meet. A test should fail for one reason only. Name tests after the behavior they check. When you fix a bug, first write a test that reproduces it. Keep fixtures small. 
Tests are the safety net of the codebase. Every change should be covered by tests. We value fast tests that run in milliseconds. Tests should be deterministic and isolated. Avoid sleeping in tests; inject a sleep function instead. Avoid network access in tests. Prefer small unit tests, and add a few integration tests where packages meet. A test should fail for one reason only. Name tests after the behavior they check. When you fix a bug, first write a test that reproduces it. Keep fixtures small. 

## Decisions

- Money is `Decimal` in code and integer cents at the gateway; never float.
- Never edit `clients/generated/` or `vendor/`. They are generated or vendored.
- Never edit a migration in `migrations/` after it exists; add a new one.
- New handlers in `packages/web/` need a test in `packages/web/tests/`.
- Commit subjects start with the package name, e.g. `billing: cap late fees`.
- `packages/legacy-pay/` is deprecated. Do not import from it.

## Release checklist

1. Pull main
2. Run make check
3. Update CHANGELOG.md with every merged PR
4. Bump the version in pyproject.toml
5. Tag the release vX.Y.Z
6. Push the tag
7. Watch CI
8. Announce in #releases
9. Update the status page
10. Close the milestone

## Migration routine

1. Find the highest migration number
2. Create the next file NNNN_description.sql
3. Write forward-only SQL
4. Never edit an existing migration
5. Run the migration check
6. Add a test for the schema change
7. Ask for a DBA review
8. Merge only after review

## Code review rubric

1. Does it match the ticket?
2. Are there tests?
3. Is money Decimal?
4. Are errors handled?
5. Is logging appropriate?
6. Are names clear?
7. Is it the smallest change?
8. Does CI pass?
9. Are docs updated?
10. Are migrations forward-only?

## Glossary

- Invoice: a bill sent to a customer.
- Charge: a payment attempt through the gateway.
- Refund: money returned to a customer.
- Late fee: a fee for paying after the due date.
- Grace period: days before a late fee applies.
- Report: a table of data for finance.
- Export: a CSV download of a report.
- Viewer: a read-only role.
- Analyst: a role that can export.
- Admin: a role that can do everything.
- Feature flag: a switch in settings.
- Nightly job: the scheduled invoice run.

## Notes from past sessions

- Remember that tests live next to packages.
- Remember to run the linter.
- Remember that settings have defaults.
- The gateway is fake in tests.
- Late fees have a minimum.
- Reports are in memory.
- Pages start at 1.
- Handlers return Response objects.
- The legacy package is deprecated.
- Generated code is in clients/generated.
- Remember that tests live next to packages.
- Remember to run the linter.
- Remember that settings have defaults.
- The gateway is fake in tests.
- Late fees have a minimum.
- Reports are in memory.
- Pages start at 1.
- Handlers return Response objects.
- The legacy package is deprecated.
- Generated code is in clients/generated.
- Remember that tests live next to packages.
- Remember to run the linter.
- Remember that settings have defaults.
- The gateway is fake in tests.
- Late fees have a minimum.
- Reports are in memory.
- Pages start at 1.
- Handlers return Response objects.
- The legacy package is deprecated.
- Generated code is in clients/generated.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
- Keep this file up to date.
