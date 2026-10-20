from datetime import UTC, datetime

from ledgerline_billing.invoices import next_run_at


def test_oracle_new_york_across_dst_end() -> None:
    # 2026-11-01: US daylight time ends. 02:00 EST = 07:00 UTC.
    now = datetime(2026, 10, 31, 12, 0, tzinfo=UTC)
    assert next_run_at("America/New_York", now) == datetime(
        2026, 11, 1, 7, 0, tzinfo=UTC
    )
