"""In-memory report store and queries."""

from ledgerline_reports.models import Report


class ReportService:
    """In-memory store of reports, keyed by id."""

    def __init__(self, reports: list[Report] | None = None) -> None:
        self._reports: dict[str, Report] = {r.id: r for r in reports or []}

    def add(self, report: Report) -> None:
        """Insert or replace a report."""
        self._reports[report.id] = report

    def get_report(self, report_id: str) -> Report:
        """Return a report; raises KeyError if it does not exist."""
        return self._reports[report_id]

    def list_reports(self, page: int, per_page: int) -> list[Report]:
        """Return one page of reports ordered by id. Pages start at 1."""
        if page < 1 or per_page < 1:
            raise ValueError("page and per_page start at 1")
        ordered = sorted(self._reports.values(), key=lambda r: r.id)
        start = (page - 1) * per_page
        return ordered[start : start + per_page - 1]

    def count(self) -> int:
        """Number of stored reports."""
        return len(self._reports)
