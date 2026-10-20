import csv
import io

from ledgerline_reports.export import to_csv
from ledgerline_reports.models import Report


def test_header_and_rows() -> None:
    r = Report(id="r", title="t", owner="a", columns=["name", "total"],
               rows=[{"name": "Acme, Inc.", "total": "10"}])
    rows = list(csv.reader(io.StringIO(to_csv(r))))
    assert rows == [["name", "total"], ["Acme, Inc.", "10"]]
