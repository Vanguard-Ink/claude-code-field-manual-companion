from decimal import Decimal

import pytest

from ledgerline_billing.discounts import apply_discount


def test_twenty_percent() -> None:
    assert apply_discount(Decimal("100.00"), 20) == Decimal("80.00")


def test_out_of_range() -> None:
    with pytest.raises(ValueError):
        apply_discount(Decimal("1.00"), 101)
