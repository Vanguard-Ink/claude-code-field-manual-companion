# Blocked: X4 volume discount

The acceptance tests contradict each other at exactly 10,000.00:

- test_sales_discount_starts_at_threshold expects 9800.00
- test_finance_threshold_is_exclusive expects 10000.00

No implementation can pass both. I implemented "over 10,000" as the
task says (finance's reading); the sales test fails. Need: a decision
from sales and finance on the boundary, then one of the tests changed.
