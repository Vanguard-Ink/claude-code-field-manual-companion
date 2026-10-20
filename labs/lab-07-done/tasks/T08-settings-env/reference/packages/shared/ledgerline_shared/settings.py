"""Runtime settings with sensible defaults, overridable from the environment."""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    retry_attempts: int = 3
    retry_backoff_seconds: float = 0.5
    default_timezone: str = "UTC"
    nightly_run_hour: int = 2
    flags: dict[str, bool] = field(default_factory=dict)


def load_settings() -> Settings:
    """Return the settings for this process.

    LEDGERLINE_RETRY_ATTEMPTS and LEDGERLINE_DEFAULT_TIMEZONE override defaults.
    """
    defaults = Settings()
    raw_attempts = os.environ.get("LEDGERLINE_RETRY_ATTEMPTS")
    attempts = defaults.retry_attempts if raw_attempts is None else int(raw_attempts)
    tz = os.environ.get("LEDGERLINE_DEFAULT_TIMEZONE", defaults.default_timezone)
    return Settings(retry_attempts=attempts, default_timezone=tz)
