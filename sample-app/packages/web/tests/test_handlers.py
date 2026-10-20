from ledgerline_reports.models import Report
from ledgerline_reports.service import ReportService
from ledgerline_web.handlers import handle_get_report


def test_get_existing_report() -> None:
    svc = ReportService([Report(id="r1", title="Q1", owner="ana")])
    assert handle_get_report(svc, "r1").status == 200
