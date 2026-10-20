"""Charging a customer through the gateway."""

import time
from collections.abc import Callable
from dataclasses import dataclass

from ledgerline_billing.gateway import FakeGateway, GatewayTimeout
from ledgerline_billing.retry_helper import with_retries
from ledgerline_shared.settings import load_settings


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
    settings = load_settings()
    charge_id = with_retries(
        lambda: gateway.submit(customer_id, amount_cents, idempotency_key),
        attempts=settings.retry_attempts,
        exceptions=(ConnectionError, GatewayTimeout),
        backoff=settings.retry_backoff_seconds,
        sleep=sleep,
    )
    return ChargeResult(charge_id=charge_id, amount_cents=amount_cents)
