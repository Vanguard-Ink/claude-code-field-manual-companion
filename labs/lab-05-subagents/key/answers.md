# LAB-05 answer key — keep out of sessions

Score each answer 0–3: correct location (1), complete — all decision points (1),
checkable — gives path:line or function names (1).

1. `packages/reports/ledgerline_reports/permissions.py` `can_export` (viewer
   branch); flag `viewer_export` via `flags.is_enabled` (flags.py). Note the
   `or True` bug: viewers can always export.
2. `charge.py` calls `retry_helper.with_retries` with its default
   `exceptions=(ConnectionError,)` in `retry_helper.py`; `GatewayTimeout` is NOT
   retried.
3. `Settings.nightly_run_hour` in `packages/shared/ledgerline_shared/settings.py`;
   used in `invoices.next_run_at`.
4. `packages/billing/ledgerline_billing/fees.py` `compute_late_fee`
   (`if fee < 0.5`).
5. `web/handlers.handle_get_report` → `ReportService.get_report` → dict lookup
   raises `KeyError`, which is not caught: the handler crashes (no 404).
