"""Home-grown retry helper. Predates the tenacity dependency."""

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def with_retries(
    fn: Callable[[], T],
    attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (ConnectionError,),
    backoff: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Call fn, retrying on the given exceptions with linear backoff."""
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except exceptions:
            if attempt == attempts:
                raise
            sleep(backoff * attempt)
    raise AssertionError("unreachable")
