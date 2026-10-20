"""Runtime settings with sensible defaults."""

from dataclasses import dataclass, field

from ledgerline_shared.env import EnvVar, int_range

NIGHTLY_RUN_HOUR = EnvVar("LEDGERLINE_NIGHTLY_RUN_HOUR", int, int_range(0, 23))


@dataclass(frozen=True)
class Settings:
    retry_attempts: int = 3
    retry_backoff_seconds: float = 0.5
    default_timezone: str = "UTC"
    nightly_run_hour: int = 2
    flags: dict[str, bool] = field(default_factory=dict)


def load_settings() -> Settings:
    """Return the settings for this process."""
    return Settings(nightly_run_hour=NIGHTLY_RUN_HOUR.read(2))
