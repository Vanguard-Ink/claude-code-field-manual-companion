import pytest

from ledgerline_billing.gateway import FakeGateway, GatewayTimeout
from ledgerline_billing.refunds import refund


def nosleep(_: float) -> None:
    return None


def test_retries_connection_errors() -> None:
    gw = FakeGateway.scripted(["conn", "conn", "ok"])
    assert refund(gw, "ch_1", 500, idempotency_key="k1", sleep=nosleep) == "rf_k1"
    assert gw.calls == 3


def test_gives_up_after_three_attempts() -> None:
    gw = FakeGateway.scripted(["conn", "conn", "conn", "ok"])
    with pytest.raises(ConnectionError):
        refund(gw, "ch_1", 500, idempotency_key="k2", sleep=nosleep)
    assert gw.calls == 3


def test_timeout_is_not_retried() -> None:
    gw = FakeGateway.scripted(["timeout", "ok"])
    with pytest.raises(GatewayTimeout):
        refund(gw, "ch_1", 500, idempotency_key="k3", sleep=nosleep)
    assert gw.calls == 1
