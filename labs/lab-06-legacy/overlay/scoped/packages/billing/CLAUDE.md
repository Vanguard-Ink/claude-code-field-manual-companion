# Billing package

- Run tests from the repository root: `python3 -m pytest packages/billing`.
- `fees.py` is legacy and untested. Characterization tests first
  (tests/characterization/), committed on their own, before any change.
- Money is Decimal; the gateway takes integer cents.
- Retry policy lives in `charge.py`; the count comes from shared settings.
