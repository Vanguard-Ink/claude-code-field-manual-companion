# Testing rules

- Every change needs a test.
- Tests must not sleep; inject a sleep function.
- Tests must not touch the network.
- Use pytest fixtures for shared setup.
- Keep each test under 50 lines.
