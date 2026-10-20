from ledgerline_reports.models import Report
from ledgerline_reports.service import ReportService
from ledgerline_reports.stats import counts_by_owner


def test_counts_sorted_by_owner() -> None:
    svc = ReportService([
        Report(id="r1", title="t", owner="zoe"),
        Report(id="r2", title="t", owner="ana"),
        Report(id="r3", title="t", owner="zoe"),
    ])
    assert counts_by_owner(svc) == {"ana": 1, "zoe": 2}
    assert list(counts_by_owner(svc)) == ["ana", "zoe"]


def test_empty() -> None:
    assert counts_by_owner(ReportService()) == {}
