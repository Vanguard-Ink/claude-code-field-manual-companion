from ledgerline_reports.models import Report
from ledgerline_reports.service import ReportService


def svc() -> ReportService:
    return ReportService([Report(id=f"r{i}", title=str(i), owner="ana")
                          for i in range(1, 6)])


def ids(page: list[Report]) -> list[str]:
    return [r.id for r in page]


def test_pages_cover_every_report_once() -> None:
    s = svc()
    assert ids(s.list_reports(1, 2)) == ["r1", "r2"]
    assert ids(s.list_reports(2, 2)) == ["r3", "r4"]
    assert ids(s.list_reports(3, 2)) == ["r5"]
    assert s.list_reports(4, 2) == []
