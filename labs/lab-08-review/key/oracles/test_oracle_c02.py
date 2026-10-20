from ledgerline_reports.models import Report
from ledgerline_reports.service import ReportService


def test_oracle_partial_last_page() -> None:
    svc = ReportService([Report(id=f"r{i}", title="t", owner="a") for i in range(5)])
    assert svc.page_count(2) == 3
