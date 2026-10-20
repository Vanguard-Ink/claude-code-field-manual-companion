"""Volume discounts."""

from decimal import Decimal

from ledgerline_shared.money import round_money

THRESHOLD = Decimal("10000.00")
RATE = Decimal("0.02")


def apply_volume_discount(amount: Decimal) -> Decimal:
    """Amount to bill after the volume discount (over 10,000.00)."""
    if amount > THRESHOLD:
        return round_money(amount * (1 - RATE))
    return round_money(amount)
