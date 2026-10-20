from ledgerline_reports.models import Report
from ledgerline_reports.service import ReportService
from ledgerline_reports.stats import counts_by_owner


def test_oracle_many_reports() -> None:
    svc = ReportService(
        [Report(id=f"r{i:02d}", title="t", owner="a") for i in range(12)]
    )
    assert counts_by_owner(svc) == {"a": 12}
