# Retries in billing

Charges and refunds retry transient gateway errors: `ConnectionError`,
`GatewayTimeout`, and `GatewayBusy` (code BUSY). Declines are never retried:
a declined card stays declined, and retrying risks duplicate charges.

Settings: `retry_attempts` (total attempts), `retry_backoff_seconds` (first
wait), `retry_max_backoff_seconds` (cap on the exponential backoff).
