"""Invoice numbering."""

MAX_SEQ = 999_999


def format_invoice_number(seq: int, year: int) -> str:
    """Return the display number, e.g. INV-2026-000123."""
    if seq < 1:
        raise ValueError("sequence starts at 1")
    if seq > MAX_SEQ:
        raise ValueError("sequence exceeds six digits")
    return f"INV-{year:04d}-{seq:06d}"
