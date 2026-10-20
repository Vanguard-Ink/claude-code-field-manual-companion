# T08 — Settings from environment variables

Operators need to override settings without code changes. `load_settings()` should read `LEDGERLINE_RETRY_ATTEMPTS` (integer) and `LEDGERLINE_DEFAULT_TIMEZONE` from the environment, falling back to the defaults. A non-integer retry count is an error.

Definition of done: `tasks/T08-settings-env/DONE.md`. Run the checks it lists and show their output before you say the task is done.
