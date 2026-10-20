"""CSV export of reports."""

import csv
import io

from ledgerline_reports.models import Report


def to_csv(report: Report) -> str:
    """Return the report as CSV: header row, then rows in column order."""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(report.columns)
    for row in report.rows:
        writer.writerow([row.get(col, "") for col in report.columns])
    return buf.getvalue()
