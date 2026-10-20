# L2 — Explain a cross-package call path

How does `charge()` decide how many times to retry a failed gateway call?
Trace it from `charge()` to wherever the number is defined, across packages.
Don't change any code.
