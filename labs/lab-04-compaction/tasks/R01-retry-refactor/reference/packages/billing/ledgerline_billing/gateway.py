"""A fake payment gateway. Tests script its responses."""

from collections.abc import Iterable
from dataclasses import dataclass, field


class GatewayTimeout(Exception):
    """The gateway did not answer in time. Safe to retry."""


class GatewayBusy(Exception):
    """The gateway is overloaded (code BUSY). Safe to retry."""


class GatewayDeclined(Exception):
    """The card was declined. Never retry."""


@dataclass
class FakeGateway:
    script: list[str] = field(default_factory=list)
    calls: int = 0

    @classmethod
    def scripted(cls, outcomes: Iterable[str]) -> "FakeGateway":
        return cls(script=list(outcomes))

    def submit(self, customer_id: str, amount_cents: int, key: str) -> str:
        self.calls += 1
        outcome = self.script.pop(0) if self.script else "ok"
        if outcome == "timeout":
            raise GatewayTimeout(f"timeout for {key}")
        if outcome == "busy":
            raise GatewayBusy(f"busy for {key}")
        if outcome == "declined":
            raise GatewayDeclined(f"declined for {customer_id}")
        if outcome == "conn":
            raise ConnectionError("connection reset")
        return f"ch_{key}"

    def refund(self, charge_id: str, amount_cents: int, key: str) -> str:
        self.calls += 1
        outcome = self.script.pop(0) if self.script else "ok"
        if outcome == "timeout":
            raise GatewayTimeout(f"timeout for {key}")
        if outcome == "busy":
            raise GatewayBusy(f"busy for {key}")
        if outcome == "conn":
            raise ConnectionError("connection reset")
        return f"rf_{key}"
