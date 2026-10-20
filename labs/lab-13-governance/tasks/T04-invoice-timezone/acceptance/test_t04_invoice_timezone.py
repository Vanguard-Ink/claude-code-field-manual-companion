from datetime import UTC, datetime

from ledgerline_billing.invoices import next_run_at


def test_new_york_during_daylight_time() -> None:
    now = datetime(2026, 3, 10, 12, 0, tzinfo=UTC)  # 08:00 EDT
    assert next_run_at("America/New_York", now) == datetime(
        2026, 3, 11, 6, 0, tzinfo=UTC)


def test_tokyo_crosses_the_utc_date() -> None:
    now = datetime(2026, 3, 10, 12, 0, tzinfo=UTC)  # 21:00 JST
    assert next_run_at("Asia/Tokyo", now) == datetime(
        2026, 3, 10, 17, 0, tzinfo=UTC)


def test_utc_customer_unchanged() -> None:
    now = datetime(2026, 3, 10, 12, 0, tzinfo=UTC)
    assert next_run_at("UTC", now) == datetime(2026, 3, 11, 2, 0, tzinfo=UTC)
