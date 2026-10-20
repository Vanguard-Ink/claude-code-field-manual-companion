# X3 — Nightly hour from the environment

Operators want to move the nightly invoice job without a
deploy. `load_settings()` should read
`LEDGERLINE_NIGHTLY_RUN_HOUR` (an integer 0–23) and use it
for `nightly_run_hour`, falling back to the default. A value
that isn't an integer in 0–23 raises `ValueError`.

Definition of done: `tasks/X3-nightly-hour-env/DONE.md`. Run the checks it lists and show their output before you say the task is done.
