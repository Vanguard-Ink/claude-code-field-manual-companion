# T02 — Retry gateway timeouts

Gateway timeouts during `charge()` are not retried, so one slow response fails the charge. Make timeouts retryable (up to the configured attempts); declines must never be retried.

Definition of done: `tasks/T02-retry-timeout/DONE.md`. Run the checks it lists and show their output before you say the task is done.
