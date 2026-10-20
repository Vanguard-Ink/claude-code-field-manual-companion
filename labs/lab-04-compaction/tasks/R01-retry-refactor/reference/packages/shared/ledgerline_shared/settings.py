"""Runtime settings with sensible defaults."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    retry_attempts: int = 3
    retry_backoff_seconds: float = 0.5
    retry_max_backoff_seconds: float = 5.0
    default_timezone: str = "UTC"
    nightly_run_hour: int = 2
    flags: dict[str, bool] = field(default_factory=dict)


def load_settings() -> Settings:
    """Return the settings for this process."""
    return Settings()
