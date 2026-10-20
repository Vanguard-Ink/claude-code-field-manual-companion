from datetime import date

from ledgerline_billing.overdue import is_overdue


def test_due_today_is_not_overdue() -> None:
    assert not is_overdue(date(2026, 3, 10), date(2026, 3, 10))


def test_day_after_is_overdue() -> None:
    assert is_overdue(date(2026, 3, 10), date(2026, 3, 11))


def test_before_due_is_not_overdue() -> None:
    assert not is_overdue(date(2026, 3, 10), date(2026, 3, 9))
