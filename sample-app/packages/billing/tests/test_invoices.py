from datetime import UTC, datetime

from ledgerline_billing.invoice_numbers import format_invoice_number
from ledgerline_billing.invoices import next_run_at


def test_next_run_for_utc_customer() -> None:
    now = datetime(2026, 3, 10, 12, 0, tzinfo=UTC)
    assert next_run_at("UTC", now) == datetime(2026, 3, 11, 2, 0, tzinfo=UTC)


def test_invoice_number_has_prefix() -> None:
    assert format_invoice_number(7, 2026).startswith("INV-")
