from ledgerline_reports.models import Report
from ledgerline_reports.service import ReportService
from ledgerline_web.handlers import handle_get_report


def test_missing_report_is_404() -> None:
    resp = handle_get_report(ReportService(), "nope")
    assert resp.status == 404
    assert resp.body == "report not found"


def test_existing_report_still_200() -> None:
    svc = ReportService([Report(id="r1", title="Q1", owner="ana")])
    assert handle_get_report(svc, "r1").status == 200
