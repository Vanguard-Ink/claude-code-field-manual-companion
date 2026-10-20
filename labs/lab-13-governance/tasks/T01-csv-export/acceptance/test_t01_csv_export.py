import csv
import io

from ledgerline_reports.export import to_csv
from ledgerline_reports.models import Report


def parse(text: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(text)))


def test_header_then_rows_in_column_order() -> None:
    r = Report(id="r1", title="Q1", owner="ana", columns=["name", "total"],
               rows=[{"total": "10", "name": "Acme"}])
    assert parse(to_csv(r)) == [["name", "total"], ["Acme", "10"]]


def test_commas_quotes_and_newlines_survive() -> None:
    tricky = 'Smith, "Jr."\nLLC'
    r = Report(id="r2", title="T", owner="ana", columns=["name"],
               rows=[{"name": tricky}])
    assert parse(to_csv(r)) == [["name"], [tricky]]


def test_missing_value_is_empty() -> None:
    r = Report(id="r3", title="T", owner="ana", columns=["a", "b"],
               rows=[{"a": "1"}])
    assert parse(to_csv(r)) == [["a", "b"], ["1", ""]]


def test_empty_report_is_header_only() -> None:
    r = Report(id="r4", title="T", owner="ana", columns=["a"])
    assert parse(to_csv(r)) == [["a"]]
