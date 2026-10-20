"""Nightly invoice job scheduling."""

from datetime import datetime, timedelta

from ledgerline_shared.settings import load_settings


def next_run_at(customer_tz: str, now: datetime) -> datetime:
    """Return the next time the nightly job runs for this customer, in UTC.

    The job runs at the configured hour in the customer's local time.
    """
    hour = load_settings().nightly_run_hour
    run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if run <= now:
        run += timedelta(days=1)
    return run
