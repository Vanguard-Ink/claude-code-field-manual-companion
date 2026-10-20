import pytest

from ledgerline_shared.settings import load_settings


def test_defaults_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LEDGERLINE_RETRY_ATTEMPTS", raising=False)
    monkeypatch.delenv("LEDGERLINE_DEFAULT_TIMEZONE", raising=False)
    s = load_settings()
    assert s.retry_attempts == 3
    assert s.default_timezone == "UTC"


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LEDGERLINE_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("LEDGERLINE_DEFAULT_TIMEZONE", "Europe/Paris")
    s = load_settings()
    assert s.retry_attempts == 5
    assert s.default_timezone == "Europe/Paris"


def test_bad_retry_count_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LEDGERLINE_RETRY_ATTEMPTS", "three")
    with pytest.raises(ValueError):
        load_settings()
