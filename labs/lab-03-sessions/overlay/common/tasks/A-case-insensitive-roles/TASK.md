# Task A — small bug fix

Support reports that "Admin" (capital A) can't view reports: role names coming
from the login system are not lower-case. Make `can_view` and `can_export`
accept role names in any case. Done when
`python3 -m pytest tests/acceptance/test_a_roles.py` and `make test lint typecheck` pass.
