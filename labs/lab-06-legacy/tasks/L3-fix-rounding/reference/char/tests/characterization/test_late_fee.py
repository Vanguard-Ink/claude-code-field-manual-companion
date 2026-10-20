import json
import pathlib
from decimal import Decimal

from ledgerline_billing.fees import compute_late_fee

HERE = pathlib.Path(__file__).parent
CASES = json.loads(
    (HERE / "late_fee_cases.json").read_text()
)


def test_late_fee_matches_recorded_behavior() -> None:
    for case in CASES:
        got = compute_late_fee(
            Decimal(case["amount"]), case["days"]
        )
        assert got == Decimal(case["recorded"]), case
