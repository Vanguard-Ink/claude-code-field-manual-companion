# T04 — Nightly job in the customer's time zone

The nightly invoice job should run at 02:00 in each customer's local time zone. `next_run_at(customer_tz, now)` currently ignores the time zone. Fix it; the result stays a UTC datetime.

Definition of done: `tasks/T04-invoice-timezone/DONE.md`. Run the checks it lists and show their output before you say the task is done.
