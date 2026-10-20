"""Runtime settings with sensible defaults."""

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
    """Return the settings for this process."""
    raw = os.environ.get("LEDGERLINE_NIGHTLY_RUN_HOUR")
    if raw is None:
        return Settings()
    hour = int(raw)
    if not 0 <= hour <= 23:
        raise ValueError(f"LEDGERLINE_NIGHTLY_RUN_HOUR out of range: {hour}")
    return Settings(nightly_run_hour=hour)
