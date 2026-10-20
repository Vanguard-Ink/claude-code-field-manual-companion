import pytest

from ledgerline_shared.settings import load_settings


def test_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LEDGERLINE_NIGHTLY_RUN_HOUR", raising=False)
    assert load_settings().nightly_run_hour == 2


def test_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LEDGERLINE_NIGHTLY_RUN_HOUR", "5")
    assert load_settings().nightly_run_hour == 5


@pytest.mark.parametrize("bad", ["24", "-1", "two", ""])
def test_invalid(monkeypatch: pytest.MonkeyPatch, bad: str) -> None:
    monkeypatch.setenv("LEDGERLINE_NIGHTLY_RUN_HOUR", bad)
    with pytest.raises(ValueError):
        load_settings()
