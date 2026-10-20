from decimal import Decimal

from ledgerline_billing.discounts import apply_discount


def test_oracle_half_cent_rounds_up() -> None:
    assert apply_discount(Decimal("1.15"), 50) == Decimal("0.58")
