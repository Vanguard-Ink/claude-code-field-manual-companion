from decimal import Decimal

from ledgerline_shared.money import from_cents, to_cents


def test_to_cents_whole_amount() -> None:
    assert to_cents(Decimal("12.34")) == 1234


def test_from_cents_round_trip() -> None:
    assert from_cents(1234) == Decimal("12.34")
