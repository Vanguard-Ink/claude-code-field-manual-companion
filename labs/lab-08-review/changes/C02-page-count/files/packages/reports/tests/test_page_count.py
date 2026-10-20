import pytest

from ledgerline_reports.models import Report
from ledgerline_reports.service import ReportService


def test_page_count_exact_multiple() -> None:
    svc = ReportService([Report(id=f"r{i}", title="t", owner="a") for i in range(4)])
    assert svc.page_count(2) == 2


def test_page_count_rejects_zero() -> None:
    with pytest.raises(ValueError):
        ReportService().page_count(0)
