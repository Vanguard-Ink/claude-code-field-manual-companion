import csv
import io

from ledgerline_reports.export import to_csv
from ledgerline_reports.models import Report


def test_oracle_formula_cells_are_neutralized() -> None:
    r = Report(
        id="r",
        title="t",
        owner="a",
        columns=["name"],
        rows=[{"name": '=HYPERLINK("http://x")'}, {"name": "+1"}],
    )
    rows = list(csv.reader(io.StringIO(to_csv(r))))
    assert rows[1][0].startswith("'=")
    assert rows[2][0] == "'+1"
