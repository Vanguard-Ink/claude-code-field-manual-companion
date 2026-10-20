"""Refunds, with the same retry policy as charges."""

import time
from collections.abc import Callable

from ledgerline_billing.gateway import FakeGateway
from ledgerline_billing.policy import transient_retrying


def refund(
    gateway: FakeGateway,
    charge_id: str,
    amount_cents: int,
    *,
    idempotency_key: str,
    sleep: Callable[[float], None] = time.sleep,
) -> str:
    """Refund part or all of a charge; returns the refund id."""
    if amount_cents <= 0:
        raise ValueError("amount must be positive")
    return transient_retrying(sleep)(
        gateway.refund, charge_id, amount_cents, idempotency_key
    )
