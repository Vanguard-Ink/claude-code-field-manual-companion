"""Invoice numbering."""


def format_invoice_number(seq: int, year: int) -> str:
    """Return the display number for an invoice."""
    if seq < 1:
        raise ValueError("sequence starts at 1")
    return f"INV-{seq}"
