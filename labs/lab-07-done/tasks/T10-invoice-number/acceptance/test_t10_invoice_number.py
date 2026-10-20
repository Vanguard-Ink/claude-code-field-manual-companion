import pytest

from ledgerline_billing.invoice_numbers import format_invoice_number


def test_format() -> None:
    assert format_invoice_number(123, 2026) == "INV-2026-000123"


def test_largest_sequence() -> None:
    assert format_invoice_number(999999, 2026) == "INV-2026-999999"


def test_overflow_is_an_error() -> None:
    with pytest.raises(ValueError):
        format_invoice_number(1_000_000, 2026)


def test_sequence_starts_at_one() -> None:
    with pytest.raises(ValueError):
        format_invoice_number(0, 2026)
