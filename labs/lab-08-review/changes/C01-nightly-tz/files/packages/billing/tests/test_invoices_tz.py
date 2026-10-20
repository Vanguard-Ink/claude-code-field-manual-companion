from datetime import UTC, datetime

from ledgerline_billing.invoices import next_run_at


def test_london_in_winter() -> None:
    now = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    assert next_run_at("Europe/London", now) == datetime(
        2026, 1, 16, 2, 0, tzinfo=UTC)


def test_tokyo_crosses_the_utc_date() -> None:
    now = datetime(2026, 3, 10, 12, 0, tzinfo=UTC)
    assert next_run_at("Asia/Tokyo", now) == datetime(
        2026, 3, 10, 17, 0, tzinfo=UTC)
