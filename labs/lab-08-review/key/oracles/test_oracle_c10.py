from datetime import date

from ledgerline_billing.overdue import is_overdue


def test_oracle_year_boundary() -> None:
    assert is_overdue(date(2026, 12, 31), date(2027, 1, 1))
