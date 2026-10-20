"""Money helpers. Amounts are Decimal in code and integer cents at the edge."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def round_money(amount: Decimal) -> Decimal:
    """Round an amount to whole cents, half a cent away from zero."""
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def to_cents(amount: Decimal) -> int:
    """Convert a Decimal amount to integer cents."""
    return int(round_money(amount) * 100)


def from_cents(cents: int) -> Decimal:
    """Convert integer cents to a Decimal amount."""
    return (Decimal(cents) / 100).quantize(CENT)
