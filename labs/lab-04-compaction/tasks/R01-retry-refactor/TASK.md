# R01 — Billing retry refactor (six steps)

Work through the steps in order. After each step, run `make test lint typecheck`.

1. In `ledgerline_billing/charge.py`, replace `with_retries` with tenacity.
   Retry `ConnectionError` and `GatewayTimeout`; attempts come from settings.
2. Read `logs/gateway-2026-03.log`. Besides timeouts, the gateway now returns
   one more transient error code. Add an exception for it in `gateway.py`
   (code `XYZ` → class `GatewayXyz`), make `FakeGateway` raise it for the
   scripted outcome of the same name in lower case, and retry it in `charge()`.
3. Delete `ledgerline_billing/retry_helper.py`. Nothing may use it any more.
4. Make the backoff configurable: add `retry_max_backoff_seconds` (default 5.0)
   to `Settings`, use exponential backoff between `retry_backoff_seconds` and
   that maximum, and remove literal backoff numbers from `charge.py`.
5. Add `refund()` in `ledgerline_billing/refunds.py`:
   `refund(gateway, charge_id, amount_cents, *, idempotency_key, sleep=...)`
   returning the gateway's refund id. Refunds need exactly the same retry
   policy as charges.
6. Write `packages/billing/docs/retries.md`: which errors are retried, the
   settings that control it, and why declines are never retried.

Definition of done: `tasks/R01-retry-refactor/DONE.md`.
