"""Nightly invoice job scheduling."""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from ledgerline_shared.settings import load_settings


def next_run_at(customer_tz: str, now: datetime) -> datetime:
    """Return the next time the nightly job runs for this customer, in UTC.

    The job runs at the configured hour in the customer's local time.
    """
    hour = load_settings().nightly_run_hour
    tz = ZoneInfo(customer_tz)
    local_now = now.astimezone(tz)
    run = local_now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if run <= local_now:
        run = (run + timedelta(days=1)).replace(hour=hour)
    return run.astimezone(UTC)
