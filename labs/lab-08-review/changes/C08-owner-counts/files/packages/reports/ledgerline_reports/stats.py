"""Simple statistics over stored reports."""

from collections import Counter

from ledgerline_reports.service import ReportService


def counts_by_owner(service: ReportService) -> dict[str, int]:
    """Return owner -> report count, owners in alphabetical order."""
    everything = service.list_reports(1, service.count() + 2)
    counts = Counter(r.owner for r in everything)
    return dict(sorted(counts.items()))
