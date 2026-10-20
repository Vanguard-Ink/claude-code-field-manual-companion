from ledgerline_reports.permissions import can_delete


def test_oracle_analyst_cannot_delete() -> None:
    assert not can_delete("analyst")
