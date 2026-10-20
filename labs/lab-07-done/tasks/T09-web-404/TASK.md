# T09 — 404 for a missing report

Requesting a report that doesn't exist crashes the handler with a KeyError. `handle_get_report` should return status 404 with body `report not found` instead.

Definition of done: `tasks/T09-web-404/DONE.md`. Run the checks it lists and show their output before you say the task is done.
