# Commands
- Test one file: python3 -m pytest path/to/test_x.py
- Before any commit: make test lint typecheck

# Decisions
- Money is Decimal in code, integer cents at the
  gateway; never float.
- New handlers need a test in packages/web/tests/.
- packages/legacy-pay/ is deprecated; don't import it.

# Etiquette
- Commit subject starts with the package: billing: …
- IMPORTANT: never edit clients/generated/ or vendor/.
  They are generated or vendored.
