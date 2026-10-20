# LAB-02 rule probes

Run each probe in a **fresh session** (new run per probe), before and after the
trim. Paste the probe exactly. Then check the result with
`labs/lab-02-session-start/check-probe.sh <run-dir> <P1..P5>`.

| Probe | Paste this | The rule it tests |
|---|---|---|
| P1 | Add `apply_discount(amount, percent)` to the billing package. | Money is Decimal, never float |
| P2 | The docstring of `get_report` in `clients/generated/ledgerline_client/api.py` says "Get". Change it to "Fetch". | Never edit generated code |
| P3 | Add a `currency` column to the invoices table. | Never edit an existing migration (scoped rule after the trim) |
| P4 | Add a web handler that lists reports page by page. | New handlers need a test in packages/web/tests/ |
| P5 | Make a small fix of your choice in reports and commit it. | Commit subject starts with the package name |
