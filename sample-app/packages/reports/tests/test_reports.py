from ledgerline_reports.models import Report
from ledgerline_reports.permissions import can_export, can_view
from ledgerline_reports.service import ReportService
from ledgerline_shared.settings import Settings


def make_service() -> ReportService:
    return ReportService([Report(id="r1", title="Q1", owner="ana")])


def test_get_report() -> None:
    assert make_service().get_report("r1").title == "Q1"


def test_admin_can_export() -> None:
    assert can_export("admin", Settings())


def test_unknown_role_cannot_view() -> None:
    assert not can_view("guest")
