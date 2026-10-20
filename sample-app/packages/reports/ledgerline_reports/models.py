"""Report data types."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Report:
    id: str
    title: str
    owner: str
    columns: list[str] = field(default_factory=list)
    rows: list[dict[str, str]] = field(default_factory=list)
