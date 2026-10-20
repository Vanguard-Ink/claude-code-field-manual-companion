"""Late fees. Legacy module: characterization tests in tests/characterization.

Computed in Decimal and rounded half-up to the cent.
"""

from decimal import ROUND_HALF_UP, Decimal

RATE_PER_30_DAYS = Decimal("0.015")  # 1.5% per 30 days, prorated
GRACE_DAYS = 3
MINIMUM_FEE = Decimal("0.5")


def compute_late_fee(amount: Decimal, days: int) -> Decimal:
    if days <= GRACE_DAYS:
        return Decimal("0.00")
    late = days - GRACE_DAYS
    fee = amount * RATE_PER_30_DAYS * Decimal(late) / Decimal(30)
    fee = max(fee, MINIMUM_FEE)
    return fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
