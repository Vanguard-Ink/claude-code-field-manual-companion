"""A replaceable clock so time-dependent code can be tested."""

from collections.abc import Callable
from datetime import UTC, datetime

_now: Callable[[], datetime] = lambda: datetime.now(UTC)  # noqa: E731


def now() -> datetime:
    return _now()


def set_clock(fn: Callable[[], datetime]) -> None:
    global _now
    _now = fn
