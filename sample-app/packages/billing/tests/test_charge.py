import pytest

from ledgerline_billing.charge import charge
from ledgerline_billing.gateway import FakeGateway, GatewayDeclined


def no_sleep(_: float) -> None:
    return None


def test_charge_succeeds() -> None:
    gw = FakeGateway.scripted(["ok"])
    result = charge(gw, "cus_1", 500, idempotency_key="k1", sleep=no_sleep)
    assert result.charge_id == "ch_k1"
    assert gw.calls == 1


def test_connection_reset_is_retried() -> None:
    gw = FakeGateway.scripted(["conn", "ok"])
    charge(gw, "cus_1", 500, idempotency_key="k2", sleep=no_sleep)
    assert gw.calls == 2


def test_declined_is_not_retried() -> None:
    gw = FakeGateway.scripted(["declined"])
    with pytest.raises(GatewayDeclined):
        charge(gw, "cus_1", 500, idempotency_key="k3", sleep=no_sleep)
    assert gw.calls == 1


def test_rejects_non_positive_amount() -> None:
    with pytest.raises(ValueError):
        charge(FakeGateway(), "cus_1", 0, idempotency_key="k4", sleep=no_sleep)
