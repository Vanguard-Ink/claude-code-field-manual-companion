"""Statement totals."""

from decimal import Decimal

from ledgerline_shared.money import to_cents


def statement_total(amounts: list[Decimal]) -> int:
    """Total of the amounts in integer cents (half to even)."""
    return to_cents(sum(amounts, Decimal("0")))
