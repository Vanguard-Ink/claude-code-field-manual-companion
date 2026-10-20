"""Generic environment-variable configuration loader."""

import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


class ConfigError(ValueError):
    """A configuration value is invalid."""


@dataclass(frozen=True)
class EnvVar(Generic[T]):
    name: str
    parse: Callable[[str], T]
    validate: Callable[[T], bool] = lambda _: True

    def read(self, default: T) -> T:
        raw = os.environ.get(self.name)
        if raw is None:
            return default
        try:
            value = self.parse(raw)
        except (TypeError, ValueError) as e:
            raise ConfigError(f"{self.name}: {raw!r}") from e
        if not self.validate(value):
            raise ConfigError(f"{self.name}: {raw!r} failed validation")
        return value


def int_range(lo: int, hi: int) -> Callable[[int], bool]:
    return lambda v: lo <= v <= hi


def parse_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on"}
