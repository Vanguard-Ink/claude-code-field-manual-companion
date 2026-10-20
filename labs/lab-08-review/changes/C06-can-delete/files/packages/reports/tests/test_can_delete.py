from ledgerline_reports.permissions import can_delete


def test_admin_can_delete() -> None:
    assert can_delete("admin")


def test_viewer_cannot_delete() -> None:
    assert not can_delete("viewer")
