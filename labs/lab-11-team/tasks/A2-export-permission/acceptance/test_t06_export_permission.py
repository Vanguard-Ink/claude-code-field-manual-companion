from ledgerline_reports.permissions import can_export
from ledgerline_shared.settings import Settings


def test_viewer_denied_without_flag() -> None:
    assert not can_export("viewer", Settings())


def test_viewer_allowed_with_flag() -> None:
    assert can_export("viewer", Settings(flags={"viewer_export": True}))


def test_analyst_unaffected() -> None:
    assert can_export("analyst", Settings())


def test_unknown_role_denied() -> None:
    assert not can_export("guest", Settings(flags={"viewer_export": True}))
