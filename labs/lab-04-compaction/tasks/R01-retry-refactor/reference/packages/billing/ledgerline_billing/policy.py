"""The retry policy shared by charges and refunds (tenacity)."""

from collections.abc import Callable

from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ledgerline_billing.gateway import GatewayBusy, GatewayTimeout
from ledgerline_shared.settings import load_settings

TRANSIENT = (ConnectionError, GatewayTimeout, GatewayBusy)


def transient_retrying(sleep: Callable[[float], None]) -> Retrying:
    """Retry transient gateway errors with capped exponential backoff."""
    s = load_settings()
    return Retrying(
        retry=retry_if_exception_type(TRANSIENT),
        stop=stop_after_attempt(s.retry_attempts),
        wait=wait_exponential(
            min=s.retry_backoff_seconds, max=s.retry_max_backoff_seconds
        ),
        sleep=sleep,
        reraise=True,
    )
