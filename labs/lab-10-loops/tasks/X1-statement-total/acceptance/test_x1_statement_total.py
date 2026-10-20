from decimal import Decimal

from ledgerline_billing.statements import statement_total


def test_sum_in_cents() -> None:
    assert statement_total([Decimal("10.10"), Decimal("0.25")]) == 1035


def test_rounds_half_to_even() -> None:
    assert statement_total([Decimal("0.125")]) == 12
    assert statement_total([Decimal("0.135")]) == 14


def test_empty_is_zero() -> None:
    assert statement_total([]) == 0
