"""Feature flags, read from settings."""

from ledgerline_shared.settings import Settings


def is_enabled(settings: Settings, name: str) -> bool:
    return settings.flags.get(name, False)
