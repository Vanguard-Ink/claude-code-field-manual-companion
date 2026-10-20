import pytest

from ledgerline_billing.charge import charge
from ledgerline_billing.gateway import FakeGateway, GatewayDeclined, GatewayTimeout


def no_sleep(_: float) -> None:
    return None


def test_two_timeouts_then_success() -> None:
    gw = FakeGateway.scripted(["timeout", "timeout", "ok"])
    result = charge(gw, "cus_1", 900, idempotency_key="t1", sleep=no_sleep)
    assert result.charge_id == "ch_t1"
    assert gw.calls == 3


def test_gives_up_after_three_timeouts() -> None:
    gw = FakeGateway.scripted(["timeout", "timeout", "timeout", "ok"])
    with pytest.raises(GatewayTimeout):
        charge(gw, "cus_1", 900, idempotency_key="t2", sleep=no_sleep)
    assert gw.calls == 3


def test_decline_still_not_retried() -> None:
    gw = FakeGateway.scripted(["declined", "ok"])
    with pytest.raises(GatewayDeclined):
        charge(gw, "cus_1", 900, idempotency_key="t3", sleep=no_sleep)
    assert gw.calls == 1
