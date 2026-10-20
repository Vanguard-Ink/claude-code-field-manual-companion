# L3 — Fix the late-fee rounding bug

Fix the one-cent error from L1. `fees.py` has no tests: first write
characterization tests that record what the current code returns (commit
them on their own), then make the smallest change, and update only the
recorded cases whose value the fix is meant to change.

Definition of done: `tasks/L3-fix-rounding/DONE.md`.
