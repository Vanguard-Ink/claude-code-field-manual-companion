from decimal import Decimal

from ledgerline_billing.fees import compute_late_fee


def test_oracle_unchanged_outputs() -> None:
    assert compute_late_fee(Decimal("100.00"), 10) == Decimal("0.5")
    assert compute_late_fee(Decimal("100.00"), 63) == Decimal("3.0")
    assert compute_late_fee(Decimal("100.00"), 2) == Decimal("0.00")
