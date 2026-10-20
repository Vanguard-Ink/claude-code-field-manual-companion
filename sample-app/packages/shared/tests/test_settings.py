from ledgerline_shared.settings import load_settings


def test_defaults() -> None:
    s = load_settings()
    assert s.retry_attempts == 3
    assert s.default_timezone == "UTC"
