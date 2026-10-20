"""Refunds through the gateway."""

import time
from collections.abc import Callable

from ledgerline_billing.gateway import FakeGateway


def refund(
    gateway: FakeGateway,
    charge_id: str,
    amount_cents: int,
    *,
    idempotency_key: str,
    sleep: Callable[[float], None] = time.sleep,
) -> str:
    """Refund a charge. Connection resets are retried; nothing else is."""
    for attempt in range(1, 4):
        try:
            return gateway.refund(charge_id, amount_cents, idempotency_key)
        except ConnectionError:
            if attempt == 3:
                raise
            sleep(0.5 * attempt)
    raise AssertionError("unreachable")
