from decimal import Decimal

from ledgerline_billing.fees import compute_late_fee


def test_ticket_case() -> None:
    assert compute_late_fee(Decimal("50.00"), 28) == Decimal("0.63")


def test_other_half_cent_cases_round_up() -> None:
    assert compute_late_fee(Decimal("50.00"), 24) == Decimal("0.53")
    assert compute_late_fee(Decimal("50.00"), 44) == Decimal("1.03")
