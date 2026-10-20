# X2 — Refunds survive a connection reset

Add `refund(gateway, charge_id, amount_cents, *,
idempotency_key, sleep=time.sleep) -> str` in
`ledgerline_billing/refunds.py`. It calls
`gateway.refund(...)` and returns the refund id. A
`ConnectionError` is retried, up to 3 attempts in total;
`GatewayTimeout` and anything else is not retried.

Definition of done: `tasks/X2-refund-retry/DONE.md`. Run the checks it lists and show their output before you say the task is done.
