from ledgerline_reports.models import Report
from ledgerline_reports.service import ReportService


def test_oracle_behavior_unchanged() -> None:
    svc = ReportService([Report(id="r1", title="t", owner="a")])
    assert svc.get_report("r1").title == "t"
    assert svc.count() == 1
