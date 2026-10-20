# X4 — Volume discount

Invoices over 10,000.00 get a 2% volume discount. Add
`apply_volume_discount(amount: Decimal) -> Decimal` in
`ledgerline_billing/discounts.py`, returning the amount to
bill, rounded to cents (half to even). The acceptance tests
were written by sales and finance together.

Definition of done: `tasks/X4-volume-discount/DONE.md`. Run the checks it lists and show their output before you say the task is done.
