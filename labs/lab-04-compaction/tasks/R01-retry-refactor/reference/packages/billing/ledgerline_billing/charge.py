"""Charging a customer through the gateway (retries via tenacity)."""

import time
from collections.abc import Callable
from dataclasses import dataclass

from ledgerline_billing.gateway import FakeGateway
from ledgerline_billing.policy import transient_retrying


@dataclass(frozen=True)
class ChargeResult:
    charge_id: str
    amount_cents: int


def charge(
    gateway: FakeGateway,
    customer_id: str,
    amount_cents: int,
    *,
    idempotency_key: str,
    sleep: Callable[[float], None] = time.sleep,
) -> ChargeResult:
    """Charge a customer. Transient gateway failures are retried."""
    if amount_cents <= 0:
        raise ValueError("amount must be positive")
    charge_id = transient_retrying(sleep)(
        gateway.submit, customer_id, amount_cents, idempotency_key
    )
    return ChargeResult(charge_id=charge_id, amount_cents=amount_cents)
