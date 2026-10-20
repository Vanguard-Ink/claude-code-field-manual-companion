from ledgerline_reports.permissions import can_export, can_view
from ledgerline_shared.settings import Settings


def test_mixed_case_roles() -> None:
    assert can_view("Admin")
    assert can_export("ANALYST", Settings())
    assert not can_view("Guest")
