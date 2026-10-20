from decimal import Decimal

from ledgerline_billing.fees import compute_late_fee


def test_long_overdue_is_capped() -> None:
    assert compute_late_fee(Decimal("100.00"), 400) == Decimal("10.00")


def test_cap_beats_minimum_fee() -> None:
    assert compute_late_fee(Decimal("2.00"), 10) == Decimal("0.20")


def test_normal_case_unchanged() -> None:
    assert compute_late_fee(Decimal("100.00"), 10) == Decimal("0.50")
    assert compute_late_fee(Decimal("100.00"), 63) == Decimal("3.0")


def test_grace_period_unchanged() -> None:
    assert compute_late_fee(Decimal("100.00"), 3) == Decimal("0.00")
