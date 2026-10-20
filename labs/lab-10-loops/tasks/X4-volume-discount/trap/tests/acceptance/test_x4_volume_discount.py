from decimal import Decimal

from ledgerline_billing.discounts import apply_volume_discount


def test_below_threshold_pays_full() -> None:
    assert apply_volume_discount(Decimal("9999.99")) == Decimal("9999.99")


def test_large_invoice_discounted() -> None:
    assert apply_volume_discount(Decimal("20000.00")) == Decimal("19600.00")


def test_finance_threshold_is_exclusive() -> None:
    assert apply_volume_discount(Decimal("10000.00")) == Decimal("10000.00")
