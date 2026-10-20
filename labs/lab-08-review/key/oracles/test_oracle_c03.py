from ledgerline_reports.permissions import can_export
from ledgerline_shared.settings import Settings


def test_oracle_defaults_have_no_flags() -> None:
    assert Settings().flags == {}
    assert not can_export("viewer", Settings())
