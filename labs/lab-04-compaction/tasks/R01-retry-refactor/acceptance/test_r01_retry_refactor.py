"""LAB-04 acceptance: one test per step of R01."""

import importlib
import importlib.util
from pathlib import Path

import pytest

from ledgerline_billing import gateway as gw_mod
from ledgerline_billing.charge import charge
from ledgerline_shared.settings import Settings

BILLING = Path(gw_mod.__file__).resolve().parent


def no_sleep(_: float) -> None:
    return None


def test_step1_timeouts_retried_with_tenacity() -> None:
    gw = gw_mod.FakeGateway.scripted(["timeout", "ok"])
    charge(gw, "cus", 100, idempotency_key="s1", sleep=no_sleep)
    assert gw.calls == 2
    assert "tenacity" in (BILLING / "charge.py").read_text()


def test_step2_new_transient_error_retried() -> None:
    exc = getattr(gw_mod, "GatewayBusy", None)
    assert exc is not None, "expected GatewayBusy (code BUSY in the log)"
    gw = gw_mod.FakeGateway.scripted(["busy"])
    with pytest.raises(exc):
        gw.submit("cus", 100, "k")
    gw = gw_mod.FakeGateway.scripted(["busy", "busy", "ok"])
    charge(gw, "cus", 100, idempotency_key="s2", sleep=no_sleep)
    assert gw.calls == 3


def test_step3_retry_helper_removed() -> None:
    assert importlib.util.find_spec("ledgerline_billing.retry_helper") is None


def test_step4_backoff_configurable() -> None:
    assert Settings().retry_max_backoff_seconds == 5.0
    source = (BILLING / "charge.py").read_text()
    assert "0.5" not in source and "5.0" not in source


def test_step5_refund_uses_same_policy() -> None:
    refunds = importlib.import_module("ledgerline_billing.refunds")
    gw = gw_mod.FakeGateway.scripted(["timeout", "busy", "ok"])
    rid = refunds.refund(gw, "ch_1", 100, idempotency_key="r5", sleep=no_sleep)
    assert rid == "rf_r5"
    assert gw.calls == 3


def test_step6_docs_written() -> None:
    doc = BILLING.parent / "docs" / "retries.md"
    text = doc.read_text()
    for word in ("GatewayBusy", "retry_attempts", "retry_max_backoff_seconds"):
        assert word in text
