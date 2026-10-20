"""Late fees. Legacy module: no tests, behavior relied on by finance.

Written before the money helpers existed. Do not 'clean up' without
characterization tests first.
"""

from decimal import Decimal

RATE_PER_30_DAYS = 0.015  # 1.5% per 30 days, prorated
GRACE_DAYS = 3


def compute_late_fee(amount: Decimal, days: int) -> Decimal:
    if days <= GRACE_DAYS:
        return Decimal("0.00")
    late = days - GRACE_DAYS
    # prorated, computed in float (historical)
    fee = float(amount) * RATE_PER_30_DAYS * (late / 30)
    if fee < 0.5:
        fee = 0.5  # minimum fee
    return Decimal(str(round(fee, 2)))
