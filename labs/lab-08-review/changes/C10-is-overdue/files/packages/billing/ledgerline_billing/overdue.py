"""Overdue checks for invoices."""

from datetime import date


def is_overdue(due: date, today: date) -> bool:
    """True only when today is strictly after the due date."""
    return today > due
