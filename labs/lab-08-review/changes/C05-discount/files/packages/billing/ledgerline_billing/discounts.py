"""Percentage discounts on invoice amounts."""

from decimal import Decimal


def apply_discount(amount: Decimal, percent: int) -> Decimal:
    """Return amount reduced by percent, rounded to the cent."""
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    discounted = float(amount) * (100 - percent) / 100
    return Decimal(str(round(discounted, 2)))
