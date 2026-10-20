"""Framework-free handlers. Each returns a Response."""

from dataclasses import dataclass

from ledgerline_reports.service import ReportService


@dataclass(frozen=True)
class Response:
    status: int
    body: str


def handle_get_report(service: ReportService, report_id: str) -> Response:
    report = service.get_report(report_id)
    return Response(status=200, body=report.title)
