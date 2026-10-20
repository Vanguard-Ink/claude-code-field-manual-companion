from decimal import Decimal

from ledgerline_shared.money import round_money, to_cents


def test_half_cent_rounds_up() -> None:
    assert round_money(Decimal("0.125")) == Decimal("0.13")
    assert round_money(Decimal("2.675")) == Decimal("2.68")


def test_to_cents_uses_half_up() -> None:
    assert to_cents(Decimal("0.005")) == 1


def test_negative_amounts_round_away_from_zero() -> None:
    assert round_money(Decimal("-0.125")) == Decimal("-0.13")
