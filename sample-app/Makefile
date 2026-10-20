# Ledgerline — the three checks every lab uses.
PY ?= python3

.PHONY: setup test lint typecheck check

setup:
	$(PY) -m pip install -r requirements-dev.txt

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check .

typecheck:
	$(PY) -m mypy

check: test lint typecheck
