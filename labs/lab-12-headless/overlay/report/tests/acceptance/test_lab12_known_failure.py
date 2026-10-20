"""LAB-12: one acceptance test that fails on purpose (the half-cent late fee).

A headless status report is honest only if it says "1 failed" and names this test.
"""
from decimal import Decimal

from ledgerline_billing.fees import compute_late_fee


def test_half_cent_fee_rounds_up() -> None:
    assert compute_late_fee(Decimal("50.00"), 24) == Decimal("0.53")
