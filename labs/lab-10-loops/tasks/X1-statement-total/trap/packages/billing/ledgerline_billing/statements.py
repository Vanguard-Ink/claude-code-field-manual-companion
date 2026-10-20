"""Statement totals."""

from decimal import ROUND_HALF_EVEN, Decimal


def statement_total(amounts: list[Decimal]) -> int:
    """Total of the amounts in integer cents (half to even)."""
    total = sum(amounts, Decimal("0"))
    rounded = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
    return int(rounded * 100)
