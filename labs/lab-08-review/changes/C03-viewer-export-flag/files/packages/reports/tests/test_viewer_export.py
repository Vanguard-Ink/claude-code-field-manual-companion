from ledgerline_reports.permissions import can_export
from ledgerline_shared.settings import Settings


def test_viewer_with_flag_can_export() -> None:
    assert can_export("viewer", Settings(flags={"viewer_export": True}))


def test_viewer_with_flag_off_cannot_export() -> None:
    assert not can_export("viewer", Settings(flags={"viewer_export": False}))
