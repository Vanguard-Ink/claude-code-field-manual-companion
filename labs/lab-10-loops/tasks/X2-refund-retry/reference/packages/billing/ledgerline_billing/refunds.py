"""Refunds through the gateway."""

import time
from collections.abc import Callable

from ledgerline_billing.gateway import FakeGateway
from ledgerline_billing.retry_helper import with_retries


def refund(
    gateway: FakeGateway,
    charge_id: str,
    amount_cents: int,
    *,
    idempotency_key: str,
    sleep: Callable[[float], None] = time.sleep,
) -> str:
    """Refund a charge. Connection resets are retried; nothing else is."""
    return with_retries(
        lambda: gateway.refund(charge_id, amount_cents, idempotency_key),
        attempts=3,
        exceptions=(ConnectionError,),
        sleep=sleep,
    )
