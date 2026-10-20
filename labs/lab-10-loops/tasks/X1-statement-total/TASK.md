# X1 — Statement total in cents

Monthly statements need a total. Add
`statement_total(amounts: list[Decimal]) -> int` in
`ledgerline_billing/statements.py`: the sum of the amounts,
rounded to whole cents (half to even), returned as integer
cents. An empty list totals 0.

Definition of done: `tasks/X1-statement-total/DONE.md`. Run the checks it lists and show their output before you say the task is done.
